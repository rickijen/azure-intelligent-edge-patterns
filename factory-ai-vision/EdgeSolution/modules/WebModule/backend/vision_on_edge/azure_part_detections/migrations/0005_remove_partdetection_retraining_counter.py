# Generated by Django 3.0.8 on 2020-08-28 07:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("azure_part_detections", "0004_remove_partdetection_location")]

    operations = [
        migrations.RemoveField(model_name="partdetection", name="retraining_counter")
    ]