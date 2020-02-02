""" Модуль логики связанной с экранами 'КЛИЕНТЫ'. """

from django.http import HttpRequest

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
