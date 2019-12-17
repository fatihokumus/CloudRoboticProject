# Generated by Django 2.2.4 on 2019-12-17 06:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0017_auto_20191217_0916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robottaskhistorylog',
            name='LogTime',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 17, 9, 29, 52, 75295)),
        ),
        migrations.AlterField(
            model_name='transferredobject',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 17, 9, 29, 52, 71341)),
        ),
        migrations.AddConstraint(
            model_name='robot',
            constraint=models.UniqueConstraint(fields=('Code', 'Map'), name='idx_unique_robot_map_code'),
        ),
        migrations.AddConstraint(
            model_name='transfervehicle',
            constraint=models.UniqueConstraint(fields=('Barcode', 'Map'), name='idx_unique_tvehicle_map_code'),
        ),
    ]
