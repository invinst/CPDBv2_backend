from django.shortcuts import render


def index(request, path=None):
    return render(request, '/www/static/index.html')
