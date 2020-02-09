from django.db import models
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import AbstractUser


class Manager(AbstractUser):
    username = models.CharField(verbose_name='Логин', max_length=150, unique=True)
    objects = UserManager()

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def kill(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def get_clients(self):
        return self.clients.filter(active=True)


class Client(models.Model):
    organization_name = models.CharField('Название организации', max_length=100)
    first_name = models.CharField('Имя', max_length=100, null=True, blank=True)
    last_name = models.CharField('Фамилия', max_length=100, null=True, blank=True)
    patronymic = models.CharField('Отчество', max_length=100, null=True, blank=True)
    phone_number = models.CharField('Телефон', max_length=100)
    email = models.CharField('Email', max_length=100, null=True, blank=True)
    inn = models.IntegerField('ИНН')
    comment = models.TextField('Комментарий', null=True, blank=True)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, related_name='clients', null=True)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.organization_name

    def get_count_active_services(self):
        active_services = self.services.filter(active=True)
        counter = 0
        for service in active_services:
            if service.ecp: counter += 1
            if service.ofd: counter += 1
            if service.fn: counter += 1
            if service.to: counter += 1
        return counter

    def get_services(self):
        return self.services.filter(active=True)

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])

    @staticmethod
    def save_client(post):
        try:
            client = Client(
                organization_name=post['organization_name'],
                first_name=post['first_name'],
                last_name=post['last_name'],
                patronymic=post['patronymic'],
                phone_number=post['phone_number'],
                email=post['email'],
                inn=post['inn'],
                comment=post['comment'],
                manager=Manager.objects.get(pk=post['manager'])
            )
            client.save()
        except Exception:
            return False
        return client


class ECP(models.Model):
    name = models.CharField('Название ЭЦП', max_length=100)
    validity = models.IntegerField('Срок действия(месяцев)', default=12)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.name

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])


class CashMachine(models.Model):
    model = models.CharField('Модель аппарата', max_length=100)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.model

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])


class OFD(models.Model):
    model = models.CharField('Название', max_length=100)
    validity = models.IntegerField('Срок действия(месяцев)')
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.model

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])


class FN(models.Model):
    name = models.CharField('Название ФН', max_length=100)
    validity = models.IntegerField('Срок действия(месяцев)', default=12)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.name

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])


class TO(models.Model):
    name = models.CharField('Название договора', max_length=100)
    validity = models.IntegerField('Срок действия(месяцев)', default=12)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.name

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])


class Service(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True, related_name='services')
    cash_machine = models.ForeignKey(CashMachine, on_delete=models.SET_NULL, blank=True, null=True)
    factory_number = models.CharField('Заводской номер', max_length=50, null=True, blank=True)

    ecp = models.ForeignKey(ECP, on_delete=models.SET_NULL, blank=True, null=True)
    ecp_add_date = models.DateField('Дата покупки ЭЦП', blank=True, null=True)
    ecp_expiration_date = models.DateField('Дата окончания срока действия ЭЦП', blank=True, null=True)
    ecp_status = models.CharField('Статус', max_length=2, null=True, blank=True)
    ecp_days_to_finish = models.IntegerField('Дней до кончания действия услуги', blank=True, null=True)

    ofd = models.ForeignKey(OFD, on_delete=models.SET_NULL, blank=True, null=True)
    ofd_add_date = models.DateField('Дата покупки ОФД', blank=True, null=True)
    ofd_expiration_date = models.DateField('Дата окончания срока действия ОФД', blank=True, null=True)
    ofd_status = models.CharField('Статус', max_length=2, null=True, blank=True)
    ofd_days_to_finish = models.IntegerField('Дней до кончания действия услуги', blank=True, null=True)

    fn = models.ForeignKey(FN, on_delete=models.SET_NULL, blank=True, null=True)
    fn_add_date = models.DateField('Дата покупки ФН', blank=True, null=True)
    fn_expiration_date = models.DateField('Дата окончания срока действия ФН', blank=True, null=True)
    fn_status = models.CharField('Статус', max_length=2, null=True, blank=True)
    fn_days_to_finish = models.IntegerField('Дней до кончания действия услуги', blank=True, null=True)

    to = models.ForeignKey(TO, on_delete=models.SET_NULL, blank=True, null=True)
    to_add_date = models.DateField('Дата заключения договора на ТО аппарата', blank=True, null=True)
    to_expiration_date = models.DateField('Дата окончания срока договора на ТО аппарата', blank=True, null=True)
    to_status = models.CharField('Статус', max_length=2, null=True, blank=True)
    to_days_to_finish = models.IntegerField('Дней до кончания действия услуги', blank=True, null=True)

    active = models.BooleanField(default=True)
    objects = models.Manager()

    def kill(self):
        self.active = False
        self.save(update_fields=['active'])
