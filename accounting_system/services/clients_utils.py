""" Модуль логики связанной с экранами 'КЛИЕНТЫ'. """

from typing import Any

from django.http import HttpRequest
from django.db.models import F, Count, Q

from accounting_system.models import Client, Manager


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


def save_client_changes(request: HttpRequest) -> None:
    """ Функция сохранения изменений после редактирования данных о клиенте. """
    p = request.POST
    client_pk: str = p.get('client_pk')
    client: Client = Client.objects.get(pk=client_pk)
    client.organization_name = p.get('organization_name')
    client.first_name = p.get('first_name')
    client.last_name = p.get('last_name')
    client.patronymic = p.get('patronymic')
    client.phone_number = p.get('phone_number')
    client.email = p.get('email')
    client.inn = p.get('inn')
    client.comment = p.get('comment')
    client.manager = Manager.objects.get(pk=p.get('manager_pk'))
    client.save()


def get_clients_queryset_for_manager(manager: Manager) -> Any:
    """ Функция генерации queryset с клиентами менеджера.
        Для админиов отдает всех активных менеджеров из базы.
        Для простого менеджера - только его клиентов. """
    if manager.is_staff:
        clients_queryset = Client.objects.filter(active=True)
    else:
        clients_queryset = manager.get_clients().filter(active=True).order_by('-id')
    return annotate_clients_queryset(clients_queryset)


def get_inn_list_from_active_clients() -> list:
    """ Функция генерирующая список из ИНН всех активных клиентов.
        Для экрана добавления клиента с целью поиска и запрета дублей. """
    inn_list = Client.objects.filter(active=True).values_list('inn', flat=True)
    return list(inn_list)


def get_filtered_clients(request: HttpRequest) -> Any:
    """ Функция поиска клиентов по названию организации переданной
        через поисковый инпут. """
    organization_name: str = request.POST.get('search_input')
    if request.user.is_staff:
        clients_queryset = Client.objects.filter(organization_name=organization_name, active=True)
    else:
        clients_queryset = request.user.get_clients().filter(organization_name=organization_name, active=True)
    return annotate_clients_queryset(clients_queryset)


def annotate_clients_queryset(clients_queryset):
    """ Аннотирует каждый объект из кверисета с клиентами по шаблону:
        client_first_name = Client.first_name,
        client_email = Client.email и т д. """
    return clients_queryset.annotate(
        client_organization_name=F('organization_name'), client_phone_number=F('phone_number'),
        client_inn=F('inn'), client_manager=F('manager__last_name'), client_count_services=
        Count('services', filter=Q(services__active=True) & ~Q(services__ecp_add_date=None)) +
        Count('services', filter=Q(services__active=True) & ~Q(services__ofd_add_date=None)) +
        Count('services', filter=Q(services__active=True) & ~Q(services__fn_add_date=None)) +
        Count('services', filter=Q(services__active=True) & ~Q(services__to_add_date=None))
        ).order_by('-id')
