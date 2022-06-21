# Generated by Django 4.0.2 on 2022-06-17 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_book_readers_alter_book_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbookrelation',
            name='rate',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Bad'), (2, 'Fine'), (3, 'Good'), (4, 'Very Good'), (5, 'Amazing')], null=True),
        ),
    ]
