from django.shortcuts import render


# Ручки-рендеры

def welcome(request):
    return render(request, 'accounting_system/welcome.html')

def auth(request):
    return render(request, 'accounting_system/auth.html')