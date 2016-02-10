from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from grading.models import Student, Assignment, Grade
from grading.forms import AssignmentForm, GradeForm
from grading.config import email_password

import csv
import datetime
import smtplib
import sys
import math
import csv
from email.mime.text import MIMEText

path2roster_file = '/Users/shuoyang/codebase/cs460site/grading/static/roster.csv'
path2turnin_file = '/Users/shuoyang/codebase/cs460site/grading/static/cs460p1_turnin.txt'

# Create your views here.

def index(request):
    assignments = Assignment.objects.all()
    context = {'assignments': assignments}
    return render(request, 'grading/index.html', context)

def init_student(request):
    roster_file = open(path2roster_file)
    roster_csv = csv.reader(roster_file, delimiter=',')
    counter = 0
    for row in roster_csv:
        lname = row[0].strip()
        fmname = row[1].strip()
        fname = fmname.split()[0]
        netID = row[2].strip()
        status = row[3].strip()
        csID = row[4].strip()

        try:
            s = Student.objects.get(pk=netID)
        except ObjectDoesNotExist:
            s = Student.objects.create(netID=netID, fname=fname,
                                       lname=lname, status=status,
                                       csID=csID)
            counter = counter + 1

    return HttpResponse('{} students inserted into Student Table!'.format(counter))

def add_assign(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('grading:index'))
    else:
        form = AssignmentForm()
    return render(request, 'grading/add_assign.html', {'form': form})

def remove_assign(request, assign_name):
    assign = Assignment.objects.get(pk=assign_name)
    try:
        assign.delete()
        return HttpResponseRedirect(reverse('grading:index'))
    except IntegrityError as e:
        return HttpResponse(str(e))

def init_grade_table(request, assign_name):
    month_map = {'Jan': 1, 'Feb': 2}

    counter = 0
    turnin = open(path2turnin_file)
    for line in turnin.readlines():
        fields = line.split()
        year = 2016
        month = month_map[fields[5]]
        day = int(fields[6])
        hm = fields[7]
        hour = int(fields[7].split(':')[0])
        minute = int(fields[7].split(':')[1])
        netID = fields[8]

        try:
            s = Grade.objects.get(netID=netID, assigName=assign_name)
        except ObjectDoesNotExist:
            dt = datetime.datetime(year, month, day, hour, minute)
            s = Grade.objects.create(netID_id=netID, submitDateTime=dt,
                                     assigName_id=assign_name,
                                     deduction=-1, score=-1,
                                     emailSent=False)
            counter = counter + 1

    return HttpResponse('{} submission inserted into grade Table for {}.'.
                        format(counter, assign_name))

def show_grade(request, assign_name):
    turnins = Grade.objects.filter(assigName=assign_name)
    assign = Assignment.objects.get(pk=assign_name)

    num_ungraded = 0
    for i in range(0, len(turnins)):
        if turnins[i].latedays == -1: # update latedays
            turnin_dt = turnins[i].submitDateTime
            duration = turnin_dt - assign.dueDate
            latedays = duration.days

            if latedays >= 0:
                # assignment submitted within 30 minutes after the due time does
                # not count as late days.
                if duration.seconds > 1800:
                    latedays += 1
            else:
                latedays = 0 # eariler turnin counts as 0 lateday

            turnins[i].latedays = latedays
            turnins[i].save()

        if turnins[i].deduction == -1:
            num_ungraded += 1

    context = {
        'turnins': turnins,
        'assign': assign,
        'num_turnins': len(turnins),
        'num_ungraded': num_ungraded,
    }

    return render(request, 'grading/show_grade.html', context)

def grade(request, assign_name, netID):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        grade_entry = Grade.objects.get(netID=netID, assigName=assign_name)
        form.instance = grade_entry
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('grading:show_grade', args=(assign_name,)))
    else:
        form = GradeForm()
    return render(request, 'grading/grade.html', {'form': form})

def deduction_details(request, assign_name, netID):
    grade_entry = Grade.objects.get(netID=netID, assigName=assign_name)
    return HttpResponse(grade_entry.gradeNotes)

def compute_grades(request, assign_name):
    turnins = Grade.objects.filter(assigName=assign_name)
    assign = Assignment.objects.get(pk=assign_name)
    for i in range(0, len(turnins)):
        remaining_latedays = 5 - turnins[i].latedays
        if remaining_latedays >= 0:
            turnins[i].score = assign.total - turnins[i].deduction
            turnins[i].save()
        else:
            num_lateday_penalty = -remaining_latedays
            raw_score = assign.total - turnins[i].deduction
            turnins[i].score = math.ceil(raw_score * (1 - 0.2 * num_lateday_penalty))
            turnins[i].save()
            #HttpResponse('Negative remaining late days!')

    return HttpResponseRedirect(reverse('grading:show_grade', args=(assign_name,)))

def send_email_all(request, assign_name):
    sender = 'shuoyang@email.arizona.edu'
    conn = smtplib.SMTP('smtpgate.email.arizona.edu', 587)
    conn.ehlo()
    conn.starttls()
    conn.login(sender, email_password)

    turnins = Grade.objects.filter(assigName=assign_name)
    for i in range(0, len(turnins)):
        # this means this submission has been graded but email not sent yet
        if turnins[i].deduction >= 0 and turnins[i].emailSent == False:
        #if turnins[i].deduction >= 0:
            s = Student.objects.get(pk=turnins[i].netID_id)
            remaining_latedays = 5 - turnins[i].latedays
            num_lateday_penalty = 0
            if remaining_latedays < 0:
                num_lateday_penalty = -remaining_latedays
                remaining_latedays = 0

            email_body = '''
Hi {0},

Your final score is {1}. Please see details below.

---------------------------------------------------
Late days used for this assignment: {2}
Late days remaining: {3}

Deductions:
{4}

Raw score: {5}
Late day penalty: {6} * 20% = {7}

Final score: {8} * (1 - {9}) = {10}
---------------------------------------------------

Please let me know if you have any questions or concerns.

Shuo
            '''.format(s.fname, turnins[i].score, turnins[i].latedays,
                       remaining_latedays, turnins[i].gradeNotes,
                       100-turnins[i].deduction, num_lateday_penalty,
                       num_lateday_penalty * 0.2, 100-turnins[i].deduction,
                       num_lateday_penalty * 0.2, turnins[i].score)
            msg = MIMEText(email_body, 'plain')
            msg['Subject'] = 'CS460: {} Grade'.format(assign_name)
            msg['From'] = sender
            msg['To'] = turnins[i].netID_id + '@email.arizona.edu'
            msg['CC'] = sender # CC myself
            conn.send_message(msg)
            turnins[i].emailSent = True
            turnins[i].save()

    return HttpResponseRedirect(reverse('grading:show_grade', args=(assign_name,)))

def send_email(request, assign_name, netID):
    sender = 'shuoyang@email.arizona.edu'
    conn = smtplib.SMTP('smtpgate.email.arizona.edu', 587)
    conn.ehlo()
    conn.starttls()
    conn.login(sender, email_password)

    turnin_entry = Grade.objects.get(assigName=assign_name, netID=netID)
    if turnin_entry.deduction >= 0:
        s = Student.objects.get(pk=turnin_entry.netID_id)
        remaining_latedays = 5 - turnin_entry.latedays
        num_lateday_penalty = 0
        if remaining_latedays < 0:
            num_lateday_penalty = -remaining_latedays
            remaining_latedays = 0

        email_body = '''
Hi {0},

Your final score is {1}. Please see details below.

---------------------------------------------------
Late days used for this assignment: {2}
Late days remaining: {3}

Deductions:
{4}

Raw score: {5}
Late day penalty: {6} * 20% = {7}

Final score: {8} * (1 - {9}) = {10}
---------------------------------------------------

Please let me know if you have any questions or concerns.

Shuo
        '''.format(s.fname, turnin_entry.score, turnin_entry.latedays,
                   remaining_latedays, turnin_entry.gradeNotes,
                   100-turnin_entry.deduction, num_lateday_penalty,
                   num_lateday_penalty * 0.2, 100-turnin_entry.deduction,
                   num_lateday_penalty * 0.2, turnin_entry.score)
        msg = MIMEText(email_body, 'plain')
        msg['Subject'] = 'CS460: {} Grade'.format(assign_name)
        msg['From'] = sender
        msg['To'] = turnin_entry.netID_id + '@email.arizona.edu'
        msg['CC'] = sender # CC myself
        conn.send_message(msg)
        if turnin_entry.emailSent == False:
            turnin_entry.emailSent = True
            turnin_entry.save()

    return HttpResponseRedirect(reverse('grading:show_grade', args=(assign_name,)))

def output2csv(request, assign_name):
    grade_entries = Grade.objects.filter(assigName=assign_name)
    fields = Grade._meta.get_fields()
    header_row = [field.name for field in fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(assign_name)

    writer = csv.writer(response)
    writer.writerow(header_row)

    for entry in grade_entries:
        writer.writerow([getattr(entry, field.name) for field in fields])

    return response
