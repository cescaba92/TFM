# Generated by Django 4.1 on 2023-08-21 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cadena_app", "0016_actividad_plancadena_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="actividad_plancadena",
            name="nom_actividad",
            field=models.CharField(max_length=264, null=True),
        ),
    ]