# Generated by Django 3.0.4 on 2020-03-21 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20200321_0111'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=16, unique=True)),
                ('severity', models.IntegerField()),
                ('recommendation', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='customuser',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.Category'),
        ),
    ]
