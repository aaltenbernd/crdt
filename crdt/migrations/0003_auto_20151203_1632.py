# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crdt', '0002_auto_20151203_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='open_ops',
            field=models.ManyToManyField(related_name='open_operation', to='crdt.Operation', blank=True),
        ),
    ]
