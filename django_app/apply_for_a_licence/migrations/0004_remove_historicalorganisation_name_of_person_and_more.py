# Generated by Django 4.2.15 on 2024-08-28 10:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0003_alter_historicalservices_type_of_service_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalorganisation",
            name="name_of_person",
        ),
        migrations.RemoveField(
            model_name="organisation",
            name="name_of_person",
        ),
    ]
