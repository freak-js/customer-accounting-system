from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import CustomUserCreationForm


@login_required
def auth(request):
    return render(request, 'accounting_system/auth.html', {'form': AuthenticationForm})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def clients(request):
    return render(request, 'accounting_system/clients.html', {'page': 'clients'})


@login_required
def staff(request):
    return render(request, 'accounting_system/staff.html', {'page': 'staff'})


@login_required
def add_manager(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff')
    else:
        form = CustomUserCreationForm
    return render(request, 'accounting_system/add_manager.html', {'form': form})
