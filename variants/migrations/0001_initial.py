# Generated by Django 3.1.6 on 2021-02-21 03:32

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('services', '0007_auto_20210220_1346'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.TimeField(default=datetime.time(9, 0))),
                ('end', models.TimeField(default=datetime.time(10, 0))),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeslots', to='services.seller')),
            ],
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.IntegerField(default=1)),
                ('col', models.IntegerField(default=1)),
                ('seats', models.IntegerField(default=4)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='services.seller')),
            ],
            options={
                'unique_together': {('row', 'col')},
            },
        ),
    ]
