# Generated by Django 4.1 on 2023-08-20 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cadena_app", "0013_energia_transporte_tipo_transporte_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tramosexternos_plancadena",
            name="descripcion_tramoexterno",
            field=models.CharField(max_length=264, null=True),
        ),
    ]
