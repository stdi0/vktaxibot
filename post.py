import json
import requests

#API_KEY = '76150e77f594d464ca0f2f580c9b7250e50295ec'
#BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/%s'

def suggest():
    url = 'http://codestats.pythonanywhere.com/stdi0/api_call/'
#    headers = { 
#        'Authorization': 'Token %s' % API_KEY,
#        'Content-Type': 'application/json',
#    }
    data = {
        'count': 10,
        'password': 'joo0shaij'
    }
    r = requests.post(url, data=json.dumps(data))
    return r
    
#city = 'Мурманск'    
result = suggest()

print(result)

#for i in result.get('suggestions'):
#    if str(i['data']['city']).lower() == city.lower():
#        print(i['data']['city'])
#        break
#else:
#    print('None')

#address = 'Миронова, 33/1'
#result = suggest(city + ' ' + address, 'address')
#for i in result.get('suggestions'):
#   if i['data']['street'] is not None:


#print(result)
