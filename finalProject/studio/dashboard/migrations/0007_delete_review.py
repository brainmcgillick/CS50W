# Generated by Django 5.0.6 on 2025-01-12 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_remove_user_instructor_name'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Review',
        ),
    ]
