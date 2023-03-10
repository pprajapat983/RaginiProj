# Generated by Django 3.0.6 on 2020-06-03 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_contact'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('items_json', models.CharField(max_length=5000)),
                ('name', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=500)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('pin_code', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=50)),
            ],
        ),
    ]
