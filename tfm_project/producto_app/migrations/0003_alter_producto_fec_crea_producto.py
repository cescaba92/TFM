# Generated by Django 4.1 on 2023-05-09 16:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producto_app", "0002_producto_sku_producto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="producto",
            name="fec_crea_producto",
            field=models.DateField(default=datetime.date.today),
        ),
    ]
