# Generated by Django 3.0.4 on 2020-03-21 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20200321_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='lat',
            field=models.DecimalField(blank=True, decimal_places=12, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='lon',
            field=models.DecimalField(blank=True, decimal_places=12, max_digits=15, null=True),
        ),
    ]
