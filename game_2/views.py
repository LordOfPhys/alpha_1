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
            UserProfile.objects.create(user = user, killer = user, target = user, room = UserProfile.objects.get(user = User.objects.filter(is_superuser=True)[0]).get_room())
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
    rooms = list(Room.objects.all())
    answer = []
    for i in range(len(rooms)):
        if rooms[i].get_room() != 'one_room' and rooms[i].get_status() != "1":
            answer.append(rooms[i].get_room())
    return HttpResponse(json.dumps({'rooms': answer}))

@csrf_exempt
def start_game(request):
    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user = Token.objects.get(key = data['token']).user)
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

    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user=Token.objects.get(key=data['token']).user)
    room = Room.objects.get(room = data['room_name'])
    if up.get_status() == '0':
        if getDistance(float(up.get_x()), float(up.get_y()), float(room.get_x_center()), float(room.get_y_center())) < 500000:
            room.add_user(up.get_user())
            up.set_room(room)
            up.set_status("1")
            return HttpResponse(json.dumps({'result': 'yes'}))
        else:
            return HttpResponse(json.dumps({'result': 'distance'}))
    else:
        return HttpResponse(json.dumps({'result': 'another_room'}))

@csrf_exempt
def exit_room(request):
    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user=Token.objects.get(key=data['token']).user)
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
    up.set_room(UserProfile.objects.get(user = User.objects.filter(is_superuser=True)[0]).get_room())
    up.set_status("0")
    return HttpResponse(json.dumps({'result': '1'}))


@csrf_exempt
def set_message(request):
    up = UserProfile.objects.get(user=Token.objects.get(key=request.META['HTTP_TOKEN']).user)
    up.set_message(json.loads(request.body.decode("utf-8"))['message'])

@csrf_exempt
def create_room(request):
    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user=Token.objects.get(key = data['token']).user)
    room = Room.objects.create(creator = up.get_user(), room=data['room_name'])
    up.set_room(room)
    up.set_status('1')
    room.set_status('0')
    room.set_x_center(str(data['lat']))
    room.set_y_center(str(data['lon']))
    room.add_user(up.get_user())
    return HttpResponse("Room created")

@csrf_exempt
def look_room(request):
    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user = Token.objects.get(key = data['token']).user)
    room = Room.objects.get(room=data["room_name"])
    room_len = len(list(room.get_users()))
    answer = {"room_len": room_len, "user_status": str(up.get_status()), "room_status": str(room.get_status())}
    return HttpResponse(json.dumps(answer))

@csrf_exempt
def look_room_yet(request):
    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user=Token.objects.get(key=data['token']).user)
    room = up.get_room();
    room_len = len(list(room.get_users()))
    answer = {"room_len": room_len, "user_status": str(up.get_status()), "room_status": str(room.get_status())}
    return HttpResponse(json.dumps(answer))

@csrf_exempt
def setLocation(request):
    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user=Token.objects.get(key=data['token']).user)
    up.set_x(str(data['lat']))
    up.set_y(str(data['lon']))
    return HttpResponse(json.dumps({"user_status": str(up.get_status())}))

@csrf_exempt
def getInfoPlay(request):
    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user = Token.objects.get(key = data['token']).user)
    up_killer = UserProfile.objects.get(user = up.get_killer())
    up_target = UserProfile.objects.get(user = up.get_target())
    room = up.get_room();
    answer = {"count_player": str(len(list(room.get_users()))), "killer_message": up_killer.get_message(), "target_message": up_target.get_message(),
              "killer_x": up_killer.get_x(), "killer_y": up_killer.get_y(), "target_x": up_target.get_x(), "target_y": up_target.get_y(),
              "user_status": up.get_status()}
    if int(len(list(room.get_users()))) == 1 and room.get_status() == "1":
        up.set_room(Room.objects.get(User.objects.filter(is_superuser=True)))
        Room.objects.get(room = room.get_room()).delete()
        up.set_status("0")
        up.set_target(up.get_user())
        up.set_killer(up.get_user())
        answer = {"count_player": str(len(list(room.get_users()))), "killer_message": up_killer.get_message(),
                  "target_message": up_target.get_message(),
                  "killer_x": up_killer.get_x(), "killer_y": up_killer.get_y(), "target_x": up_target.get_x(),
                  "target_y": up_target.get_y(),
                  "user_status": "win"}
        return HttpResponse(json.dumps(answer))
    return HttpResponse(json.dumps(answer))

@csrf_exempt
def sendMessage(request):
    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user = Token.objects.get(key = data['token']).user)
    up.set_message(data['message'])
    return HttpResponse({'result': '1'})

@csrf_exempt
def gameOver(request):
    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user = Token.objects.get(key = data['token']).user)
    room = up.get_room()
    len_room = len(list(room.get_users()))
    if len_room >= 3:
        up_killer = UserProfile.objects.get(user = up.get_killer)
        up_target = UserProfile.objects.get(user = up.get_target)
        up_killer.set_target(up_target.get_user())
        up_target.set_killer(up_killer.get_user())
        up.set_killer(up.get_user())
        up.set_target(up.get_user())
        up.set_status("0")
        up.set_room(Room.objects.get(creator = User.objects.filter(is_superuser = True)))
        room.delete_user(up.get_user())
    else:
        if len_room == 2:
            up.set_status("0")
            up.set_room(Room.objects.get(creator = User.objects.filter(is_superuser = True)))
            up.set_killer(up.get_user())
            up.set_target(up.get_user())
            up_killer = UserProfile.objects.get(user = up.get_killer())
            up_killer.set_target(up_killer.get_user())
            up_killer.set_killer(up_killer.get_user())
            room.delete_user(up.get_user())
    return HttpResponse(json.dumps({"result": "1"}))

@csrf_exempt
def kill_User(request):
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

    data = json.loads(request.body.decode("utf-8"))
    up = UserProfile.objects.get(user=Token.objects.get(key=data['token']).user)
    room = up.get_room()
    up_target = UserProfile.objects.get(user = up.get_target())
    up_new_target = UserProfile.objects.get(user = up_target.get_target())
    distance = (up.get_x(), up.get_y(), up_target.get_x(), up_target.get_y())
    if distance <= 500:
        up.set_target(up_target.get_target())
        up_target.set_killer(up_target.get_user())
        up_target.set_target(up_target.get_user())
        up_target.set_status("0")
        up_new_target.set_killer(up.get_user())
        room.delete_user(up_target.get_user())
        if len(list(room.get_users())) == 1:
            up.set_room(Room.objects.get(User.objects.filter(is_superuser=True)))
            Room.objects.get(room=room.get_room()).delete()
            up.set_status("0")
            up.set_target(up.get_user())
            up.set_killer(up.get_user())
            return HttpResponse(json.dumps({"result": "win"}))
        else:
            return HttpResponse(json.dumps({"result": "yes"}))
    else:
        return HttpResponse(json.dumps({"result": "no"}))