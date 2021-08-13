# Generated by Django 3.2.4 on 2021-08-11 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='name',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
