from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from .utils import get_service_class_instance, create_service_for_client
from .forms import (CustomUserCreationForm, ManagerChangeForm, CashMachineCreationForm, FNCreationForm,
                    TOCreationForm, ECPCreationForm, OFDCreationForm)
from .models import Manager, Client, CashMachine, ECP, OFD, FN, TO


@login_required
def auth(request):
    """"""
    return render(request, 'accounting_system/auth.html', {'form': AuthenticationForm})


# CLIENTS


@login_required
def clients(request):
    if request.user.is_staff:
        clients = Client.objects.filter(active=True)[::-1][:7]
        clients_list = [client.organization_name for client in clients]
    else:
        clients = request.user.get_clients().filter(active=True)[::-1][:7]
        clients_list = [client.organization_name for client in clients]
    context = {'page': 'clients', 'user': request.user, 'clients': clients, 'clients_list': str(clients_list)}
    return render(request, 'accounting_system/clients.html', context)


@login_required
def filter_clients(request):
    organization_name = request.POST.get('search_data')
    if request.user.is_staff:
        clients = Client.objects.filter(organization_name=organization_name)
        not_filter_clients = Client.objects.filter(active=True)
        clients_list = [client.organization_name for client in not_filter_clients]
    else:
        clients = request.user.get_clients().filter(organization_name=organization_name)
        not_filter_clients = request.user.get_clients().filter(active=True)
        clients_list = [client.organization_name for client in not_filter_clients]
    context = {'page': 'clients', 'user': request.user, 'clients': clients, 'clients_list': str(clients_list)}
    return render(request, 'accounting_system/clients.html', context)


@login_required
def add_client(request):
    if request.method == 'POST':
        if Client.save_client(request.POST):
            return redirect('clients')
        # TODO Добавить выведение ошибки при сохранении клиента (экран уведомлений)
    managers = Manager.objects.all().filter(is_active=True)
    context = {'page': 'clients', 'user': request.user, 'managers': managers}
    return render(request, 'accounting_system/add_client.html', context)


@login_required
def delete_client(request):
    if client_pk := request.POST.get('client_pk_for_delete'):
        client = get_object_or_404(Client, pk=client_pk)
        client.kill()
        return redirect('clients')
    client_pk = request.POST.get('client_pk')
    client = get_object_or_404(Manager, pk=client_pk)
    context = {'page': 'clients', 'client': client, 'user': request.user}
    return render(request, 'accounting_system/delete_client.html', context)


@login_required
def client_profile(request):
    client_pk = request.POST.get('client_pk')
    client = get_object_or_404(Client, pk=client_pk)
    client_services = client.get_services()
    context = {'page': 'clients', 'client': client, 'user': request.user, 'client_services': client_services}
    return render(request, 'accounting_system/client_profile.html', context)


# STAFF


@login_required
def staff(request):
    managers = Manager.objects.all().filter(is_active=True)
    context = {'page': 'staff', 'managers': managers, 'user': request.user}
    return render(request, 'accounting_system/staff.html', context)


@login_required
@staff_member_required
def add_manager(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff')
    else:
        form = CustomUserCreationForm
    context = {'page': 'staff', 'form': form, 'user': request.user}
    return render(request, 'accounting_system/add_manager.html', context)


@login_required
@staff_member_required
def change_manager_form(request):
    change_manager_pk = request.POST.get('manager_pk')
    change_manager = get_object_or_404(Manager, pk=change_manager_pk)
    form = ManagerChangeForm(instance=change_manager)
    context = {'page': 'staff', 'form': form, 'user': request.user, 'change_manager': change_manager}
    return render(request, 'accounting_system/change_manager.html', context)


@login_required
@require_POST
@staff_member_required
def change_manager(request):
    manager_pk_for_change = request.POST.get('manager_pk_for_change')
    manager = get_object_or_404(Manager, pk=manager_pk_for_change)
    form = ManagerChangeForm(request.POST, instance=manager)
    if form.is_valid():
        form.save()
        return redirect('staff')


@login_required
@staff_member_required
def delete_manager(request):
    if manager_pk := request.POST.get('manager_pk_for_delete'):
        manager = get_object_or_404(Manager, pk=manager_pk)
        manager.kill()
        return redirect('staff')
    manager_pk = request.POST.get('manager_pk')
    manager = get_object_or_404(Manager, pk=manager_pk)
    context = {'page': 'staff', 'user': request.user, 'manager': manager}
    return render(request, 'accounting_system/delete_manager.html', context)


# TASKS


@login_required
def tasks(request):
    context = {'page': 'tasks', 'user': request.user}
    return render(request, 'accounting_system/tasks.html', context)


# CALENDAR


@login_required
def calendar(request):
    context = {'page': 'calendar', 'user': request.user}
    return render(request, 'accounting_system/calendar.html', context)


# SERVICE


@login_required
@staff_member_required
def service(request):
    context = {'page': 'service', 'user': request.user}
    return render(request, 'accounting_system/service.html', context)


@login_required
@require_POST
def add_service_for_client_form(request):
    client_pk = request.POST.get('client_pk')
    kkt_list = CashMachine.objects.all().filter(active=True)
    ecp_list = ECP.objects.all().filter(active=True)
    ofd_list = OFD.objects.all().filter(active=True)
    fn_list = FN.objects.all().filter(active=True)
    to_list = TO.objects.all().filter(active=True)
    context = {'page': 'service', 'user': request.user, 'client_pk': client_pk,
               'kkt_list': kkt_list, 'ecp_list': ecp_list, 'ofd_list': ofd_list,
               'fn_list': fn_list, 'to_list': to_list}
    return render(request, 'accounting_system/add_service_for_client.html', context)


@login_required
@require_POST
def add_service_for_client(request):
    create_service_for_client(request)
    return redirect('clients')


# KKT


@login_required
@staff_member_required
def kkt_service(request):
    kkt_list = CashMachine.objects.all().filter(active=True)
    context = {'page': 'service', 'user': request.user, 'kkt_list': kkt_list}
    return render(request, 'accounting_system/kkt_service.html', context)


@login_required
@staff_member_required
def add_kkt(request):
    if request.method == 'POST':
        form = CashMachineCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kkt-service')
    form = CashMachineCreationForm
    context = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/add_kkt.html', context)


@login_required
@staff_member_required
def delete_kkt(request):
    service_pk = request.POST.get('service_pk')
    context = {'page': 'service', 'user': request.user,
               'service_pk': service_pk, 'service_type': 'kkt', 'back_path': 'kkt-service'}
    return render(request, 'accounting_system/delete_service.html', context)


# FN


@login_required
@staff_member_required
def fn_service(request):
    fn_list = FN.objects.all().filter(active=True)
    context = {'page': 'service', 'user': request.user, 'fn_list': fn_list}
    return render(request, 'accounting_system/fn_service.html', context)


@login_required
@staff_member_required
def add_fn(request):
    if request.method == 'POST':
        form = FNCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fn-service')
    form = FNCreationForm
    context = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/add_fn.html', context)


@login_required
@staff_member_required
def delete_fn(request):
    service_pk = request.POST.get('service_pk')
    context = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
               'service_type': 'fn', 'back_path': 'fn-service'}
    return render(request, 'accounting_system/delete_service.html', context)


# TO


@login_required
@staff_member_required
def to_service(request):
    to_list = TO.objects.all().filter(active=True)
    context = {'page': 'service', 'user': request.user, 'to_list': to_list}
    return render(request, 'accounting_system/to_service.html', context)


@login_required
@staff_member_required
def add_to(request):
    if request.method == 'POST':
        form = TOCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('to-service')
    form = TOCreationForm
    context = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/add_to.html', context)


@login_required
@staff_member_required
def delete_to(request):
    service_pk = request.POST.get('service_pk')
    context = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
               'service_type': 'to', 'back_path': 'to-service'}
    return render(request, 'accounting_system/delete_service.html', context)


# ECP


@login_required
@staff_member_required
def ecp_service(request):
    ecp_list = ECP.objects.all().filter(active=True)
    context = {'page': 'service', 'user': request.user, 'ecp_list': ecp_list}
    return render(request, 'accounting_system/ecp_service.html', context)


@login_required
@staff_member_required
def add_ecp(request):
    if request.method == 'POST':
        form = ECPCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ecp-service')
    form = ECPCreationForm
    context = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/add_ecp.html', context)


@login_required
@staff_member_required
def delete_ecp(request):
    service_pk = request.POST.get('service_pk')
    context = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
               'service_type': 'ecp', 'back_path': 'ecp-service'}
    return render(request, 'accounting_system/delete_service.html', context)


# OFD


@login_required
@staff_member_required
def ofd_service(request):
    ofd_list = OFD.objects.all().filter(active=True)
    context = {'page': 'service', 'user': request.user, 'ofd_list': ofd_list}
    return render(request, 'accounting_system/ofd_service.html', context)


@login_required
@staff_member_required
def add_ofd(request):
    if request.method == 'POST':
        form = OFDCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ofd-service')
    form = OFDCreationForm
    context = {'page': 'service', 'user': request.user, 'form': form}
    return render(request, 'accounting_system/add_ofd.html', context)


@login_required
@staff_member_required
def delete_ofd(request):
    service_pk = request.POST.get('service_pk')
    context = {'page': 'service', 'user': request.user, 'service_pk': service_pk,
               'service_type': 'ofd', 'back_path': 'ofd-service'}
    return render(request, 'accounting_system/delete_service.html', context)


# NOT RENDER VIEWS


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@require_POST
@staff_member_required
def delete_service(request):
    back_path = request.POST.get('back_path')
    service_pk = request.POST.get('service_pk')
    service_class_instance = get_service_class_instance(request)
    service = get_object_or_404(service_class_instance, pk=service_pk)
    service.kill()
    return redirect(back_path)
