# Generated by Django 3.1.6 on 2021-03-01 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_auto_20210301_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='booked_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
