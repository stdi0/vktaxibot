import json
import requests

API_KEY = '76150e77f594d464ca0f2f580c9b7250e50295ec'
BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/%s'

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
    
city = 'Мурманск'    
result = suggest(city, 'address')

for i in result.get('suggestions'):
    if str(i['data']['city']).lower() == city.lower():
        print(i['data']['city'])
        break
else:
    print('None')

address = 'Миронова, 33/1'
result = suggest(city + ' ' + address, 'address')
for i in result.get('suggestions'):
   if i['data']['street'] is not None:


#print(result)
