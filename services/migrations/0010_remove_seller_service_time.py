# Generated by Django 3.1.6 on 2021-02-27 20:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_auto_20210223_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seller',
            name='service_time',
        ),
    ]
