from django.shortcuts import render_to_response

from .models import State


def index(request):
    return render_to_response('app/base.html', {'states': State.all()})
