# Generated by Django 3.1.5 on 2021-03-06 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pictures', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinfo',
            old_name='emile',
            new_name='email',
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='code',
            field=models.CharField(max_length=32, null=True),
        ),
    ]