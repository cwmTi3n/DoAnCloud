# Generated by Django 4.1.4 on 2022-12-12 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_giohang_diachi_alter_giohang_sanphams'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donhang',
            name='soluong',
            field=models.IntegerField(default=1),
        ),
    ]
