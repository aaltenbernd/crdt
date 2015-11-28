# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crdt', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='number',
            old_name='num',
            new_name='number',
        ),
        migrations.AddField(
            model_name='number',
            name='title',
            field=models.CharField(default=b'', max_length=10),
        ),
    ]
