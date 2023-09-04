# Generated by Django 4.1 on 2023-08-23 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cadena_app", "0021_midpointemision_plancadena_suministroemision_asociado"),
    ]

    operations = [
        migrations.AddField(
            model_name="midpointemision_plancadena",
            name="tramos_PlanCadena",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="cadena_app.tramos_plancadena",
            ),
        ),
        migrations.AlterField(
            model_name="midpointemision_plancadena",
            name="tipo_midpoint",
            field=models.CharField(
                choices=[
                    ("TO", "Tierra Ocupacion"),
                    ("TX", "Tierra Relax"),
                    ("SU", "Suministro"),
                    ("TR", "Tramos"),
                    ("AC", "Actividades"),
                ],
                default="SU",
                max_length=2,
            ),
        ),
    ]
