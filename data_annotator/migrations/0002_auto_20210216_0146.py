# Generated by Django 3.1 on 2021-02-16 01:46

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_annotator', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='samplesproject',
            name='annotators',
        ),
        migrations.RemoveField(
            model_name='samplesproject',
            name='contacts',
        ),
        migrations.RemoveField(
            model_name='samplesproject',
            name='manager',
        ),
        migrations.RemoveField(
            model_name='samplesproject',
            name='operators',
        ),
        migrations.AddField(
            model_name='samplesproject',
            name='users',
            field=models.ManyToManyField(related_name='works_as_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='samplesproject',
            name='Latitud_site',
            field=models.CharField(default='22.07', max_length=50),
        ),
        migrations.AlterField(
            model_name='samplesproject',
            name='Longitud_site',
            field=models.CharField(default='-79.49', max_length=50),
        ),
    ]
