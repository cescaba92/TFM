# Generated by Django 4.1 on 2023-09-30 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("produccion_app", "0004_remove_actividad_orden_tipo_actividad_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="actividad_orden",
            name="estado_actividad",
            field=models.CharField(
                choices=[
                    ("PL", "Planificado"),
                    ("EN", "En ejecución"),
                    ("CO", "Completado"),
                ],
                default="PL",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="ordenproduccion",
            name="estado_produccion",
            field=models.CharField(
                choices=[
                    ("RE", "Registrado"),
                    ("PR", "En Producción"),
                    ("CO", "Completado"),
                    ("CA", "Cancelado"),
                ],
                default="RE",
                max_length=2,
            ),
        ),
    ]