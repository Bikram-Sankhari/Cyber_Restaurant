# Generated by Django 5.0 on 2024-01-28 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_alter_category_category_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='image',
            field=models.ImageField(blank=True, default='unknown.jpg', upload_to='food_images/'),
        ),
    ]
