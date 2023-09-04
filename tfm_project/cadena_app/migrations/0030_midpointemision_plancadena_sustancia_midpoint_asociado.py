# Generated by Django 4.1 on 2023-09-04 21:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cadena_app", "0029_rename_nox_energia_fuenteenergia_nox_energia"),
    ]

    operations = [
        migrations.AddField(
            model_name="midpointemision_plancadena",
            name="sustancia_midpoint_asociado",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="cadena_app.sustancia_midpoint_emision",
            ),
        ),
    ]
