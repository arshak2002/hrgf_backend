# Generated by Django 4.2.23 on 2025-07-24 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productimage',
            old_name='profile_picture',
            new_name='image',
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='cover_image/'),
        ),
    ]
