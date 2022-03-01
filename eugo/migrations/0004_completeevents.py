# Generated by Django 4.0.2 on 2022-03-01 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eugo', '0003_remove_lecturer_pos_remove_lecturer_wildorbattle_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompleteEvents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eugo.mapevent')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eugo.player')),
            ],
        ),
    ]