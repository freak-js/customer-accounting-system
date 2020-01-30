from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from .utils import (get_service_class_instance, create_service_for_client, get_data_to_find_matches,
                    make_changes_to_the_service, get_client_profile_context, get_tasks_list,
                    update_tasks_status, get_managers_queryset)
from .forms import (CustomUserCreationForm, ManagerChangeForm, CashMachineCreationForm, FNCreationForm,
                    TOCreationForm, ECPCreationForm, OFDCreationForm)
from .models import Manager, Client, CashMachine, ECP, OFD, FN, TO, Service
from typing import Union
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


# AUTH


@receiver(user_logged_in)
def signal_user_logged_in(sender, user: Manager, request: HttpRequest, **kwargs) -> None:
    """ Контроллер пересчета и обновления статусов и колчества дней до кончания услуги.
        Вызывается при логине любого из менеджеров. """
    update_tasks_status()


@login_required
def auth(request: HttpRequest) -> HttpResponse:
    """ Контроллер авторизации пользователей. """
    return render(request, 'accounting_system/auth.html', {'form': AuthenticationForm})


def logout_view(request: HttpRequest) -> HttpResponse:
    """ Контроллер выхода из системы. """
    logout(request)
    return redirect('login')


# CLIENTS


@login_required
def clients(request: HttpRequest) -> HttpResponse:
    """ Контроллер со списком клиентов и живым регистронезависимым поиском. """
    if request.user.is_staff:
        clients_queryset = Client.objects.filter(active=True).order_by('-id')
        data_to_find_matches: list = get_data_to_find_matches(clients_queryset)
    else:
        clients_queryset = request.user.get_clients().filter(active=True).order_by('-id')
        data_to_find_matches: list = get_data_to_find_matches(clients_queryset)
    context: dict = {'page': 'clients', 'user': request.user, 'clients': clients_queryset[:10],
                     'data_to_find_matches': str(data_to_find_matches)}
    return render(request, 'accounting_system/clients/clients.html', context)


@login_required
def filter_clients(request: HttpRequest) -> HttpResponse:
    """ Контроллер с отфильтрованным списком клиентов по данным полученным из clients.
        Мимикрирует под clients с сохранением функционала. """
    organization_name: str = request.POST.get('search_input')
    if request.user.is_staff:
        clients_queryset = Client.objects.filter(organization_name=organization_name)
        not_filter_clients = Client.objects.filter(active=True)
        data_to_find_matches: list = get_data_to_find_matches(not_filter_clients)
    else:
        clients_queryset = request.user.get_clients().filter(organization_name=organization_name)
        not_filter_clients = request.user.get_clients().filter(active=True)
        data_to_find_matches: list = get_data_to_find_matches(not_filter_clients)
    context: dict = {'page': 'clients', 'user': request.user, 'clients': clients_queryset,
                     'data_to_find_matches': str(data_to_find_matches)}
    return render(request, 'accounting_system/clients/clients.html', context)


@login_required
def add_client(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления клиента. """
    if request.method == 'POST':
        if Client.save_client(request.POST):
            return redirect('clients')
        # TODO Добавить выведение ошибки при сохранении клиента (экран уведомлений)
    managers = Manager.objects.filter(is_active=True)
    context: dict = {'page': 'clients', 'user': request.user, 'managers': managers}
    return render(request, 'accounting_system/clients/add_client.html', context)


@login_required
def delete_client(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления клиента """
    if client_pk := request.POST.get('client_pk_for_delete'):
        client: Client = get_object_or_404(Client, pk=client_pk)
        client.kill()
        return redirect('clients')
    client_pk: str = request.POST.get('client_pk')
    client: Client = get_object_or_404(Client, pk=client_pk)
    context: dict = {'page': 'clients', 'client': client, 'user': request.user}
    return render(request, 'accounting_system/clients/delete_client.html', context)


@login_required
def client_profile(request: HttpRequest) -> HttpResponse:
    """ Контроллер профиля клиента. Отображает список услуг присвоенных клиенту. """
    context = get_client_profile_context(request)
    return render(request, 'accounting_system/clients/client_profile.html', context)


# STAFF


@login_required
@staff_member_required
def staff(request: HttpRequest) -> HttpResponse:
    """ Контроллер со списком пользователей зарегестрированных в системе.
        Доступен только администратору и суперпользователю. """
    managers = get_managers_queryset().order_by('pk')
    context: dict = {'page': 'staff', 'managers': managers, 'user': request.user}
    return render(request, 'accounting_system/managers/staff.html', context)


@login_required
@staff_member_required
def add_manager(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления нового менеджера в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: CustomUserCreationForm = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff')
    else:
        form = CustomUserCreationForm()
    context: dict = {'page': 'staff', 'form': form, 'user': request.user}
    return render(request, 'accounting_system/managers/add_manager.html', context)


@login_required
@staff_member_required
def change_manager_form(request: HttpRequest) -> HttpResponse:
    """ Контроллер изменения данных менеджера.
        Доступен только администратору и суперпользователю. """
    change_manager_pk: str = request.POST.get('manager_pk')
    manager: Manager = get_object_or_404(Manager, pk=change_manager_pk)
    form: ManagerChangeForm = ManagerChangeForm(instance=manager)
    context: dict = {'page': 'staff', 'form': form, 'user': request.user, 'change_manager': manager}
    return render(request, 'accounting_system/managers/change_manager.html', context)


@login_required
@require_POST
@staff_member_required
def change_manager(request: HttpRequest) -> HttpResponse:
    """ Контроллер изменения данных менеджера.
        Доступен только администратору и суперпользователю. """
    manager_pk_for_change: str = request.POST.get('manager_pk_for_change')
    manager: Manager = get_object_or_404(Manager, pk=manager_pk_for_change)
    form: ManagerChangeForm = ManagerChangeForm(request.POST, instance=manager)
    if form.is_valid():
        form.save()
        return redirect('staff')


@login_required
@staff_member_required
def delete_manager(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления менеджера.
        Доступен только администратору и суперпользователю. """
    if manager_pk := request.POST.get('manager_pk_for_delete'):
        manager: Manager = get_object_or_404(Manager, pk=manager_pk)
        manager.kill()
        return redirect('staff')
    manager_pk: str = request.POST.get('manager_pk')
    manager: Manager = get_object_or_404(Manager, pk=manager_pk)
    context: dict = {'page': 'staff', 'user': request.user, 'manager': manager}
    return render(request, 'accounting_system/managers/delete_manager.html', context)


# TASKS


@login_required
def tasks(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы с задачами пользователя.
        Для менеджера выводит список его задач.
        Для администратора выводит список задач всех менеджеров в системе,
        включая и его собственные. """
    tasks_list = get_tasks_list(request.user)
    context: dict = {'page': 'tasks', 'user': request.user, 'tasks': tasks_list}
    return render(request, 'accounting_system/tasks/tasks.html', context)


# CALENDAR


@login_required
def calendar(request: HttpRequest) -> HttpResponse:
    """ Контроллер интерактивного календаря. """
    context: dict = {'page': 'calendar', 'user': request.user}
    return render(request, 'accounting_system/calendar/calendar.html', context)


# SERVICE


@login_required
@staff_member_required
def service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы с услкгами. Формирует список доступных категорий услуг.
        Доступен только администратору и суперпользователю. """
    context: dict = {'page': 'service', 'user': request.user}
    return render(request, 'accounting_system/services/service.html', context)


@login_required
@require_POST
def add_service_for_client_form(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы с формой добавления услуги для клиента. """
    client_pk: str = request.POST.get('client_pk')
    kkt_list = CashMachine.objects.filter(active=True)
    ecp_list = ECP.objects.filter(active=True)
    ofd_list = OFD.objects.filter(active=True)
    fn_list = FN.objects.filter(active=True)
    to_list = TO.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'client_pk': client_pk,
                     'kkt_list': kkt_list, 'ecp_list': ecp_list, 'ofd_list': ofd_list,
                     'fn_list': fn_list, 'to_list': to_list}
    return render(request, 'accounting_system/services/add_service_for_client.html', context)


@login_required
@require_POST
def add_service_for_client(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления услуги для клиента. Использует логику из модуля utils.py. """
    create_service_for_client(request)
    return redirect('clients')


@login_required
@require_POST
@staff_member_required
def delete_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления услуги из системы.
        Доступен только администратору и суперпользователю. """
    back_path: str = request.POST.get('back_path')
    service_pk: str = request.POST.get('service_pk')
    service_class_instance: Union[ECP, OFD, FN, TO] = get_service_class_instance(request)
    service_object: Union[ECP, OFD, FN, TO] = get_object_or_404(service_class_instance, pk=service_pk)
    service_object.kill()
    return redirect(back_path)


@login_required
@require_POST
def delete_service_from_client(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления улуги присвоенной клиенту. """
    client_pk: str = request.POST.get('client_pk')
    if service_pk := request.POST.get('service_pk_for_delete'):
        service_object: Service = get_object_or_404(Service, pk=service_pk)
        service_object.kill()
        context = get_client_profile_context(request)
        return render(request, 'accounting_system/clients/client_profile.html', context)
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'clients', 'user': request.user, 'service_pk': service_pk, 'client_pk': client_pk}
    return render(request, 'accounting_system/services/delete_service_from_client.html', context)


def change_service_for_client_form(request: HttpRequest) -> HttpResponse:
    """ Контроллер изменения услуги присвоенной клиенту """
    client_pk: str = request.POST.get('client_pk')
    service_pk: str = request.POST.get('service_pk')
    service_object: Service = get_object_or_404(Service, pk=service_pk)
    kkt_list = CashMachine.objects.filter(active=True)
    ecp_list = ECP.objects.filter(active=True)
    ofd_list = OFD.objects.filter(active=True)
    fn_list = FN.objects.filter(active=True)
    to_list = TO.objects.filter(active=True)
    context: dict = {'page': 'clients', 'user': request.user, 'service': service_object, 'kkt_list': kkt_list,
                     'ecp_list': ecp_list, 'ofd_list': ofd_list, 'fn_list': fn_list, 'to_list': to_list,
                     'client_pk': client_pk}
    return render(request, 'accounting_system/services/change_service_for_client_form.html', context)


def save_service_changes(request: HttpRequest) -> HttpResponse:
    """ Контроллер сохранения изменений в услуге. """
    make_changes_to_the_service(request)
    context = get_client_profile_context(request)
    return render(request, 'accounting_system/clients/client_profile.html', context)


# KKT


@login_required
@staff_member_required
def kkt_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы со списком кассовой техники внесенной в систему.
        Доступен только администратору и суперпользователю. """
    kkt_list = CashMachine.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'kkt_list': kkt_list}
    return render(request, 'accounting_system/services/kkt_service.html', context)


@login_required
@staff_member_required
def add_kkt(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления кассового аппарата в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: CashMachineCreationForm = CashMachineCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kkt-service')
    form: CashMachineCreationForm = CashMachineCreationForm()
    context: dict = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/services/add_kkt.html', context)


@login_required
@staff_member_required
def delete_kkt(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления кассового аппарата из системы.
        Доступен только администратору и суперпользователю. """
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'service', 'user': request.user,
                     'service_pk': service_pk, 'service_type': 'kkt', 'back_path': 'kkt-service'}
    return render(request, 'accounting_system/services/delete_service.html', context)


# FN


@login_required
@staff_member_required
def fn_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы со списком фискальных накопителей внесенных в систему.
        Доступен только администратору и суперпользователю. """
    fn_list = FN.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'fn_list': fn_list}
    return render(request, 'accounting_system/services/fn_service.html', context)


@login_required
@staff_member_required
def add_fn(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления фискального накопителя в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: FNCreationForm = FNCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fn-service')
    form: FNCreationForm = FNCreationForm()
    context: dict = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/services/add_fn.html', context)


@login_required
@staff_member_required
def delete_fn(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления фискального накопителя из системы.
        Доступен только администратору и суперпользователю. """
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
                     'service_type': 'fn', 'back_path': 'fn-service'}
    return render(request, 'accounting_system/services/delete_service.html', context)


# TO


@login_required
@staff_member_required
def to_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы со списком типов договоров технического
        обслуживания ККТ, внесенных в систему.
        Доступен только администратору и суперпользователю. """
    to_list = TO.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'to_list': to_list}
    return render(request, 'accounting_system/services/to_service.html', context)


@login_required
@staff_member_required
def add_to(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления договора технического обслуживания в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: TOCreationForm = TOCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('to-service')
    form: TOCreationForm = TOCreationForm()
    context: dict = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/services/add_to.html', context)


@login_required
@staff_member_required
def delete_to(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления договора технического обслуживания из системы.
        Доступен только администратору и суперпользователю. """
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
                     'service_type': 'to', 'back_path': 'to-service'}
    return render(request, 'accounting_system/services/delete_service.html', context)


# ECP


@login_required
@staff_member_required
def ecp_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы со списком ЭЦП внесенных в систему.
        Доступен только администратору и суперпользователю. """
    ecp_list = ECP.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'ecp_list': ecp_list}
    return render(request, 'accounting_system/services/ecp_service.html', context)


@login_required
@staff_member_required
def add_ecp(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления ЭЦП в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: ECPCreationForm = ECPCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ecp-service')
    form: ECPCreationForm = ECPCreationForm()
    context: dict = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/services/add_ecp.html', context)


@login_required
@staff_member_required
def delete_ecp(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления ЭЦП из системы.
        Доступен только администратору и суперпользователю. """
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
                     'service_type': 'ecp', 'back_path': 'ecp-service'}
    return render(request, 'accounting_system/services/delete_service.html', context)


# OFD


@login_required
@staff_member_required
def ofd_service(request: HttpRequest) -> HttpResponse:
    """ Контроллер страницы со списком доступных ОФД внесенных в систему.
        Доступен только администратору и суперпользователю. """
    ofd_list = OFD.objects.filter(active=True)
    context: dict = {'page': 'service', 'user': request.user, 'ofd_list': ofd_list}
    return render(request, 'accounting_system/services/ofd_service.html', context)


@login_required
@staff_member_required
def add_ofd(request: HttpRequest) -> HttpResponse:
    """ Контроллер добавления ОФД в систему.
        Доступен только администратору и суперпользователю. """
    if request.method == 'POST':
        form: OFDCreationForm = OFDCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ofd-service')
    form: OFDCreationForm = OFDCreationForm()
    context: dict = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/services/add_ofd.html', context)


@login_required
@staff_member_required
def delete_ofd(request: HttpRequest) -> HttpResponse:
    """ Контроллер удаления ОФД из системы.
        Доступен только администратору и суперпользователю. """
    service_pk: str = request.POST.get('service_pk')
    context: dict = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
                     'service_type': 'ofd', 'back_path': 'ofd-service'}
    return render(request, 'accounting_system/services/delete_service.html', context)
