from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from grading.models import Student, Assignment, Grade
from grading.forms import AssignmentForm, GradeForm

import csv
import datetime

path2roster_file = '/Users/shuoyang/codebase/cs460site/grading/static/roster_test.csv'
path2turnin_file = '/Users/shuoyang/codebase/cs460site/grading/static/cs460p1_turnin_test.txt'

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
                                     deduction=-1, score=-1)
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
    #return HttpResponse('test')
