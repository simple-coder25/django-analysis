# Generated by Django 2.2.5 on 2019-09-11 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formatting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='validationmodel',
            name='applied',
            field=models.BooleanField(default=False),
        ),
    ]