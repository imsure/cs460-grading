from django.forms import ModelForm, DateTimeInput

from grading.models import Assignment, Grade


class AssignmentForm(ModelForm):

    class Meta:
        model = Assignment
        fields = ('assigName', 'dueDate', 'total')

        widgets = {'dueDate':  DateTimeInput(format='%Y-%m-%d %H:%M')}

class GradeForm(ModelForm):

    class Meta:
        model = Grade
        fields = ('gradeNotes', 'deduction')
