# Generated by Django 3.2 on 2021-05-14 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frama_app', '0003_auto_20210430_0024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='contents',
        ),
        migrations.AddField(
            model_name='file',
            name='file_object',
            field=models.FileField(null=True, upload_to='user_files/'),
        ),
    ]
