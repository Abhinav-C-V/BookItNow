# Generated by Django 5.1.2 on 2024-10-23 07:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hotel_name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('1', '1 Star'), ('2', '2 Star'), ('3', '3 Star'), ('4', '4 Star'), ('5', '5 Star')], default='3', max_length=10)),
                ('address', models.CharField(max_length=255)),
                ('base_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_number', models.CharField(max_length=10)),
                ('category', models.CharField(choices=[('SINGLE', 'Single Bed'), ('DOUBLE', 'Double Bed'), ('SUITE', 'Suite'), ('DELUXE', 'Deluxe'), ('KING', 'King Size Bed'), ('QUEEN', 'Queen Size Bed')], default='SINGLE', max_length=20)),
                ('ac_type', models.CharField(choices=[('AC', 'AC'), ('NON_AC', 'Non-AC')], default='AC', max_length=6)),
                ('is_available', models.BooleanField(default=True)),
                ('total_rooms', models.PositiveIntegerField(default=0)),
                ('available_rooms', models.PositiveIntegerField(default=0)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='home.hotel')),
            ],
        ),
    ]