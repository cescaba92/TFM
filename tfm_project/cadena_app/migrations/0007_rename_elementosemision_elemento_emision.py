# Generated by Django 4.1 on 2023-07-31 20:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cadena_app", "0006_midpoint_emision_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ElementosEmision",
            new_name="Elemento_Emision",
        ),
    ]
