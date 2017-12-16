import requests
import json
from datetime import datetime
from db import db_session, Vacancy, Area, Industry
import sqlalchemy.exc
from sqlalchemy.sql.expression import func
import threading
from bs4 import BeautifulSoup

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

def get_vacancy(id, area_filter=['1']):
    null = None
    request = requests.get(base_url+str(id), headers = headers)
    # print (request.status_code)
    if request.status_code == 200:

        vacancy = json.loads(request.text)
        name = vacancy['name']
        # print (name)
        if vacancy['area']['id'] in area_filter or len(area_filter) == 0:
            area = int(vacancy['area']['id'])
            description = BeautifulSoup(vacancy['description'], "lxml").text

            if vacancy['salary']:
                salary_from = int(vacancy['salary'].get('from')) if vacancy['salary'].get('from') else null
                salary_to = int(vacancy['salary'].get('to')) if vacancy['salary'].get('to') else null
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

        else:

            return None

    else:

        return None

def put_vacancy(id):
    if not Vacancy.query.filter(Vacancy.id == id).first():
        try:
            vacancy_attrs = get_vacancy(id)
        
            vacancy_to_add = Vacancy(id, *vacancy_attrs)

            db_session.add(vacancy_to_add)
            return 1
        except (TypeError, sqlalchemy.exc.IntegrityError):
            # print ('No such id: {}'.format(id))
            return 0
    else:
        # print ('This id\s already in base: {}'.format(id))
        return 0

def put_vacancies_range(start_id, number_to_put=1000, commit_each = 100):
    counter = 0
    vacancies_added = 0
    for vacancy_id in range(start_id, start_id+number_to_put):
        inc = put_vacancy(vacancy_id)
        vacancies_added += inc
        counter += inc
        if counter == commit_each:
            db_session.commit()
            counter = 0
    else:
        db_session.commit()

    print ('Added {} vacancies.'.format(vacancies_added))

# def put_vacancies_range_threads(start_id, number_to_put=1000, threads_number=4):
#     threads = []
#     for i in range(threads_number):
#         print (i)
#         one_thread = threading.Thread(target = put_vacancies_range, args = (start_id + i * number_to_put, number_to_put ))
#         threads.append(one_thread)

#     for i in range(threads_number):
#         threads[i].start()

#     for i in range(threads_number):
#         threads[i].join()



if __name__ == '__main__':
    current_max_id = db_session.query(func.max(Vacancy.id)).first()[0] + 1
    print (current_max_id)
    put_vacancies_range (current_max_id, 5000, 100)
