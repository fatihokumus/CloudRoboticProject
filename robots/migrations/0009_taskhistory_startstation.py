# Generated by Django 2.2.5 on 2019-12-12 07:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0008_auto_20191212_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskhistory',
            name='StartStation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='StartStation_TOTask', to='robots.StartStation'),
        ),
    ]