# Generated by Django 3.1.6 on 2021-03-01 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('variants', '0004_auto_20210301_0235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='col',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='table',
            name='row',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='table',
            name='seats',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='end',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='start',
            field=models.TimeField(),
        ),
    ]
