# Generated by Django 3.0.4 on 2020-03-23 11:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_2', '0008_auto_20200318_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='killer',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='killer', to=settings.AUTH_USER_MODEL, verbose_name='killer'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='target',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='target', to=settings.AUTH_USER_MODEL, verbose_name='target'),
        ),
    ]
