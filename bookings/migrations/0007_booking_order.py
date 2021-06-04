# Generated by Django 3.1.6 on 2021-03-08 00:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0006_auto_20210304_0514'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='order',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='bookings.order'),
            preserve_default=False,
        ),
    ]
