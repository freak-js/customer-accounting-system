from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


@login_required
def clients(request):
    return render(request, 'accounting_system/clients.html')


@login_required
def staff(request):
    return render(request, 'accounting_system/staff.html')


@login_required
def auth(request):
    return render(request, 'accounting_system/auth.html', {'form': AuthenticationForm})


def logout_view(request):
    logout(request)
    return redirect('login')