from django.shortcuts import render, redirect, reverse
from django.views.decorators.clickjacking import xframe_options_exempt

from data.models import OfficerAlias


def index_view(request, path=None):
    return render(request, 'index.html')


@xframe_options_exempt
def embed_view(request, path=None):
    return render(request, 'index.html')


def officer_view(request, officer_id=None, slug=None):
    try:
        alias = OfficerAlias.objects.get(old_officer_id=officer_id)
        return redirect(
            reverse(
                'officer',
                kwargs={'officer_id': alias.new_officer_id, 'slug': '' if slug is None else slug}
            ),
            permanent=True
        )
    except OfficerAlias.DoesNotExist:
        pass

    return render(request, 'index.html')


def complaint_view(request, crid=None, officer_id=None):
    try:
        alias = OfficerAlias.objects.get(old_officer_id=officer_id)
        return redirect(
            reverse('complaint', kwargs={'officer_id': alias.new_officer_id, 'crid': crid}),
            permanent=True
        )
    except OfficerAlias.DoesNotExist:
        pass

    return render(request, 'index.html')
