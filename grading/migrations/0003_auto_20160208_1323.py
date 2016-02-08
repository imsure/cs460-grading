# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0002_grade_latedays'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='gradeNotes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grade',
            name='deduction',
            field=models.IntegerField(default=0),
        ),
    ]
