# Generated by Django 3.0.4 on 2020-03-17 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_2', '0006_auto_20200315_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='message',
            field=models.CharField(default='Я здесь...', max_length=1000),
        ),
    ]