# Generated by Django 2.1.2 on 2019-06-15 05:26

import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import repository.models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0003_auto_20190615_0526'),
        ('repository', '0014_update_meta'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackageCompatibility',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_version', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='max_version', to='targets.TargetVersion')),
                ('min_version', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='min_version', to='targets.TargetVersion')),
            ],
        ),
        migrations.AlterField(
            model_name='packageversion',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=repository.models.get_version_zip_filepath),
        ),
        migrations.AddField(
            model_name='packagecompatibility',
            name='package_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repository.PackageVersion'),
        ),
        migrations.AddField(
            model_name='packagecompatibility',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='targets.Target'),
        ),
    ]
