# Generated by Django 4.2.13 on 2024-07-04 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sign', '0003_alter_attendancerecord_check_in_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancerecord',
            name='working_hours',
            field=models.DurationField(blank=True, null=True, verbose_name='working_hours'),
        ),
    ]
