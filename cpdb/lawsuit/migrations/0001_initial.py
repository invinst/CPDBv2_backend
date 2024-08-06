# Generated by Django 2.2.10 on 2020-07-28 04:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data', '0124_attachmentnarrative'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lawsuit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('case_no', models.CharField(db_index=True, max_length=20, unique=True)),
                ('incident_date', models.DateTimeField(null=True)),
                ('summary', models.TextField()),
                ('location', models.CharField(blank=True, max_length=64)),
                ('add1', models.CharField(blank=True, max_length=16)),
                ('add2', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LawsuitInteraction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LawsuitMisconduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LawsuitOutcome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LawsuitService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LawsuitViolence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payee', models.CharField(max_length=255)),
                ('settlement', models.DecimalField(decimal_places=2, max_digits=16, null=True)),
                ('legal_fees', models.DecimalField(decimal_places=2, max_digits=16, null=True)),
                ('lawsuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='lawsuit.Lawsuit')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LawsuitPlaintiff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
                ('lawsuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plaintiffs', to='lawsuit.Lawsuit')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='interactions',
            field=models.ManyToManyField(to='lawsuit.LawsuitInteraction'),
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='misconducts',
            field=models.ManyToManyField(to='lawsuit.LawsuitMisconduct'),
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='officers',
            field=models.ManyToManyField(to='data.Officer'),
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='outcomes',
            field=models.ManyToManyField(to='lawsuit.LawsuitOutcome'),
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='services',
            field=models.ManyToManyField(to='lawsuit.LawsuitService'),
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='violences',
            field=models.ManyToManyField(to='lawsuit.LawsuitViolence'),
        ),
    ]
