from django.forms import ModelForm, DateTimeInput

from grading.models import Assignment


class AssignmentForm(ModelForm):

    class Meta:
        model = Assignment
        fields = ('assigName', 'dueDate', 'total')

        widgets = {'dueDate':  DateTimeInput(format='%Y-%m-%d %H:%M')}
