# Generated by Django 4.1 on 2023-09-03 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cadena_app", "0023_midpointtramos"),
    ]

    operations = [
        migrations.RenameField(
            model_name="sustancia_emision",
            old_name="unidad_emision",
            new_name="categoria_emision",
        ),
        migrations.AddField(
            model_name="sustancia_emision",
            name="formula_emision",
            field=models.CharField(default="", max_length=264),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="sustancia_emision",
            name="valor_emision",
            field=models.FloatField(default="0"),
        ),
    ]
