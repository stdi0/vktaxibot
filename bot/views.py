from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import urllib.request
import urllib.parse
import json
import os
from .models import Order

# Create your views here.

confirmation_token = 'd144b920'
token = 'b87ef73d04d9f9eefae28697b2d27acaa21e862c382b8bc3af5bc0cf1aada1109aa46afd118777757abe5'

@csrf_exempt
def index(request):
    #text = "No"
    if request.method == "POST":
    #    text = "Yes"
        #if request.POST['type'] == 'confirmation':
        #   return HttpResponse(confirmation_token)
    #try:
    #    data = request.body.decode('utf-8')
    #    received_json_data = json.loads(data)
    #except:
    #    pass
    #try:
    #    received_json_data = request.body.decode('utf-8')
    #except:
    #    received_json_data = 'Empty'
        data = request.body.decode('utf-8')
        received_json_data = json.loads(data)
        #if received_json_data['type'] = 'confirmation':
        #    return HttpResponse(confirmation_token)
        #path = '/home/vktaxibot/vktaxibot/json.txt'
        #f = open(path, 'w')
        #f.write(received_json_data['type'])
        if received_json_data['type'] == 'confirmation':
            return HttpResponse(confirmation_token)
        elif received_json_data['type'] == 'message_new':
            user_id = received_json_data['object']['user_id']
            input_message = received_json_data['object']['body']
            order = Order(user_id=user_id, message=input_message)
            order.save()
            #path = '/home/vktaxibot/vktaxibot/json.txt'
            #f = open(path, 'w')
            #f.write(str(user_id))
            output_message = 'Hi'
            request = urllib.request.Request('https://api.vk.com/method/messages.send?user_id=' + str(user_id) + '&message=' + output_message + '&access_token=' + token)
            resp = urllib.request.urlopen(request)
            return HttpResponse('ok')

        #path = '/home/vktaxibot/vktaxibot/json.txt'
        #f = open(path, 'w')
        #f.write(data)
    #else:
    #    path = '/home/vktaxibot/vktaxibot/json.txt'
    #    f = open(path, 'w')
    #    f.write('No')
    return HttpResponse('ok')
    

