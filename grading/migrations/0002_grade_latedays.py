# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='latedays',
            field=models.IntegerField(default=-1),
        ),
    ]
