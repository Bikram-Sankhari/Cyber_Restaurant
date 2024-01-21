# Generated by Django 5.0 on 2024-01-15 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_rename_address_line_1_userprofile_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='address',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='unknown.jpg', null=True, upload_to='users/profile_pictures'),
        ),
    ]