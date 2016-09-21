from django.shortcuts import render


def index(request, path=None):
    return render(request, '/var/www/index.html')
