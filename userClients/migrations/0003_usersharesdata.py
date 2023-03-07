# Generated by Django 4.1.7 on 2023-03-07 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userClients', '0002_delete_usersharesdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSharesData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=225)),
                ('company_symbol', models.CharField(max_length=50)),
                ('shares_qty', models.IntegerField()),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userClients.userclient')),
            ],
        ),
    ]
