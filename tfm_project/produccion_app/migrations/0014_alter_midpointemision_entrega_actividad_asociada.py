# Generated by Django 4.1 on 2023-10-02 23:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("produccion_app", "0013_alter_enviocalculosendpoint_envio_asociada_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="midpointemision_entrega",
            name="actividad_asociada",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="produccion_app.actividad_envio",
            ),
        ),
    ]
