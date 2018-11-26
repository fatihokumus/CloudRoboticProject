# Generated by Django 2.1.3 on 2018-11-26 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0007_auto_20181126_1429'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CurrentSticker', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='custom_sticker', to='robots.Sticker')),
                ('Down', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='down_sticker', to='robots.Sticker')),
                ('Left', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='left_sticker', to='robots.Sticker')),
                ('Map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='robots.Map')),
                ('Right', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='right_sticker', to='robots.Sticker')),
                ('Top', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='top_sticker', to='robots.Sticker')),
            ],
        ),
    ]