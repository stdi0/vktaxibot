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

            if input_message == 'отмена' or input_message == 'Отмена' or input_message == 'Отмен':
                orders = Order.objects.filter(user_id=user_id, active=True)
                if orders:
                    for order in orders:
                        order.active = False
                        order.save()
                    send_mail('Отмена заказа', 'Отмена заказа. http://vktaxibot.pythonanywhere.com/canceled_orders', settings.EMAIL_HOST_USER, ['vktaxibot@gmail.com'])
                output_message = 'Все активные заказы отменены. Спасибо.'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)
                return HttpResponse('ok')

            stage1 = Order.objects.filter(user_id=user_id, active=True, city=None)
            if stage1:
                #Проверка на пользовательское исключение
                if input_message.lower() == 'исключение':
                    stage1.city = stage1.tmp
                    stage1.save()
                    output_message = 'Заказ номер ' + order.id + ': Хорошо, чтобы продолжить, напишите адрес, откуда Вас забрать. Для отмены заказа, напишите слово \"отмена\"'
                    request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                    resp = urllib.request.urlopen(request)
                    return HttpResponse('ok')

                request = urllib.request.Request('http://kladr-api.ru/api.php?query=' + quote(input_message.strip()) + '&contentType=city&typeCode=1')
                resp = urllib.request.urlopen(request)
                resp = json.loads(resp.read().decode('utf-8'))
                if resp.get('result'):
                    stage1.city = input_message
                    stage1.save()

                    request = urllib.request.Request('http://kladr-api.ru/api.php?query=' + quote(stage1.city) + '&contentType=city&typeCode=1')
                    resp = urllib.request.urlopen(request)
                    resp = json.loads(resp.read().decode('utf-8'))
                    cityId = resp.get('result')[0]['id']

                    output_message = 'Заказ номер ' + order.id + ': Хорошо, чтобы продолжить, напишите адрес, откуда Вас забрать. Для отмены заказа, напишите слово \"отмена\"'
                else:
                    stage1.tmp = input_message
                    stage1.save()
                    output_message = 'Заказ номер ' + order.id + ': Извините, такой город не найден. Проверьте правильность написания. Если Вы уверены, что не ошиблись, напишите слово \"Исключение\". Для отмены заказа, напишите слово \"отмена\"'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)
                #Здесь проверяем является ли входящее сообщение нужным адресом
                return HttpResponse('ok')

            stage2 = Order.objects.filter(user_id=user_id, active=True, address_source=None)
            if stage2:
                #Проверка на пользовательское исключение
                if input_message.lower() == 'исключение':
                    stage2.address_source = stage2.tmp
                    stage2.save()
                    output_message = 'Заказ номер ' + order.id + ': Хорошо, чтобы продолжить, напишите адрес, куда Вы хотите поехать, если адресов несколько, перечислите их через точку с запятой. Для отмены заказа, напишите слово \"отмена\"'
                    request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                    resp = urllib.request.urlopen(request)
                    return HttpResponse('ok')
                #Распарсить адрес
                #pattern = re.compile('у*л*.*\s*\w*\s[\w/\\]*')
                result = re.sub(r'^у*л*и*ц*а*п*р*о*с*п*е*к*т*.?\s*', '', input_message.strip())
                result = re.sub(r',?\sд*о*м*с*т*р*о*е*н*и*е*.?\s*\d+.*$', '', result)

                request = urllib.request.Request('http://kladr-api.ru/api.php?query=' + quote(result) +'&contentType=street&cityId=' + cityId)
                resp = urllib.request.urlopen(request)
                resp = json.loads(resp.read().decode('utf-8'))
                if resp.get('result'):
                    stage2.address_source = input_message
                    stage2.save()
                    output_message = 'Заказ номер ' + order.id + ': Хорошо, чтобы продолжить, напишите адрес, куда Вы хотите поехать, если адресов несколько, перечислите их через точку с запятой. Для отмены заказа, напишите слово \"отмена\"'
                else:
                    stage2.tmp = input_message
                    stage2.save()
                    output_message = 'Заказ номер ' + order.id + ': Извините, такой адрес не найден. Проверьте правильность написания. Если Вы уверены, что не ошиблись, напишите слово \"Исключение\". Для отмены заказа, напишите слово \"отмена\"'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)
                #Здесь проверяем является ли входящее сообщение нужным адресом
                return HttpResponse('ok')

            stage3 = Order.objects.filter(user_id=user_id, active=True, address_destination=None)
            if stage3:
                #Здесь проверяем является ли входящее сообщение нужным адресом
                #result = re.sub(r'^у*л*и*ц*а*п*р*о*с*п*е*к*т*.?\s*', '', input_message.strip())
                if input_message.lower() == 'исключение':
                    stage3.address_destination = stage3.tmp
                    stage3.save()
                    output_message = 'Заказ номер ' + order.id + ': Спасибо, Ваш заказ принят в обработку! Ожидайте ответа. Для отмены заказа, напишите слово \"отмена\"'
                    request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                    resp = urllib.request.urlopen(request)
                    return HttpResponse('ok')

                addresses = re.split(r';', input_message.strip())
                for address in addresses:
                    result = re.sub(r'^у*л*и*ц*а*п*р*о*с*п*е*к*т*.?\s*', '', input_message.strip())
                    result = re.sub(r',?\sд*о*м*с*т*р*о*е*н*и*е*.?\s*\d+.*$', '', result)

                    request = urllib.request.Request('http://kladr-api.ru/api.php?query=' + quote(result) +'&contentType=street&cityId=' + cityId)
                    resp = urllib.request.urlopen(request)
                    resp = json.loads(resp.read().decode('utf-8'))

                    if not resp.get('result'):
                        output_message = 'Заказ номер ' + order.id + ': Извините, адрес(а) не найден(ы). Проверьте правильность написания. Если Вы уверены, что не ошиблись, напишите слово \"Исключение\". Для отмены заказа, напишите слово \"отмена\"'
                        request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                        resp = urllib.request.urlopen(request)
                        return HttpResponse('ok')

                stage3.address_destination = input_message
                output_message = 'Заказ номер ' + order.id + ': Спасибо, Ваш заказ принят в обработку! Ожидайте ответа. Для отмены заказа, напишите слово \"отмена\"'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)
                send_mail('Новый заказ', 'Создан новый заказ! http://vktaxibot.pythonanywhere.com/active_orders', settings.EMAIL_HOST_USER, ['vktaxibot@gmail.com'])

                return HttpResponse('ok')

            if input_message.lower() == 'такси':
                #Снимаем активность со старых заказов
                old_orders = Order.objects.filter(user_id=user_id, active=True)
                if old_orders:
                    for order in old_olders:
                        order.active = False
                        order.save()

                order = Order(user_id=user_id, active=True)
                order.save()
                output_message = 'Вашему заказу присвоен номер ' + order.id + '. Чтобы продолжить, напишите свой город. Для отмены, напишите слово \"отмена\"'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)

                return HttpResponse('ok')
            else:
                output_message = 'Для заказа машины, напишите слово \"Такси\"'
                request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + quote(output_message) + '&access_token=' + token)
                resp = urllib.request.urlopen(request)

                return HttpResponse('ok')

    return HttpResponse('ok')
    

