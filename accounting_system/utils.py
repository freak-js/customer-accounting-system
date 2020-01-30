from .models import ECP, CashMachine, OFD, FN, TO, Service, Client, Manager
from typing import Union, List
import datetime
from dateutil.relativedelta import relativedelta
from django.http import HttpRequest
from django.db.models import Count, Q
import time
from typing import Any

# CONSTANTS

SERVICE_TYPE_DICT: dict = {'kkt': CashMachine, 'ecp': ECP, 'ofd': OFD, 'fn': FN, 'to': TO}

UPDATE_FIELD_LIST = ['ecp_days_to_finish', 'ecp_status', 'ofd_days_to_finish', 'ofd_status',
                     'fn_days_to_finish', 'fn_status', 'to_days_to_finish', 'to_status']


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
    ecp_days_to_finish: int = get_days_to_finish(ecp_expiration_date) if ecp_expiration_date else None
    ecp_status: str = get_service_status(ecp_days_to_finish) if ecp_expiration_date else None

    ofd_pk: str = p.get('ofd_pk')
    ofd: OFD = OFD.objects.get(pk=ofd_pk) if ofd_pk else None
    ofd_add_date: str = p.get('add_ofd_date') if p.get('add_ofd_date') else None
    ofd_expiration_date: datetime = get_expiration_date(ofd_pk, 'ofd', ofd_add_date) if ofd_add_date else None
    ofd_days_to_finish: int = get_days_to_finish(ofd_expiration_date) if ofd_expiration_date else None
    ofd_status: str = get_service_status(ofd_days_to_finish) if ofd_expiration_date else None

    fn_pk: str = p.get('fn_pk')
    fn: FN = FN.objects.get(pk=fn_pk) if fn_pk else None
    fn_add_date: str = p.get('add_fn_date') if p.get('add_fn_date') else None
    fn_expiration_date: datetime = get_expiration_date(fn_pk, 'fn', fn_add_date) if fn_add_date else None
    fn_days_to_finish: int = get_days_to_finish(fn_expiration_date) if fn_expiration_date else None
    fn_status: str = get_service_status(fn_days_to_finish) if fn_expiration_date else None

    to_pk: str = p.get('to_pk')
    to: TO = TO.objects.get(pk=to_pk) if to_pk else None
    to_add_date: str = p.get('add_to_date') if p.get('add_to_date') else None
    to_expiration_date: datetime = get_expiration_date(to_pk, 'to', to_add_date) if to_add_date else None
    to_days_to_finish: int = get_days_to_finish(to_expiration_date) if to_expiration_date else None
    to_status: str = get_service_status(to_days_to_finish) if to_expiration_date else None

    service: Service = Service(client=client, cash_machine=cash_machine, factory_number=factory_number,
                               ecp=ecp, ecp_add_date=ecp_add_date, ecp_expiration_date=ecp_expiration_date,
                               ecp_days_to_finish=ecp_days_to_finish, ecp_status=ecp_status,
                               ofd=ofd, ofd_add_date=ofd_add_date, ofd_expiration_date=ofd_expiration_date,
                               ofd_days_to_finish=ofd_days_to_finish, ofd_status=ofd_status,
                               fn=fn, fn_add_date=fn_add_date, fn_expiration_date=fn_expiration_date,
                               fn_days_to_finish=fn_days_to_finish, fn_status=fn_status,
                               to=to, to_add_date=to_add_date, to_expiration_date=to_expiration_date,
                               to_days_to_finish=to_days_to_finish, to_status=to_status, )
    service.save()


def make_changes_to_the_service(request: HttpRequest) -> None:
    """ Функция внесения изменений в существующую услугу для клиента. """
    p: dict = request.POST
    cash_machine_pk: str = p.get('cash_machine_pk')
    ecp_pk: str = p.get('ecp_pk')
    ofd_pk: str = p.get('ofd_pk')
    fn_pk: str = p.get('fn_pk')
    to_pk: str = p.get('to_pk')
    service = Service.objects.get(pk=p.get('service_pk'))

    service.cash_machine = CashMachine.objects.get(pk=cash_machine_pk) if cash_machine_pk else None
    service.factory_number = p.get('factory_number')

    service.ecp = ECP.objects.get(pk=ecp_pk) if ecp_pk else None
    service.ecp_add_date = p.get('add_ecp_date') if p.get('add_ecp_date') else None
    service.ecp_expiration_date = get_expiration_date(ecp_pk, 'ecp',
                                                      service.ecp_add_date) if service.ecp_add_date else None
    service.ecp_days_to_finish = get_days_to_finish(
        service.ecp_expiration_date) if service.ecp_expiration_date else None
    service.ecp_status = get_service_status(service.ecp_days_to_finish) if service.ecp_expiration_date else None

    service.ofd = OFD.objects.get(pk=ofd_pk) if ofd_pk else None
    service.ofd_add_date = p.get('add_ofd_date') if p.get('add_ofd_date') else None
    service.ofd_expiration_date = get_expiration_date(ofd_pk, 'ofd',
                                                      service.ofd_add_date) if service.ofd_add_date else None
    service.ofd_days_to_finish = get_days_to_finish(
        service.ofd_expiration_date) if service.ofd_expiration_date else None
    service.ofd_status = get_service_status(service.ofd_days_to_finish) if service.ofd_expiration_date else None

    service.fn = FN.objects.get(pk=fn_pk) if fn_pk else None
    service.fn_add_date = p.get('add_fn_date') if p.get('add_fn_date') else None
    service.fn_expiration_date = get_expiration_date(fn_pk, 'fn', service.fn_add_date) if service.fn_add_date else None
    service.fn_days_to_finish = get_days_to_finish(service.fn_expiration_date) if service.fn_expiration_date else None
    service.fn_status = get_service_status(service.fn_days_to_finish) if service.fn_expiration_date else None

    service.to = TO.objects.get(pk=to_pk) if to_pk else None
    service.to_add_date = p.get('add_to_date') if p.get('add_to_date') else None
    service.to_expiration_date = get_expiration_date(to_pk, 'to', service.to_add_date) if service.to_add_date else None
    service.to_days_to_finish = get_days_to_finish(service.to_expiration_date) if service.to_expiration_date else None
    service.to_status = get_service_status(service.to_days_to_finish) if service.to_expiration_date else None
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
    ecp_days_to_finish: int = get_days_to_finish(ecp_expiration_date)
    ecp_status: str = get_service_status(ecp_days_to_finish)
    save_service(client=client, ecp=ecp, ecp_add_date=ecp_add_date, ecp_expiration_date=ecp_expiration_date,
                 ecp_days_to_finish=ecp_days_to_finish, ecp_status=ecp_status)


def save_ofd_service(client_pk: str, ofd_pk: str, ofd_add_date: str) -> None:
    """ Сохранение услуги ОФД как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    ofd: OFD = OFD.objects.get(pk=ofd_pk)
    ofd_expiration_date: datetime = get_expiration_date(ofd_pk, 'ofd', ofd_add_date)
    ofd_days_to_finish: int = get_days_to_finish(ofd_expiration_date)
    ofd_status: str = get_service_status(ofd_days_to_finish)
    save_service(client=client, ofd=ofd, ofd_add_date=ofd_add_date, ofd_expiration_date=ofd_expiration_date,
                 ofd_days_to_finish=ofd_days_to_finish, ofd_status=ofd_status)


def save_fn_service(client_pk: str, fn_pk: str, fn_add_date: str) -> None:
    """ Сохранение услуги ФН как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    fn: FN = FN.objects.get(pk=fn_pk)
    fn_expiration_date: datetime = get_expiration_date(fn_pk, 'fn', fn_add_date)
    fn_days_to_finish: int = get_days_to_finish(fn_expiration_date)
    fn_status: str = get_service_status(fn_days_to_finish)
    save_service(client=client, fn=fn, fn_add_date=fn_add_date, fn_expiration_date=fn_expiration_date,
                 fn_days_to_finish=fn_days_to_finish, fn_status=fn_status)


def save_to_service(client_pk: str, to_pk: str, to_add_date: str):
    """ Сохранение услуги ТО как отдельную услугу. """
    client: Client = Client.objects.get(pk=client_pk)
    to: TO = TO.objects.get(pk=to_pk)
    to_expiration_date: datetime = get_expiration_date(to_pk, 'to', to_add_date)
    to_days_to_finish: int = get_days_to_finish(to_expiration_date)
    to_status: str = get_service_status(to_days_to_finish)
    save_service(client=client, to=to, to_add_date=to_add_date, to_expiration_date=to_expiration_date,
                 to_days_to_finish=to_days_to_finish, to_status=to_status)


def save_service(client=None, cash_machine=None, factory_number=None,
                 ecp=None, ecp_add_date=None, ecp_expiration_date=None, ecp_days_to_finish=None, ecp_status=None,
                 ofd=None, ofd_add_date=None, ofd_expiration_date=None, ofd_days_to_finish=None, ofd_status=None,
                 fn=None, fn_add_date=None, fn_expiration_date=None, fn_days_to_finish=None, fn_status=None,
                 to=None, to_add_date=None, to_expiration_date=None, to_days_to_finish=None, to_status=None) -> None:
    """ Сохранение услуги, принимает входные данные от одной из функций
        (save_ecp_service, save_ofd_service, save_fn_service, save_to_service)
        сохраняет как отдельную услугу заполняя пустые поля значениями None. """
    service = Service(client=client, cash_machine=cash_machine, factory_number=factory_number,
                      ecp=ecp, ecp_add_date=ecp_add_date, ecp_expiration_date=ecp_expiration_date,
                      ecp_days_to_finish=ecp_days_to_finish, ecp_status=ecp_status,
                      ofd=ofd, ofd_add_date=ofd_add_date, ofd_expiration_date=ofd_expiration_date,
                      ofd_days_to_finish=ofd_days_to_finish, ofd_status=ofd_status,
                      fn=fn, fn_add_date=fn_add_date, fn_expiration_date=fn_expiration_date,
                      fn_days_to_finish=fn_days_to_finish, fn_status=fn_status,
                      to=to, to_add_date=to_add_date, to_expiration_date=to_expiration_date,
                      to_days_to_finish=to_days_to_finish, to_status=to_status)
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


def get_days_to_finish(expiration_date: datetime) -> int:
    """ Функция получения количества дней до окончания срока действия услуги. """
    return (expiration_date - datetime.date.today()).days


def get_service_status(days_to_finish: int) -> str:
    """ Функция получения статуса услуги в виде строкового кода.
        Отслеживает значение количества дней до окончания услуги и присваивает соответсвующий код.
        Менее 0 дней - код: 'FA' (FAILED)
        Менее 10-ти дней - код: 'AL' (ALARM)
        Менее 30-ти дней - код: 'AT' (ATTENTION)
        Более 30-ти дней - код: 'OK' (OK). """
    if days_to_finish < 0:
        return 'FA'
    if days_to_finish < 10:
        return 'AL'
    elif days_to_finish < 30:
        return 'AT'
    else:
        return 'OK'


def get_data_to_find_matches(clients_queryset) -> list:
    """ Функция формирования списка из данных для поиска совпадений на странице clients. """
    data_to_find_matches: list = []
    for client in clients_queryset:
        data_to_find_matches.append(client.organization_name)
        data_to_find_matches.append(client.phone_number)
        data_to_find_matches.append(str(client.inn))
    return data_to_find_matches


def get_client_profile_context(request: HttpRequest) -> dict:
    """ Функция генерации контекста для контроллера рендера страницы профайла клиента. """
    client_pk: str = request.POST.get('client_pk')
    client: Client = Client.objects.get(pk=client_pk)
    client_services = client.get_services()
    context: dict = {'page': 'clients', 'client': client, 'user': request.user,
                     'client_services': client_services, 'client_pk': client_pk}
    return context


def get_tasks_list(user: Manager) -> List[Service]:
    """ Функция получения списка услуг, с подходящим к окончанию,
        или истекшим сроком действия услуги.
        Проверяет на отсутсвие статуса 'ОК' в каждой из подуслуг,
        в случае его отсутсвия - добавляет услугу в список task_list. """
    task_list: list = []
    if user.is_staff:
        service_queryset = Service.objects.filter(active=True, client__active=True)
        for service in service_queryset:
            if check_service_overdue(service):
                task_list.append(service)
    else:
        manager_clients_queryset = user.get_clients()
        for client in manager_clients_queryset:
            for service in client.get_services():
                if check_service_overdue(service):
                    task_list.append(service)
    return task_list


def check_service_overdue(service: Service) -> bool:
    """ Функция проверки статуса услуги.
        В случае несовпадения со статусом 'OK' возвращет True. """
    if service.ecp_status and service.ecp_status != 'OK':
        return True
    if service.ofd_status and service.ofd_status != 'OK':
        return True
    if service.fn_status and service.fn_status != 'OK':
        return True
    if service.to_status and service.to_status != 'OK':
        return True
    return False


def update_tasks_status() -> None:
    """ Функция апдейта статусов услуг при входе менеджера в систему. """
    service_queryset = Service.objects.filter(active=True)
    service_objects_list = [update_task(service) for service in service_queryset]
    Service.objects.bulk_update(service_objects_list, UPDATE_FIELD_LIST)


def update_task(service: Service) -> Service:
    """ Функция пересчета и обновления дней до окончания услуги и статуса услуги. """
    if service.ecp_expiration_date:
        service.ecp_days_to_finish = get_days_to_finish(service.ecp_expiration_date)
        service.ecp_status = get_service_status(service.ecp_days_to_finish)
    if service.ofd_expiration_date:
        service.ofd_days_to_finish = get_days_to_finish(service.ofd_expiration_date)
        service.ofd_status = get_service_status(service.ofd_days_to_finish)
    if service.fn_expiration_date:
        service.fn_days_to_finish = get_days_to_finish(service.fn_expiration_date)
        service.fn_status = get_service_status(service.fn_days_to_finish)
    if service.to_expiration_date:
        service.to_days_to_finish = get_days_to_finish(service.to_expiration_date)
        service.to_status = get_service_status(service.to_days_to_finish)
    return service


def get_managers_queryset() -> Any:
    managers_queryset = Manager.objects.filter(is_active=True, clients__active=True,
        clients__services__active=True).annotate(
            count_failed_tasks=Count('clients__services', filter=Q(clients__services__ecp_status='FA')) +
                Count('clients__services', filter=Q(clients__services__ofd_status='FA')) +
                Count('clients__services', filter=Q(clients__services__fn_status='FA')) +
                Count('clients__services', filter=Q(clients__services__to_status='FA')),
            count_tasks=Count('clients__services', filter=Q(clients__services__ecp_status='AL') |
                Q(clients__services__ecp_status='AT')) +
                Count('clients__services', filter=Q(clients__services__ofd_status='AL') |
                Q(clients__services__ofd_status='AT')) +
                Count('clients__services', filter=Q(clients__services__fn_status='AL') |
                Q(clients__services__fn_status='AT')) +
                Count('clients__services', filter=Q(clients__services__to_status='AL') |
                Q(clients__services__to_status='AT'))
    )
    print(managers_queryset.query)
    return managers_queryset
