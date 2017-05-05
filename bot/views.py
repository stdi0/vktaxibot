# coding: utf8

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import requests
import json
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
API_KEY = '76150e77f594d464ca0f2f580c9b7250e50295ec'
BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/%s'

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
    message = 'Заказ номер ' + order_id + ' направлен водителям. Стоимость по данному заказу составит ' + cost + ' руб. Ожидайте звонка или смс. Для отмены заказа напишите \"отмена\" и номер заказа.'
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
    order.status = 2
    order.save() 
    return HttpResponseRedirect(reverse('active_orders'))

def suggest(query, resource):
    url = BASE_URL % resource
    headers = { 
        'Authorization': 'Token %s' % API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        'query': query
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r.json()

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

            request = urllib.request.Request('https://api.vk.com/method/groups.isMember?group_id=' + str(group_id) + '&user_id=' + str(user_id))
            resp = urllib.request.urlopen(request)
            resp = json.loads(resp.read().decode('utf-8'))
            
            if resp.get('response') == 0:
                output_message = 'Прежде чем начать пользоваться VK Taxi, необходимо подписаться: http://vk.com/vktaxibot' 
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)
                return HttpResponse('ok')

            match = re.findall(r'отмена\s(\d*)', input_message.lower())
            if match: 
                order = Order.objects.get(user_id=user_id, id=match[0])
                order.active = False
                order.status = 2
                order.save()
                send_mail('Отмена заказа ' + str(order.id), 'Отмена заказа номер ' + str(order.id) +'. http://vktaxibot.pythonanywhere.com/canceled_orders', settings.EMAIL_HOST_USER, ['vktaxibot@gmail.com'])
                output_message = 'Заказ номер ' + str(order.id) + ' отменен. Спасибо.'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)
                return HttpResponse('ok')

            stage1 = Order.objects.filter(user_id=user_id, active=True, city=None)
            if stage1:
                #Проверка на пользовательское исключение
                if input_message.lower() == 'исключение':
                    stage1[0].city = stage1[0].tmp
                    stage1[0].save()
                    output_message = 'Заказ номер ' + str(stage1[0].id) + ': Хорошо, чтобы продолжить, напишите свой номер телефона. Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                    request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                    resp = urllib.request.urlopen(request)
                    return HttpResponse('ok')

                result = suggest(input_message, 'address')

                for i in result.get('suggestions'):
                    input_message = re.sub('^.*\s', '', input_message.strip())
                    if str(i['data']['city']).lower() == input_message.lower():
                        stage1[0].city = input_message
                        stage1[0].save()
                        output_message = 'Заказ номер ' + str(stage1[0].id) + ': Хорошо, чтобы продолжить, напишите свой номер телефона. Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                        break
                else:
                    stage1[0].tmp = input_message
                    stage1[0].save()
                    output_message = 'Заказ номер ' + str(stage1[0].id) + ': Извините, такой город не найден. Проверьте правильность написания. Если Вы уверены, что не ошиблись, напишите слово \"Исключение\". Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)
                #Здесь проверяем является ли входящее сообщение нужным адресом
                return HttpResponse('ok')

            stage2 = Order.objects.filter(user_id=user_id, active=True, phone=None)
            if stage2:
                
                stage2.phone = input_message
                stage2.save()

                output_message = 'Заказ номер ' + str(stage2[0].id) + ': Хорошо, чтобы продолжить, напишите адрес, откуда Вас забрать. Для отмены заказа, напишите слово \"отмена\" и номер заказа.'

                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)
                return HttpResponse('ok')    

            stage3 = Order.objects.filter(user_id=user_id, active=True, address_source=None)
            if stage2:
                #Проверка на пользовательское исключение
                if input_message.lower() == 'исключение':
                    stage3[0].address_source = stage3[0].tmp
                    stage3[0].save()
                    output_message = 'Заказ номер ' + str(stage3[0].id) + ': Хорошо, чтобы продолжить, напишите адрес, куда Вы хотите поехать, если адресов несколько, перечислите их через точку с запятой. Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                    request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                    resp = urllib.request.urlopen(request)
                    return HttpResponse('ok')

                house_num = re.findall(r'\s\d+.*$', input_message)
                if not house_num:
                    output_message = 'Заказ номер ' + str(stage3[0].id) + ': Ошибка, Вы не указали номер дома. Повторите ввод адреса. Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                    request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                    resp = urllib.request.urlopen(request)
                    return HttpResponse('ok')
                #Распарсить адрес
                #pattern = re.compile('у*л*.*\s*\w*\s[\w/\\]*')

                result = suggest(stage3[0].city + ' ' + input_message, 'address')
                for i in result.get('suggestions'):
                    if i['data']['street'] is not None:
                        stage3[0].address_source = input_message
                        stage3[0].save()
                        output_message = 'Заказ номер ' + str(stage3[0].id) + ': Хорошо, чтобы продолжить, напишите адрес, куда Вы хотите поехать, если адресов несколько, перечислите их через точку с запятой. Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                        break
                else:
                    stage3[0].tmp = input_message
                    stage3[0].save()
                    output_message = 'Заказ номер ' + str(stage3[0].id) + ': Извините, такой адрес не найден. Проверьте правильность написания. Если Вы уверены, что не ошиблись, напишите слово \"Исключение\". Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)
                #Здесь проверяем является ли входящее сообщение нужным адресом
                return HttpResponse('ok')

            stage4 = Order.objects.filter(user_id=user_id, active=True, address_destination=None)
            if stage3:
                #Здесь проверяем является ли входящее сообщение нужным адресом
                #result = re.sub(r'^у*л*и*ц*а*п*р*о*с*п*е*к*т*.?\s*', '', input_message.strip())
                if input_message.lower() == 'исключение':
                    stage4[0].address_destination = stage4[0].tmp
                    stage4[0].save()
                    output_message = 'Заказ номер ' + str(stage4[0].id) + ': Спасибо, Ваш заказ принят в обработку! Ожидайте ответа. Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                    request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                    resp = urllib.request.urlopen(request)
                    return HttpResponse('ok')

                addresses = re.split(r';', input_message.strip())
                for address in addresses:

                    house_num = re.findall(r'\s\d+.*$', address)
                    if not house_num:
                        output_message = 'Заказ номер ' + str(stage4[0].id) + ': Ошибка, Вы не указали номер дома в адресе(ах). Повторите ввод адреса(ов). Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                        request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                        resp = urllib.request.urlopen(request)
                        return HttpResponse('ok')

                    result = suggest(stage4[0].city + ' ' + address, 'address')
                    for i in result.get('suggestions'):
                        if i['data']['street'] is not None:
                            stage4[0].address_destination = input_message
                            stage4[0].active = False
                            stage4[0].save()
                            output_message = 'Заказ номер ' + str(stage4[0].id) + ': Спасибо, Ваш заказ принят в обработку! Ожидайте ответа. Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                            request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                            resp = urllib.request.urlopen(request)
                            send_mail('Новый заказ', 'Создан новый заказ! http://vktaxibot.pythonanywhere.com/active_orders', settings.EMAIL_HOST_USER, ['vktaxibot@gmail.com'])
                            return HttpResponse('ok')
                
                output_message = 'Заказ номер ' + str(stage4[0].id) + ': Извините, адрес(а) не найден(ы). Проверьте правильность написания. Если Вы уверены, что не ошиблись, напишите слово \"Исключение\". Для отмены заказа, напишите слово \"отмена\" и номер заказа.'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)
                return HttpResponse('ok')

                

            if input_message.lower() == 'такси':
                #Снимаем активность со старых заказов
                old_orders = Order.objects.filter(user_id=user_id, active=True)
                if old_orders:
                    for order in old_orders:
                        order.active = False
                        order.save()

                order = Order(user_id=user_id, active=True)
                order.save()
                output_message = 'Вашему заказу присвоен номер ' + str(order.id) + '. Чтобы продолжить, напишите свой город. Для отмены, напишите слово \"отмена\"'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)

                return HttpResponse('ok')
            else:
                output_message = 'Для заказа машины, напишите слово \"Такси\"'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)

                return HttpResponse('ok')
    

