# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crdt', '0003_auto_20151203_1632'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutgoingOperation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operation', models.CharField(max_length=20)),
                ('num', models.CharField(max_length=10)),
            ],
        ),
        migrations.RenameModel(
            old_name='Operation',
            new_name='IncomingOperation',
        ),
        migrations.AlterField(
            model_name='node',
            name='open_ops',
            field=models.ManyToManyField(related_name='open_operation', to='crdt.OutgoingOperation', blank=True),
        ),
    ]
