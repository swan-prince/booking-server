# Generated by Django 3.1.6 on 2021-02-26 01:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_auto_20210223_1355'),
        ('variants', '0002_productvariation_variation'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='variation',
            unique_together={('product', 'name')},
        ),
    ]
