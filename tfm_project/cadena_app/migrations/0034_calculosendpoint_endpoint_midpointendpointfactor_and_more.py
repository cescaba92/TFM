# Generated by Django 4.1 on 2023-09-05 22:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "cadena_app",
            "0033_remove_midpointemision_plancadena_midpoints_emision_asociada_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="CalculosEndpoint",
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
                ("nom_calculo", models.CharField(max_length=264)),
            ],
        ),
        migrations.CreateModel(
            name="Endpoint",
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
                ("nom_endpoint", models.CharField(max_length=264)),
            ],
        ),
        migrations.CreateModel(
            name="MidpointEndpointFactor",
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
                ("unidad", models.CharField(max_length=264)),
                ("factor", models.FloatField()),
                (
                    "calculosEndpoint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cadena_app.calculosendpoint",
                    ),
                ),
                (
                    "midpoint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cadena_app.midpoint_emision",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="calculosendpoint",
            name="endpoint",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="cadena_app.endpoint"
            ),
        ),
    ]
