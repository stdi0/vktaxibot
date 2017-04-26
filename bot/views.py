from django.shortcuts import render
from django.http import HttpResponse
import json
import os

# Create your views here.
def confirmation(request):
    #if request.method == "POST":
        #data = request.body.decode('utf-8')
        #received_json_data = json.loads(data)
    path = '/home/vktaxibot/vktaxibot/json.txt'
    f = open(path, 'w')
    f.write('Hello, world!')
    return HttpResponse("Hello, world!")

