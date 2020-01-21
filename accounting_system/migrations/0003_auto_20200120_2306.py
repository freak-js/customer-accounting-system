# Generated by Django 2.2.9 on 2020-01-20 20:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting_system', '0002_auto_20200116_0140'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='manager',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='fn',
            name='validity',
            field=models.IntegerField(default=12, verbose_name='Срок действия(месяцев)'),
        ),
        migrations.AlterField(
            model_name='ofd',
            name='validity',
            field=models.IntegerField(verbose_name='Срок действия(месяцев)'),
        ),
        migrations.AlterField(
            model_name='service',
            name='ecp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounting_system.ECP'),
        ),
        migrations.AlterField(
            model_name='service',
            name='ecp_add_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата покупки ЭЦП'),
        ),
        migrations.AlterField(
            model_name='service',
            name='ecp_expiration_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата окончания срока действия ЭЦП'),
        ),
        migrations.AlterField(
            model_name='service',
            name='fn_add_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата покупки ФН'),
        ),
        migrations.AlterField(
            model_name='service',
            name='fn_expiration_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата окончания срока действия ФН'),
        ),
        migrations.AlterField(
            model_name='service',
            name='ofd_add_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата покупки ОФД'),
        ),
        migrations.AlterField(
            model_name='service',
            name='ofd_expiration_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата окончания срока действия ОФД'),
        ),
        migrations.AlterField(
            model_name='service',
            name='to_add_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата заключения договора на ТО аппарата'),
        ),
        migrations.AlterField(
            model_name='service',
            name='to_expiration_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата окончания срока договора на ТО аппарата'),
        ),
        migrations.AlterField(
            model_name='to',
            name='validity',
            field=models.IntegerField(default=12, verbose_name='Срок действия(месяцев)'),
        ),
    ]
