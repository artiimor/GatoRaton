# Generated by Django 2.1.5 on 2019-11-09 10:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('datamodel', '0003_auto_20191109_1022'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='mouse_user',
        ),
        migrations.AddField(
            model_name='game',
            name='mouseUser',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gamemouseUsers', to=settings.AUTH_USER_MODEL),
        ),
    ]
