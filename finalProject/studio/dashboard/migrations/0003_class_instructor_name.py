# Generated by Django 5.0.6 on 2025-01-02 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_class_booking_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='instructor_name',
            field=models.CharField(default='', max_length=20),
        ),
    ]
