import requests
import json
from db import db_session, Vacancy, Area, Industry
import sqlalchemy.exc

base_url = 'https://api.hh.ru/'

headers = {
    'User-Agent':'test job analytics (sokolov.nikita@gmail.com)',
    'Authorization':'Bearer V1CFTBLRP08MMF4UR2209C8LSVJ8E5J9QF96LTO6CEEG10EF513NEIJNAK6TN4TR'
}

def get_vacancies_ids (datefrom, dateto, search_item, base_url = base_url+'vacancies'):
    ids = []
    per_page = 50
    page = 0
    count = per_page
    while count > 0:
        options = ('?text={}&date_from={}&date_to={}&per_page={}&page={}&no_magic=true'.
                    format (search_item, datefrom, dateto, per_page, page))
        try:
            request = requests.get(base_url+options, headers = headers)
            print (request.text)
            print (request)
            current_search = json.loads(request.text)['items']
        except KeyError:
            current_search = []
        count = len(current_search)
        page += 1
        for item in current_search:
            ids.append(item['id'])
    return ids