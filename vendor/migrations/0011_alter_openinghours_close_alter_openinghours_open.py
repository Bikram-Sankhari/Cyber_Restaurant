# Generated by Django 5.0 on 2024-01-31 19:38

import vendor.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0010_alter_openinghours_close_alter_openinghours_open'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openinghours',
            name='close',
            field=models.FloatField(blank=True, choices=vendor.models.get_time_choices, null=True),
        ),
        migrations.AlterField(
            model_name='openinghours',
            name='open',
            field=models.FloatField(blank=True, choices=vendor.models.get_time_choices, null=True),
        ),
    ]
