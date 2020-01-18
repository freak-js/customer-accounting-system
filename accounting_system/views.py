from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from .forms import CustomUserCreationForm, UserChangeForm
from .models import Manager, Client


@login_required
def auth(request):
    """"""
    return render(request, 'accounting_system/auth.html', {'form': AuthenticationForm})


@login_required
def clients(request):
    if request.user.is_staff:
        clients = Client.objects.all().filter(active=True)[:5][::-1]
    else:
        clients = request.user.get_clients().filter(active=True)[:5][::-1]
    context = {'page': 'clients', 'manager_name': str(request.user), 'user': request.user, 'clients': clients}
    return render(request, 'accounting_system/clients.html', context)


@login_required
def add_client(request):
    if request.method == 'POST':
        if Client.save_client(request.POST):
            return redirect('clients')
    managers = Manager.objects.all().filter(is_active=True)
    context = {'page': 'clients', 'manager_name': str(request.user), 'user': request.user, 'managers': managers}
    return render(request, 'accounting_system/add_client.html', context)


@login_required
def delete_client(request):
    if client_pk := request.POST.get('client_pk_for_delete'):
        client = get_object_or_404(Client, pk=client_pk)
        client.kill()
        return redirect('clients')
    client_pk = request.POST.get('client_pk')
    client = get_object_or_404(Manager, pk=client_pk)
    context = {'page': 'clients', 'manager_name': str(request.user), 'client': client, 'user': request.user}
    return render(request, 'accounting_system/delete_client.html', context)


@login_required
def staff(request):
    managers = Manager.objects.all().filter(is_active=True)
    context = {'page': 'staff', 'manager_name': str(request.user), 'managers': managers, 'user': request.user}
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
    context = {'page': 'staff', 'manager_name': str(request.user), 'form': form, 'user': request.user}
    return render(request, 'accounting_system/add_manager.html', context)


@login_required
@staff_member_required
def change_manager_form(request):
    change_manager_pk = request.POST.get('manager_pk')
    change_manager = get_object_or_404(Manager, pk=change_manager_pk)
    form = UserChangeForm(instance=change_manager)
    context = {'page': 'staff', 'manager_name': str(request.user), 'form': form,
               'user': request.user, 'change_manager': change_manager}
    return render(request, 'accounting_system/change_manager.html', context)


@login_required
@require_POST
@staff_member_required
def change_manager(request):
    manager_pk_for_change = request.POST.get('manager_pk_for_change')
    change_manager = get_object_or_404(Manager, pk=manager_pk_for_change)
    form = UserChangeForm(request.POST, instance=change_manager)
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
    context = {'page': 'staff', 'manager_name': str(request.user), 'user': request.user, 'manager': manager}
    return render(request, 'accounting_system/delete_manager.html', context)


@login_required
def tasks(request):
    context = {'page': 'tasks', 'manager_name': str(request.user), 'user': request.user}
    return render(request, 'accounting_system/tasks.html', context)


@login_required
def calendar(request):
    context = {'page': 'calendar', 'manager_name': str(request.user), 'user': request.user}
    return render(request, 'accounting_system/calendar.html', context)


@login_required
def service(request):
    context = {'page': 'service', 'manager_name': str(request.user), 'user': request.user}
    return render(request, 'accounting_system/service.html', context)


# NOT RENDER VIEWS


def logout_view(request):
    logout(request)
    return redirect('login')
