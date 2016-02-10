# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grading', '0003_auto_20160208_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='emailSent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='grade',
            name='deduction',
            field=models.IntegerField(default=-1),
        ),
    ]
