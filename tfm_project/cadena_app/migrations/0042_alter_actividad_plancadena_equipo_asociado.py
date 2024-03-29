# Generated by Django 4.1 on 2023-10-07 19:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("suministro_app", "0006_suministro_unidad_suministro"),
        ("cadena_app", "0041_alter_midpointemision_plancadena_tipo_midpoint"),
    ]

    operations = [
        migrations.AlterField(
            model_name="actividad_plancadena",
            name="equipo_asociado",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="suministro_app.equipos",
            ),
        ),
    ]
