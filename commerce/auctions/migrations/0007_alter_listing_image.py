# Generated by Django 3.2.13 on 2022-05-10 15:58

import auctions.models
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20220509_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.ImageField(null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/media/my_sell/', location='/Users/b.vance/Documents/GitHub/cs50Ebay/commerce/media/my_sell/'), upload_to=auctions.models.image_directory_path),
        ),
    ]