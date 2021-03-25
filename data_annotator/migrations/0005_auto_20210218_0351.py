# Generated by Django 3.1 on 2021-02-18 03:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_annotator', '0004_profile_active_proj'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shape',
            options={'verbose_name_plural': 'Shapes'},
        ),
        migrations.AddField(
            model_name='shape',
            name='date_captured',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='image',
            name='date_captured',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
