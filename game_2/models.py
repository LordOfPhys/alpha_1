# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class Room(models.Model):
    room = models.CharField(max_length=100, default='', unique=True)
    creator = models.OneToOneField(User, unique=True, verbose_name='room_creator', related_name='room_creator', on_delete=models.CASCADE, default='')
    users = models.ManyToManyField(User, blank=True)
    x_center = models.CharField(max_length=100, default='0')
    y_center = models.CharField(max_length=100, default='0')
    status = models.CharField(max_length=100, default='0')

    def get_room(self):
        return self.room

    def get_x_center(self):
        return self.x_center

    def set_x_center(self, x):
        self.x_center = x
        self.save()

    def get_y_center(self):
        return self.y_center

    def set_y_center(self, y):
        self.y_center = y
        self.save()

    def set_creator(self, creator):
        self.creator = creator
        self.save()

    def get_creator(self):
        return self.creator

    def set_status(self, status):
        self.status = status
        self.save()

    def get_users(self):
        return self.users.all()

    def get_status(self):
        return self.status

    def add_user(self, user):
        self.users.add(user)
        self.save()

    def delete_user(self, user):
        self.users.remove(user)
        self.save()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, verbose_name='user_profile', related_name='user_profile', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, verbose_name='user_room', related_name='user_room', on_delete=models.CASCADE, default='')
    target = models.ForeignKey(User, verbose_name='target', on_delete=models.CASCADE, related_name='target', default='')
    killer = models.ForeignKey(User, verbose_name='killer', on_delete=models.CASCADE, related_name='killer', default='')
    x = models.CharField(max_length=100, default='0')
    y = models.CharField(max_length=100, default='0')
    status = models.CharField(max_length=100, default='0')
    message = models.CharField(max_length=1000, default='Я здесь...')

    def set_message(self, message):
        self.message = message
        self.save()

    def get_message(self):
        return self.message

    def get_user(self):
        return self.user

    def get_status(self):
        return self.status

    def set_room(self, room):
        self.room = room
        self.save()

    def get_room(self):
        return self.room

    def set_status(self, status):
        self.status = status
        self.save()

    def set_target(self, target):
        self.target = target
        self.save()

    def get_target(self):
        return self.target

    def set_killer(self, killer):
        self.killer = killer
        self.save()

    def get_killer(self):
        return self.killer

    def set_x(self, x):
        self.x = x
        self.save()

    def set_y(self, y):
        self.y = y
        self.save()

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y