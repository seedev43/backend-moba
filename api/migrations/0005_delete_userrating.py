# Generated by Django 4.2.17 on 2025-01-04 02:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_userrating_updated_at'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserRating',
        ),
    ]
