#- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.utils.safestring import mark_safe
from game_2.models import UserProfile, Room
import random
import json
import math

def index(request):
    return HttpResponse('200')

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        if User.objects.filter(username = data['login']).exists() is False:
            user = User.objects.create_user(data['login'], data['email'], data['password'])
            user.is_active=True
            user.save()
            UserProfile.objects.create(user = user, killer = user, target = user, room = UserProfile(user = User.objects.filter(is_superuser=True)).get_room())
            Token.objects.get_or_create(user = user)
            return HttpResponse(json.dumps({'token': user.auth_token.key}))
        else:
            return HttpResponse(json.dumps({'token': 'Bad boy'}))
    else:
        return HttpResponse('Выйди отседова')

@csrf_exempt
def log(request):
    if request.method == 'POST':
        data = request.body.decode("utf-8")
        result = json.loads(data)
        user = authenticate(username=result['login'], password=result['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                Token.objects.get_or_create(user = user)
                return HttpResponse(json.dumps({'token': user.auth_token.key}))
            else:
                return HttpResponse(json.dumps({'token': '-1'}))
        else:
            context_dict = {'token': '-1'}
            return HttpResponse(json.dumps(context_dict))
    else:
        return HttpResponse('Тебе тут не рады')

@csrf_exempt
def logout_view(request):
    if Token.objects.get(key = request.META['HTTP_TOKEN']).user is not None:
        up = UserProfile.objects.get(user = Token.objects.get(key = request.META['HTTP_TOKEN']).user)
        Token.objects.get(key = request.META['HTTP_TOKEN']).user.auth_token.delete()
        return HttpResponse(json.dumps({'token': '-1'}))
    else:
        return HttpResponse('Да закрой уже этот сервер')

@csrf_exempt
def main_view(request):
    return HttpResponse(json.dumps({'rooms': Room.objects.all()}))

@csrf_exempt
def start_game(request):
    up = UserProfile.objects.get(user = Token.objects.get(key = request.META['HTTP_TOKEN']).user)
    room = up.get_room()
    if room.get_creator() == up.get_user():
        array = list(room.get_users())
        random.shuffle(array)
        for i in range(1, len(array) - 1):
            UserProfile.objects.get(user=array[i]).set_target(array[i + 1])
            UserProfile.objects.get(user=array[i]).set_killer(array[i - 1])
        UserProfile.objects.get(user=array[0]).set_target(array[1])
        UserProfile.objects.get(user=array[0]).set_killer(array[len(array) - 1])
        UserProfile.objects.get(user=array[len(array) - 1]).set_killer(array[len(array) - 2])
        UserProfile.objects.get(user=array[len(array) - 1]).set_target(array[0])
        room.set_status("1")
        return HttpResponse(json.dumps({'result': 'yes'}))
    else:
        return HttpResponse(json.dumps({'result': '-1'}))

@csrf_exempt
def join_room(request):

    def deg2rad(deg):
        return deg * (math.pi / 180.0)

    def getDistance(x, y, x_center, y_center):
        R = 6371.0
        dLat = deg2rad(x_center - x)
        dLon = deg2rad(y_center - y)
        a = math.sin(dLat / 2.0) * math.sin(dLat / 2.0) + math.cos(deg2rad(x)) * math.cos(deg2rad(x_center)) * math.sin(
            dLon / 2.0) * math.sin(dLon / 2.0)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c * 1000
        return math.ceil(d)

    up = UserProfile.objects.get(user=Token.objects.get(key=request.META['HTTP_TOKEN']).user)
    room = json.loads(request.body.decode("utf-8"))['room']
    if up.get_status() == '0':
        if getDistance(up.get_x(), up.get_y(), room.get_x_center(), room.get_y_center()) < 500000:
            room.add_user(up.get_user())
            up.set_status("1")
        else:
            return HttpResponse(json.dumps({'result': 'distance'}))
    else:
        return HttpResponse(json.dumps({'result': 'another_room'}))

@csrf_exempt
def exit_room(request):
    up = UserProfile.objects.get(user=Token.objects.get(key=request.META['HTTP_TOKEN']).user)
    room = up.get_room()
    if up.get_user() == room.get_creator():
        if len(list(room.get_users())) > 1:
            room.delete_user(up.get_user())
            new_creator = list(room.get_users())[0]
            new_creator_up = UserProfile.objects.get(user=new_creator)
            room.set_creator(new_creator)
            room.set_y_center(new_creator_up.get_y())
            room.set_x_center(new_creator_up.get_x())
        else:
            room.delete_user(up.get_user())
            room.delete()
    else:
        room.delete_user(up.get_user())
    up.set_room(Room.objects.get(creator=User.objects.filter(is_superuser=True)))
    up.set_status("0")


@csrf_exempt
def set_message(request):
    up = UserProfile.objects.get(user=Token.objects.get(key=request.META['HTTP_TOKEN']).user)
    up.set_message(json.loads(request.body.decode("utf-8"))['message'])

@csrf_exempt
def create_room(request):
    up = UserProfile.objects.get(user=Token.objects.get(key=request.META['HTTP_TOKEN']).user)
    data = json.loads(request.body.decode("utf-8"))
    room = Room.objects.create(creator = up.get_user(), room=data['room_name'])
    room.set_status('0')
    room.set_x_center(up.get_x())
    room.set_y_center(up.get_y())
    room.add_user(up.get_user())
    return HttpResponse("Room created")
