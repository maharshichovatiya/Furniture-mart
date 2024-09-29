# Generated by Django 5.1 on 2024-09-15 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='furniture',
            name='category',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='furniture',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='furniture_images/'),
        ),
    ]