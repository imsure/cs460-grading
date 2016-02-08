from django.db import models

# Create your models here.

class Student(models.Model):
    netID = models.CharField(primary_key=True, max_length=100)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    status = models.CharField(max_length=1)
    csID = models.IntegerField()

    class Meta:
        db_table = 'student'

class Assignment(models.Model):
    assigName = models.CharField(primary_key=True, max_length=10)
    dueDate = models.DateTimeField()
    total = models.IntegerField()

    class Meta:
        db_table = 'assignment'

class Grade(models.Model):
    submitDateTime = models.DateTimeField()
    netID = models.ForeignKey(Student)
    assigName = models.ForeignKey(Assignment)
    gradeNotes = models.TextField(blank=True, null=True)
    # -1 indicates late days has not been computed
    latedays = models.IntegerField(default=-1)
    # -1 indicates score has not avaiable
    score = models.IntegerField(default=-1)
    deduction = models.IntegerField(default=-1)

    class Meta:
        db_table = 'grade'
        # a student can only have one submission for one assignment
        unique_together = ('assigName', 'netID')
