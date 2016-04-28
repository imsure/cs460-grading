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
path2turnin_file = '/Users/shuoyang/codebase/cs460site/grading/static/{}_turnin.txt'

# Create your views here.

# home page
def index(request):
    assignments = Assignment.objects.all()
    context = {'assignments': assignments}
    return render(request, 'grading/index.html', context)

# initialize student table
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

def get_student_score_ldays(netID, assign_name):
    try:
        grade_entry = Grade.objects.get(netID=netID, assigName=assign_name)
        return (grade_entry.score, grade_entry.latedays)
    except ObjectDoesNotExist:
        return (-1, 0)

# show student table with the derived data:
# such as remaining late days, assigname score.
def show_students(request):
    students = Student.objects.all()
    ldays_remaining = []
    prog1_score = []
    prog1_ldays = []
    prog2_score = []
    prog2_ldays = []
    hw1_score = []
    hw1_ldays = []
    hw2_score = []
    hw2_ldays = []
    hw3_score = []
    hw3_ldays = []
    prog3_score = []
    prog3_ldays = []
    hw4_score = []
    hw4_ldays = []

    for s in students:
        (score_p1, ldays_p1) = get_student_score_ldays(s.netID, 'Prog1')
        prog1_score.append(score_p1)
        prog1_ldays.append(ldays_p1)
        (score_p2, ldays_p2) = get_student_score_ldays(s.netID, 'Prog2')
        prog2_score.append(score_p2)
        prog2_ldays.append(ldays_p2)
        (score_h1, ldays_h1) = get_student_score_ldays(s.netID, 'HW1')
        hw1_score.append(score_h1)
        hw1_ldays.append(ldays_h1)
        (score_h2, ldays_h2) = get_student_score_ldays(s.netID, 'HW2')
        hw2_score.append(score_h2)
        hw2_ldays.append(ldays_h2)
        (score_h3, ldays_h3) = get_student_score_ldays(s.netID, 'HW3')
        hw3_score.append(score_h3)
        hw3_ldays.append(ldays_h3)
        (score_p3, ldays_p3) = get_student_score_ldays(s.netID, 'Prog3')
        prog3_score.append(score_p3)
        prog3_ldays.append(ldays_p3)
        (score_h4, ldays_h4) = get_student_score_ldays(s.netID, 'HW4')
        hw4_score.append(score_h4)
        hw4_ldays.append(ldays_h4)



        # remaining_latedays = compute_remaining_ldays('Prog1', s.netID)
        # remaining_latedays = compute_remaining_ldays('Prog2', s.netID)
        # remaining_latedays = compute_remaining_ldays('HW1', s.netID)
        # remaining_latedays = compute_remaining_ldays('HW2', s.netID)
        # remaining_latedays = compute_remaining_ldays('HW3', s.netID)
        # remaining_latedays = compute_remaining_ldays('Prog3', s.netID)
        remaining_latedays = compute_remaining_ldays('HW4', s.netID)
        if remaining_latedays < 0:
            ldays_remaining.append(0)
        else:
            ldays_remaining.append(remaining_latedays)

    context = {
        'students': list(zip(students,
                             prog1_ldays, prog1_score,
                             prog2_ldays, prog2_score,
                             hw1_ldays, hw1_score,
                             hw2_ldays, hw2_score,
                             hw3_ldays, hw3_score,
                             prog3_ldays, prog3_score,
                             hw4_ldays, hw4_score,
                             ldays_remaining)),
    }
    return render(request, 'grading/show_students.html', context)
    #return HttpResponse('test')

# add an assignment to Assignment table
def add_assign(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('grading:index'))
    else:
        form = AssignmentForm()
    return render(request, 'grading/add_assign.html', {'form': form})

# don't do this! Dangerous!
def remove_assign(request, assign_name):
    assign = Assignment.objects.get(pk=assign_name)
    try:
        assign.delete()
        return HttpResponseRedirect(reverse('grading:index'))
    except IntegrityError as e:
        return HttpResponse(str(e))

# initialize grading table for an assignment
def init_grade_table(request, assign_name):
    month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4}

    counter = 0
    turnin = open(path2turnin_file.format(assign_name))
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

def compute_remaining_ldays(assign_name, netID):
    remaining_ldays = 0
    if assign_name == 'Prog1':
        try:
            prog1_entry = Grade.objects.get(assigName='Prog1', netID=netID)
            remaining_ldays = 5 - prog1_entry.latedays
        except ObjectDoesNotExist:
            remaining_ldays = 5

    if assign_name == 'Prog2':
        try:
            prog1_entry = Grade.objects.get(assigName='Prog1', netID=netID)
            remaining_ldays = 5 - prog1_entry.latedays
        except ObjectDoesNotExist:
            remaining_ldays = 5

        try:
            prog2_entry = Grade.objects.get(assigName='Prog2', netID=netID)
            remaining_ldays -= prog2_entry.latedays
        except ObjectDoesNotExist:
            pass

    if assign_name == 'HW1':
        try:
            prog1_entry = Grade.objects.get(assigName='Prog1', netID=netID)
            remaining_ldays = 5 - prog1_entry.latedays
        except ObjectDoesNotExist:
            remaining_ldays = 5

        try:
            prog2_entry = Grade.objects.get(assigName='Prog2', netID=netID)
            remaining_ldays -= prog2_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw1_entry = Grade.objects.get(assigName='HW1', netID=netID)
            remaining_ldays -= hw1_entry.latedays
        except ObjectDoesNotExist:
            pass

    if assign_name == 'HW2':
        try:
            prog1_entry = Grade.objects.get(assigName='Prog1', netID=netID)
            remaining_ldays = 5 - prog1_entry.latedays
        except ObjectDoesNotExist:
            remaining_ldays = 5

        try:
            prog2_entry = Grade.objects.get(assigName='Prog2', netID=netID)
            remaining_ldays -= prog2_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw1_entry = Grade.objects.get(assigName='HW1', netID=netID)
            remaining_ldays -= hw1_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw2_entry = Grade.objects.get(assigName='HW2', netID=netID)
            remaining_ldays -= hw2_entry.latedays
        except ObjectDoesNotExist:
            pass

    if assign_name == 'HW3':
        try:
            prog1_entry = Grade.objects.get(assigName='Prog1', netID=netID)
            remaining_ldays = 5 - prog1_entry.latedays
        except ObjectDoesNotExist:
            remaining_ldays = 5

        try:
            prog2_entry = Grade.objects.get(assigName='Prog2', netID=netID)
            remaining_ldays -= prog2_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw1_entry = Grade.objects.get(assigName='HW1', netID=netID)
            remaining_ldays -= hw1_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw2_entry = Grade.objects.get(assigName='HW2', netID=netID)
            remaining_ldays -= hw2_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw3_entry = Grade.objects.get(assigName='HW3', netID=netID)
            remaining_ldays -= hw3_entry.latedays
        except ObjectDoesNotExist:
            pass

    if assign_name == 'Prog3':
        try:
            prog1_entry = Grade.objects.get(assigName='Prog1', netID=netID)
            remaining_ldays = 5 - prog1_entry.latedays
        except ObjectDoesNotExist:
            remaining_ldays = 5

        try:
            prog2_entry = Grade.objects.get(assigName='Prog2', netID=netID)
            remaining_ldays -= prog2_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw1_entry = Grade.objects.get(assigName='HW1', netID=netID)
            remaining_ldays -= hw1_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw2_entry = Grade.objects.get(assigName='HW2', netID=netID)
            remaining_ldays -= hw2_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw3_entry = Grade.objects.get(assigName='HW3', netID=netID)
            remaining_ldays -= hw3_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            prog3_entry = Grade.objects.get(assigName='Prog3', netID=netID)
            remaining_ldays -= prog3_entry.latedays
        except ObjectDoesNotExist:
            pass

    if assign_name == 'HW4':
        try:
            prog1_entry = Grade.objects.get(assigName='Prog1', netID=netID)
            remaining_ldays = 5 - prog1_entry.latedays
        except ObjectDoesNotExist:
            remaining_ldays = 5

        try:
            prog2_entry = Grade.objects.get(assigName='Prog2', netID=netID)
            remaining_ldays -= prog2_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw1_entry = Grade.objects.get(assigName='HW1', netID=netID)
            remaining_ldays -= hw1_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw2_entry = Grade.objects.get(assigName='HW2', netID=netID)
            remaining_ldays -= hw2_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw3_entry = Grade.objects.get(assigName='HW3', netID=netID)
            remaining_ldays -= hw3_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            prog3_entry = Grade.objects.get(assigName='Prog3', netID=netID)
            remaining_ldays -= prog3_entry.latedays
        except ObjectDoesNotExist:
            pass

        try:
            hw4_entry = Grade.objects.get(assigName='HW4', netID=netID)
            remaining_ldays -= hw4_entry.latedays
        except ObjectDoesNotExist:
            pass


    return remaining_ldays

def compute_grades(request, assign_name):
    turnins = Grade.objects.filter(assigName=assign_name)
    assign = Assignment.objects.get(pk=assign_name)
    for i in range(0, len(turnins)):
        if turnins[i].deduction == -1:
            turnins[i].score = -1
            turnins[i].save()
            continue

        remaining_latedays = compute_remaining_ldays(assign_name, turnins[i].netID_id)
        if remaining_latedays >= 0 or turnins[i].latedays == 0: # no penalty
            turnins[i].score = assign.total - turnins[i].deduction
            turnins[i].save()
        else: # got late day penalty only when at least 1 late day is used and remaining late days is negative
            # number of late days with penalty should be the min of late days used
            # for the assignment and absolute value of remaining latedays.
            num_lateday_penalty = min(turnins[i].latedays, -remaining_latedays)
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
            remaining_latedays = compute_remaining_ldays(assign_name, turnins[i].netID_id)
            # remaining_latedays = 5 - turnins[i].latedays
            if remaining_latedays >= 0 or turnins[i].latedays == 0: # no penalty
                num_lateday_penalty = 0
            else:
                num_lateday_penalty = min(turnins[i].latedays, -remaining_latedays)
            # num_lateday_penalty = 0

            if remaining_latedays < 0:
                # num_lateday_penalty = -remaining_latedays
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

        remaining_latedays = compute_remaining_ldays(assign_name, turnin_entry.netID_id)
        # remaining_latedays = 5 - turnins[i].latedays
        if remaining_latedays >= 0 or turnin_entry.latedays == 0: # no penalty
            num_lateday_penalty = 0
        else:
            num_lateday_penalty = min(turnin_entry.latedays, -remaining_latedays)
            # num_lateday_penalty = 0

        if remaining_latedays < 0:
            # num_lateday_penalty = -remaining_latedays
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
