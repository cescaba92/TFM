# Generated by Django 4.1 on 2023-07-31 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cadena_app", "0003_elementosemision"),
    ]

    operations = [
        migrations.AlterField(
            model_name="elementosemision",
            name="tipo_emision",
            field=models.CharField(
                choices=[
                    ("AT", "Atmósfera"),
                    ("TI", "Tierra"),
                    ("AD", "Agua Dulce"),
                    ("AS", "Océanos"),
                    ("RF", "Recursos Fosiles"),
                    ("AU", "Oceanos"),
                ],
                default="AT",
                max_length=2,
            ),
        ),
    ]
