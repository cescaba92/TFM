# Generated by Django 4.1 on 2023-07-31 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cadena_app", "0007_rename_elementosemision_elemento_emision"),
    ]

    operations = [
        migrations.CreateModel(
            name="sustancia_emision",
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
                    "tipo_emision",
                    models.CharField(
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
                ("componente_emision", models.CharField(max_length=264)),
                ("unidad_emision", models.CharField(max_length=264)),
                ("valor_emision", models.FloatField(default="Kg")),
                (
                    "midpoint_emision",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cadena_app.midpoint_emision",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Elemento_Emision",
        ),
    ]