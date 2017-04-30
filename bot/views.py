# coding: utf8

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import urllib.request
import urllib.parse
import json
import os
import re
from .models import Order
from urllib.parse import quote

# Create your views here.

confirmation_token = 'd144b920'
token = 'b87ef73d04d9f9eefae28697b2d27acaa21e862c382b8bc3af5bc0cf1aada1109aa46afd118777757abe5'
group_id = '145824671'

def index(request):
    #context = {'result': result}
    if request.user.is_authenticated():
        return render(request, 'bot/index.html')
    return HttpResponseRedirect(reverse('login'))

def active_orders(request):
    if request.user.is_authenticated():
        result = []
        try:
            result = Order.objects.filter(status=1).order_by('date')
            for pos, order in enumerate(result):
                order.pos = pos + 1
                order.save()
            paginator = Paginator(result, 50)
            page = request.GET.get('page')
            try:
                result = paginator.page(page)
            except PageNotAnInteger:
                result = paginator.page(1)
            except EmptyPage:
                result = paginator.page(paginator.num_pages)
        except:
            pass
        context = {'result': result}
        return render(request, 'bot/active_orders.html', context)
    return HttpResponseRedirect(reverse('login'))

def completed_orders(request):
    if request.user.is_authenticated():
        result = []
        try:
            result = Order.objects.filter(status=0).order_by('date')
            for pos, order in enumerate(result):
                order.pos = pos + 1
                order.save()
            paginator = Paginator(result, 50)
            page = request.GET.get('page')
            try:
                result = paginator.page(page)
            except PageNotAnInteger:
                result = paginator.page(1)
            except EmptyPage:
                result = paginator.page(paginator.num_pages)
        except:
            pass
        context = {'result': result}
        return render(request, 'bot/completed_orders.html', context)
    return HttpResponseRedirect(reverse('login'))

def canceled_orders(request):
    if request.user.is_authenticated():
        result = []
        try:
            result = Order.objects.filter(status=2).order_by('date')
            for pos, order in enumerate(result):
                order.pos = pos + 1
                order.save()
            paginator = Paginator(result, 50)
            page = request.GET.get('page')
            try:
                result = paginator.page(page)
            except PageNotAnInteger:
                result = paginator.page(1)
            except EmptyPage:
                result = paginator.page(paginator.num_pages)
        except:
            pass
        context = {'result': result}
        return render(request, 'bot/canceled_orders.html', context)
    return HttpResponseRedirect(reverse('login'))

def complete(request):
    cost = request.GET['cost']
    order_id = request.GET['id']
    order =  get_object_or_404(Order, id=int(order_id))
    user_id = order.user_id
    message = 'Ваш заказ направлен водителям. Стоимость по Вашему заказу составит ' + cost + ' руб. Ожидайте звонка или смс. Для отмены заказа напишите \"отмена\".'
    request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(message) + '&access_token=' + token)
    resp = urllib.request.urlopen(request)
    order.status = 0
    order.save()
    return HttpResponseRedirect(reverse('active_orders'))

def cancel(request, id):
    order =  get_object_or_404(Order, id=id)
    user_id = order.user_id
    message = 'Ваш заказ не может быть обработан. Проверьте корректность указанной Вами информации.'
    request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(message) + '&access_token=' + token)
    resp = urllib.request.urlopen(request)   
    order.status = 3
    order.save() 
    return HttpResponseRedirect(reverse('active_orders'))


@csrf_exempt
def bot(request):
    req = urllib.request.Request('http://kladr-api.ru/api.php?query=Murmansk&contentType=city&typeCode=1&token=5904d4ee0a69de0b798b4570')
    resp = urllib.request.urlopen(req)
    return HttpResponse('ok')
    

