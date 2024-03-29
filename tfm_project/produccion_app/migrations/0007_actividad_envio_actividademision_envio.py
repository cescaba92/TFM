# Generated by Django 4.1 on 2023-10-01 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cadena_app", "0041_alter_midpointemision_plancadena_tipo_midpoint"),
        ("suministro_app", "0006_suministro_unidad_suministro"),
        ("produccion_app", "0006_alter_ordenentrega_fecha_entrega"),
    ]

    operations = [
        migrations.CreateModel(
            name="Actividad_Envio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "estado_actividad",
                    models.CharField(
                        choices=[
                            ("PL", "Planificado"),
                            ("EN", "En ejecución"),
                            ("CO", "Completado"),
                        ],
                        default="PL",
                        max_length=2,
                    ),
                ),
                ("nom_actividad", models.CharField(max_length=264, null=True)),
                ("tiempo_equipo_asociado", models.FloatField()),
                (
                    "equipo_asociado",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="suministro_app.equipos",
                    ),
                ),
                (
                    "produccion_asociada",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="produccion_app.ordenentrega",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ActividadEmision_Envio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cantidad_sustancia", models.FloatField()),
                (
                    "actividadorden_asociado",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="produccion_app.actividad_envio",
                    ),
                ),
                (
                    "sustancia_asociada",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cadena_app.sustancia_emision",
                    ),
                ),
            ],
        ),
    ]
