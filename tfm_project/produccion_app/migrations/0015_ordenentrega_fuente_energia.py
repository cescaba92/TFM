# Generated by Django 4.1 on 2023-10-02 23:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cadena_app", "0041_alter_midpointemision_plancadena_tipo_midpoint"),
        ("produccion_app", "0014_alter_midpointemision_entrega_actividad_asociada"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordenentrega",
            name="fuente_energia",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="cadena_app.fuenteenergia",
            ),
        ),
    ]