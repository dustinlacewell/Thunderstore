# Generated by Django 2.1.2 on 2019-06-16 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0015_auto_20190615_0526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='packageversion',
            name='name',
        ),
        migrations.RemoveField(
            model_name='packageversion',
            name='uuid4',
        ),
        migrations.AddField(
            model_name='package',
            name='slug',
            field=models.SlugField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='uploaderidentity',
            name='slug',
            field=models.SlugField(blank=True, max_length=128, unique=True),
        ),
        migrations.RemoveField(
            model_name='package',
            name='latest',
        ),
        migrations.AlterUniqueTogether(
            name='package',
            unique_together={('owner', 'slug')},
        ),
    ]