from django.shortcuts import render
from django.http import HttpResponse
import json
import os

# Create your views here.

confirmation_token = 'd144b920'

def confirmation(request):
    if request.method == "POST":
        if request.POST['type'] == 'confirmation':
            return HttpResponse(confirmation_token)
        #data = request.body.decode('utf-8')
        #received_json_data = json.loads(data)
    #path = '/home/vktaxibot/vktaxibot/json.txt'
    #f = open(path, 'w')
    #.write('Hello, world!')
    return HttpResponse("No")
    

