import requests
import json
from datetime import datetime
from db import db_session, Vacancy, Area, Industry
import sqlalchemy.exc

base_url = 'https://api.hh.ru/vacancies/'

headers = {
    'User-Agent':'test job analytics (sokolov.nikita@gmail.com)',
    'Authorization':'Bearer V1CFTBLRP08MMF4UR2209C8LSVJ8E5J9QF96LTO6CEEG10EF513NEIJNAK6TN4TR'
}

# def get_vacancies_ids (datefrom, dateto, search_item, base_url = base_url+'vacancies'):
#     ids = []
#     per_page = 50
#     page = 0
#     count = per_page
#     while count > 0:
#         options = ('?text={}&date_from={}&date_to={}&per_page={}&page={}&no_magic=true'.
#                     format (search_item, datefrom, dateto, per_page, page))
#         try:
#             request = requests.get(base_url+options, headers = headers)
#             print (request.text)
#             print (request)
#             current_search = json.loads(request.text)['items']
#         except KeyError:
#             current_search = []
#         count = len(current_search)
#         page += 1
#         for item in current_search:
#             ids.append(item['id'])
#     return ids

def get_vacancy(id):
    null = None
    request = requests.get(base_url+str(id), headers = headers)
    vacancy = json.loads(request.text)
    name = vacancy['name']
    area = int(vacancy['area']['id'])
    description = vacancy['description']

    if vacancy['salary']:
        salary_from = int(vacancy['salary'].get('from'))
        salary_to = int(vacancy['salary'].get('to'))
        salary_gross = vacancy['salary'].get('gross')
        if salary_gross == 'true':
            salary_gross = True
        elif salary_gross == 'false':
            salary_gross = False
    else:
        salary_from = null
        salary_to = null
        salary_gross = null

    published_at = datetime.strptime(vacancy['published_at'][:-5], '%Y-%m-%dT%H:%M:%S')

    exp = vacancy['experience']['name']
    employment = vacancy['employment']['name']
    employer = vacancy['employer']['name']


    return (name, area, description, 
            salary_from, salary_to, salary_gross, 
            published_at, exp, employment , employer)

def put_vacancy(id):
    if not Vacancy.query.filter(Vacancy.id == id).first():
        name, area, description, salary_from, salary_to, salary_gross, published_at, exp, employment , employer = get_vacancy(id)
        vacancy_to_add = Vacancy(id, name, area, description, salary_from, salary_to, salary_gross, published_at, exp, employment , employer)
        db_session.add(vacancy_to_add)

if __name__ == '__main__':
    id = 10000001
    put_vacancy (id)
    db_session.commit()