# Generated by Django 3.2.13 on 2022-05-11 22:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_watchitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='bid_date_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
