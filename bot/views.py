# coding: utf8

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
import urllib.request
import urllib.parse
import json
import os
from .models import Order

# Create your views here.

confirmation_token = 'd144b920'
token = 'b87ef73d04d9f9eefae28697b2d27acaa21e862c382b8bc3af5bc0cf1aada1109aa46afd118777757abe5'

def index(request):
    return HttpResponse('Index')

def active_orders(request):
    if request.user.is_authenticated():
        result = []
        try:
            result = Order.objects.filter(active=True).order_by('date')
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
            result = Order.objects.filter(active=False).order_by('date')
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

def complete(request, pos):
    order =  get_object_or_404(Order, pos=pos)
    user_id = order.user_id
    message = 'Спасибо, Ваш заказ принят в обработку! Ожидайте ответа.'
    request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + str(message.encode('utf-8')) + '&access_token=' + token)
    resp = urllib.request.urlopen(request)
    order.active = False
    order.save()
    return HttpResponseRedirect(reverse('active_orders'))


@csrf_exempt
def bot(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        received_json_data = json.loads(data)
        if received_json_data['type'] == 'confirmation':
            return HttpResponse(confirmation_token)
        elif received_json_data['type'] == 'message_new':
            user_id = received_json_data['object']['user_id']
            input_message = received_json_data['object']['body']
            order = Order(user_id=user_id, message=input_message)
            order.save()
            output_message = 'Спасибо,%20Ваш%20заказ%20принят%20в%20обработку!%20Ожидайте%20ответа.'
            #data = urllib.parse.urlencode({'user_id': user_id, 'message': output_message, 'token': token}).encode()
            #request = urllib.request.Request('GET', 'https://api.vk.com/method/messages.send')
            request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + str(output_message.encode('utf-8')) + '&access_token=' + token)
            resp = urllib.request.urlopen(request)
            return HttpResponse('ok')

    return HttpResponse('ok')
    

