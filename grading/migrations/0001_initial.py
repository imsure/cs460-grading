# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('assigName', models.CharField(primary_key=True, max_length=10, serialize=False)),
                ('dueDate', models.DateTimeField()),
                ('total', models.IntegerField()),
            ],
            options={
                'db_table': 'assignment',
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('submitDateTime', models.DateTimeField()),
                ('deduction', models.TextField()),
                ('score', models.IntegerField(default=-1)),
                ('assigName', models.ForeignKey(to='grading.Assignment')),
            ],
            options={
                'db_table': 'grade',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('netID', models.CharField(primary_key=True, max_length=100, serialize=False)),
                ('fname', models.CharField(max_length=100)),
                ('lname', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=1)),
                ('csID', models.IntegerField()),
            ],
            options={
                'db_table': 'student',
            },
        ),
        migrations.AddField(
            model_name='grade',
            name='netID',
            field=models.ForeignKey(to='grading.Student'),
        ),
        migrations.AlterUniqueTogether(
            name='grade',
            unique_together=set([('assigName', 'netID')]),
        ),
    ]
