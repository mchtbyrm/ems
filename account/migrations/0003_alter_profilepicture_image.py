# Generated by Django 4.2.3 on 2023-08-01 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_remove_profile_image_profilepicture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilepicture',
            name='image',
            field=models.ImageField(blank=True, default='profile_pics/default.png', null=True, upload_to='profile_pics'),
        ),
    ]