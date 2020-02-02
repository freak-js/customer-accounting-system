""" Модуль логики связанной с экраном 'КАЛЕНДАРЬ'. """

from typing import List

from accounting_system.models import Manager, Service


def get_event_list(manager: Manager) -> List[dict]:
    event_list: List[dict] = []
    if manager.is_staff:
        services_queryset = Service.objects.filter(active=True)
    else:
        services_queryset = Service.objects.filter(active=True, client__active=True, client__manager=manager.pk)
    for service in services_queryset:
        if service.ecp_expiration_date:
            event_list.append({'date': str(service.ecp_expiration_date) + ' 00:00:00',
                               'title': str(service.client), 'description': str(service.ecp)})
        if service.ofd_expiration_date:
            event_list.append({'date': str(service.ofd_expiration_date) + ' 00:00:00',
                               'title': str(service.client), 'description': str(service.ofd)})
        if service.fn_expiration_date:
            event_list.append({'date': str(service.fn_expiration_date) + ' 00:00:00',
                               'title': str(service.client), 'description': str(service.fn)})
        if service.to_expiration_date:
            event_list.append({'date': str(service.to_expiration_date) + ' 00:00:00',
                               'title': str(service.client), 'description': str(service.to)})
    return event_list
