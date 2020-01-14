from django.db import models
from django.contrib.auth.models import AbstractUser


class Manager(AbstractUser):

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Client(models.Model):
    organization_name = models.CharField('Название организации', max_length=100)
    first_name = models.CharField('Имя', max_length=100, null=True, blank=True)
    last_name = models.CharField('Фамилия', max_length=100, null=True, blank=True)
    patronymic = models.CharField('Отчество', max_length=100, null=True, blank=True)
    phone_number = models.CharField('Телефон', max_length=100)
    email = models.CharField('Email', max_length=100, null=True, blank=True)
    inn = models.IntegerField('ИНН')
    comment = models.TextField('Комментарий', null=True, blank=True)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.organization_name


class ECP(models.Model):
    name = models.CharField('Название ЭЦП', max_length=100, default='ЭЦП на 1 год')
    validity = models.IntegerField('Срок действия(лет)', default=1)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CashMachine(models.Model):
    model = models.CharField('Модель аппарата', max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.model


class OFD(models.Model):
    model = models.CharField('Название', max_length=100)
    validity = models.IntegerField('Срок действия(меясцев)')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.model


class FN(models.Model):
    name = models.CharField('Название ФН', max_length=100)
    validity = models.IntegerField('Срок действия(меясцев)')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TO(models.Model):
    name = models.CharField('Название договора', max_length=100)
    validity = models.IntegerField('Срок действия(лет)', default=1)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True, related_name='services')
    cash_machine = models.ForeignKey(CashMachine, on_delete=models.SET_NULL, blank=True, null=True)
    ecp = models.ForeignKey(Manager, on_delete=models.SET_NULL, blank=True, null=True)
    ecp_add_date = models.DateField('Дата покупки ЭЦП')
    ecp_expiration_date = models.DateField('Дата окончания срока действия ЭЦП')
    ofd = models.ForeignKey(OFD, on_delete=models.SET_NULL, blank=True, null=True)
    ofd_add_date = models.DateField('Дата покупки ОФД')
    ofd_expiration_date = models.DateField('Дата окончания срока действия ОФД')
    fn = models.ForeignKey(FN, on_delete=models.SET_NULL, blank=True, null=True)
    fn_add_date = models.DateField('Дата покупки ФН')
    fn_expiration_date = models.DateField('Дата окончания срока действия ФН')
    to = models.ForeignKey(TO, on_delete=models.SET_NULL, blank=True, null=True)
    to_add_date = models.DateField('Дата заключения договора на ТО аппарата')
    to_expiration_date = models.DateField('Дата окончания срока договора на ТО аппарата')
