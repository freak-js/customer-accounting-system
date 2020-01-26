from .models import ECP, CashMachine, OFD, FN, TO, Service, Client
from typing import Union
import datetime
from dateutil.relativedelta import relativedelta

from django.http import HttpRequest

# CONSTANTS

SERVICE_TYPE_DICT: dict = {'kkt': CashMachine, 'ecp': ECP, 'ofd': OFD, 'fn': FN, 'to': TO}


# FUNCTIONS


def get_service_class_instance(request: HttpRequest) -> Union[CashMachine, ECP, OFD, FN, TO]:
    """ Функция получения типа данных из ОРМ модели. """
    service_type: str = request.POST.get('service_type')
    service_class_instance: Union[CashMachine, ECP, OFD, FN, TO] = SERVICE_TYPE_DICT.get(service_type)
    return service_class_instance


def save_service_with_cash_machine(request: HttpRequest) -> None:
    """ Функция сохранения услуги при условии наличия кассы. """
    p: dict = request.POST
    client_pk: str = p.get('client_pk')
    client: Client = Client.objects.get(pk=client_pk)

    cash_machine_pk: str = p.get('cash_machine_pk')
    factory_number: str = p.get('factory_number')
    cash_machine: CashMachine = CashMachine.objects.get(pk=cash_machine_pk) if cash_machine_pk else None

    ecp_pk: str = p.get('ecp_pk')
    ecp: ECP = ECP.objects.get(pk=ecp_pk) if ecp_pk else None
    ecp_add_date: str = p.get('add_ecp_date') if p.get('add_ecp_date') else None
    ecp_expiration_date: datetime = get_expiration_date(ecp_pk, 'ecp', ecp_add_date) if ecp_add_date else None

    ofd_pk: str = p.get('ofd_pk')
    ofd: OFD = OFD.objects.get(pk=ofd_pk) if ofd_pk else None
    ofd_add_date: str = p.get('add_ofd_date') if p.get('add_ofd_date') else None
    ofd_expiration_date: datetime = get_expiration_date(ofd_pk, 'ofd', ofd_add_date) if ofd_add_date else None

    fn_pk: str = p.get('fn_pk')
    fn: FN = FN.objects.get(pk=fn_pk) if fn_pk else None
    fn_add_date: str = p.get('add_fn_date') if p.get('add_fn_date') else None
    fn_expiration_date: datetime = get_expiration_date(fn_pk, 'fn', fn_add_date) if fn_add_date else None

    to_pk: str = p.get('to_pk')
    to: TO = TO.objects.get(pk=to_pk) if to_pk else None
    to_add_date: str = p.get('add_to_date') if p.get('add_to_date') else None
    to_expiration_date: datetime = get_expiration_date(to_pk, 'to', to_add_date) if to_add_date else None

    service: Service = Service(client=client, cash_machine=cash_machine, factory_number=factory_number,
                               ecp=ecp, ecp_add_date=ecp_add_date, ecp_expiration_date=ecp_expiration_date,
                               ofd=ofd, ofd_add_date=ofd_add_date, ofd_expiration_date=ofd_expiration_date,
                               fn=fn, fn_add_date=fn_add_date, fn_expiration_date=fn_expiration_date,
                               to=to, to_add_date=to_add_date, to_expiration_date=to_expiration_date)
    service.save()


def save_service_without_cash_machine(request: HttpRequest) -> None:
    """ Функция сохранения услуги БЕЗ кассы. """
    client_pk: str = request.POST.get('client_pk')
    if ecp_pk := request.POST.get('ecp_pk'):
        ecp_add_date: str = request.POST.get('add_ecp_date')
        save_ecp_service(client_pk, ecp_pk, ecp_add_date)
    if ofd_pk := request.POST.get('ofd_pk'):
        ofd_add_date: str = request.POST.get('add_ofd_date')
        save_ofd_service(client_pk, ofd_pk, ofd_add_date)
    if fn_pk := request.POST.get('fn_pk'):
        fn_add_date: str = request.POST.get('add_fn_date')
        save_fn_service(client_pk, fn_pk, fn_add_date)
    if to_pk := request.POST.get('to_pk'):
        to_add_date: str = request.POST.get('add_to_date')
        save_to_service(client_pk, to_pk, to_add_date)


def save_ecp_service(client_pk: str, ecp_pk: str, ecp_add_date: str) -> None:
    """ Сохранение услуги ЭЦП как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    ecp: ECP = ECP.objects.get(pk=ecp_pk)
    ecp_expiration_date: datetime = get_expiration_date(ecp_pk, 'ecp', ecp_add_date)
    save_service(client=client, ecp=ecp, ecp_expiration_date=ecp_expiration_date)


def save_ofd_service(client_pk: str, ofd_pk: str, ofd_add_date: str) -> None:
    """ Сохранение услуги ОФД как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    ofd: OFD = OFD.objects.get(pk=ofd_pk)
    ofd_expiration_date: datetime = get_expiration_date(ofd_pk, 'ofd', ofd_add_date)
    save_service(client=client, ofd=ofd, ofd_expiration_date=ofd_expiration_date)


def save_fn_service(client_pk: str, fn_pk: str, fn_add_date: str) -> None:
    """ Сохранение услуги ФН как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    fn: FN = FN.objects.get(pk=fn_pk)
    fn_expiration_date: datetime = get_expiration_date(fn_pk, 'fn', fn_add_date)
    save_service(client=client, fn=fn, fn_expiration_date=fn_expiration_date)


def save_to_service(client_pk: str, to_pk: str, to_add_date: str):
    """ Сохранение услуги ТО как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    to: TO = TO.objects.get(pk=to_pk)
    to_expiration_date: datetime = get_expiration_date(to_pk, 'to', to_add_date)
    save_service(client=client, to=to, to_expiration_date=to_expiration_date)


def save_service(client=None, cash_machine=None, factory_number=None, ecp=None, ecp_add_date=None,
                 ecp_expiration_date=None, ofd=None, ofd_add_date=None, ofd_expiration_date=None,
                 fn=None, fn_add_date=None, fn_expiration_date=None, to=None, to_add_date=None,
                 to_expiration_date=None) -> None:
    """ Сохранение услуги, принимает входные данные от одной из функций
        (save_ecp_service, save_ofd_service, save_fn_service, save_to_service)
        сохраняет как отдельную услугу заполняя пустые поля значениями None. """
    service = Service(client=client, cash_machine=cash_machine, factory_number=factory_number,
                      ecp=ecp, ecp_add_date=ecp_add_date, ecp_expiration_date=ecp_expiration_date,
                      ofd=ofd, ofd_add_date=ofd_add_date, ofd_expiration_date=ofd_expiration_date,
                      fn=fn, fn_add_date=fn_add_date, fn_expiration_date=fn_expiration_date,
                      to=to, to_add_date=to_add_date, to_expiration_date=to_expiration_date)
    service.save()


def create_service_for_client(request: HttpRequest) -> None:
    """ Функция - определитель сценария сохранения.
        Проверяет наличия id кассового оборудования, в случае его наличия - вызывает
        функцию сохранения услуги с привиязкой услуг к кассе, иначе сохранет каждую
        услугу индивидуально. """
    if request.POST.get('cash_machine_pk'):
        save_service_with_cash_machine(request)
    else:
        save_service_without_cash_machine(request)


def get_expiration_date(service_pk: str, service_type: str, add_date: str) -> datetime:
    """ Функция получения даты окончания действия услуги. """
    service: Union[ECP, OFD, FN, TO] = SERVICE_TYPE_DICT[service_type].objects.get(pk=service_pk)
    validity: int = service.validity
    day: int = int(add_date[8:10])
    month: int = int(add_date[5:7])
    year: int = int(add_date[0:4])
    datetime_add_date: datetime = datetime.date(year, month, day)
    return datetime_add_date + relativedelta(months=validity)


def get_data_to_find_matches(clients_queryset) -> list:
    """ Функция формирования списка из данных для поиска совпадений на странице clients. """
    data_to_find_matches: list = []
    for client in clients_queryset:
        data_to_find_matches.append(client.organization_name)
        data_to_find_matches.append(client.phone_number)
        data_to_find_matches.append(str(client.inn))
    return data_to_find_matches
