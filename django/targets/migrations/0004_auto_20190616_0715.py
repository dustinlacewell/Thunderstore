# Generated by Django 2.1.2 on 2019-06-16 07:15

from django.db import migrations, models
import targets.models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0003_auto_20190615_0526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='target',
            name='icon',
            field=models.ImageField(upload_to=targets.models.get_version_png_filepath),
        ),
        migrations.AlterField(
            model_name='target',
            name='slug',
            field=models.SlugField(blank=True, max_length=128, unique=True),
        ),
    ]