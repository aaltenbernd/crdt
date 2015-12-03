# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crdt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operation',
            name='num',
            field=models.CharField(max_length=10),
        ),
    ]
