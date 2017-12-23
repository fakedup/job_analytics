import requests
import json
from datetime import datetime
from db import db_session, Vacancy, Area, Industry
from grab_dirs import get_areas
import sqlalchemy.exc
from sqlalchemy.sql.expression import func
import threading
from bs4 import BeautifulSoup

base_url = 'https://api.hh.ru/vacancies/'

headers = {
    'User-Agent':'test job analytics (sokolov.nikita@gmail.com)',
    'Authorization':'Bearer V1CFTBLRP08MMF4UR2209C8LSVJ8E5J9QF96LTO6CEEG10EF513NEIJNAK6TN4TR'
}

def get_vacancy_dict(id):
    request = requests.get(base_url + str(id), headers=headers)

    if request.status_code == 200:
        result = json.loads(request.text)
        result['id'] = id
        return result

    return None

def parse_vacancy(vacancy_dict, area_filter=('1', '2')):
    name = vacancy_dict['name']
    if vacancy_dict['area']['id'] in area_filter or len(area_filter) == 0:
        area = int(vacancy_dict['area']['id'])
        description = BeautifulSoup(vacancy_dict['description'], "lxml").text

        if vacancy_dict['salary']:
            salary_from = (
                int(vacancy_dict['salary'].get('from'))
                if vacancy_dict['salary'].get('from') else None
            )
            salary_to = (
                int(vacancy_dict['salary'].get('to'))
                if vacancy_dict['salary'].get('to') else None
            )
            salary_gross = vacancy_dict['salary'].get('gross')
            if salary_gross == 'true':
                salary_gross = True
            elif salary_gross == 'false':
                salary_gross = False
        else:
            salary_from = None
            salary_to = None
            salary_gross = None

        published_at = datetime.strptime(
            vacancy_dict['published_at'][:-5],
            '%Y-%m-%dT%H:%M:%S')

        exp = vacancy_dict['experience']['name']
        employment = vacancy_dict['employment']['name']
        employer = vacancy_dict['employer']['name']

        return (vacancy_dict['id'], name, area, description,
                salary_from, salary_to, salary_gross,
                published_at, exp, employment, employer)


def put_vacancy(vacancy_attrs):
    try:
        vacancy_to_add = Vacancy(*vacancy_attrs)

        db_session.add(vacancy_to_add)
        return True
    except sqlalchemy.exc.IntegrityError:
        print('Something went wrong for id {}'.format(vacancy_attrs[0]))
    return False


def put_vacancies_range(start_id, number_to_put=1000, commit_each=100):
    counter = 0
    vacancies_added = 0
    current_counter = 0
    vacancy_id = start_id
    max_id = 23000000
    while current_counter<number_to_put and vacancy_id<max_id:
        inc = 0

        if not Vacancy.query.filter(Vacancy.id == vacancy_id).first():
            vacancy_dict = get_vacancy_dict(vacancy_id)
            if vacancy_dict:
                vacancy_attrs = parse_vacancy(vacancy_dict)
                if vacancy_attrs and put_vacancy(vacancy_attrs):
                    inc = 1

        vacancies_added += inc
        counter += inc
        if counter == commit_each:
            db_session.commit()
            current_counter += counter
            print ('{} vacancies added since start.'.format(current_counter))
            counter = 0
        vacancy_id += 1
    else:
        db_session.commit()

    print('Added {} vacancies.'.format(vacancies_added))

def put_vacancies_range_2(start_id, number_to_put, commit_each):
    # Параллелим обращения к api hh.ru

    vacancy_ids = list(range(start_id, start_id + number_to_put))
    
    vacancy_dicts = []

    def getter():
        try:
            while True:
                vacancy_id = vacancy_ids.pop()
                vacancy_dict = get_vacancy_dict(vacancy_id)
                if vacancy_dict:
                    vacancy_dicts.append(vacancy_dict)
        except IndexError:
            pass

    getter_threads = []

    for i in range(4):
        getter_thread = threading.Thread(target=getter)
        getter_threads.append(getter_thread)

    for thread in getter_threads:
        thread.start()

    counter = 0
    vacancies_added = 0

    while any(t.isAlive() for t in getter_threads) or vacancy_dicts:
        if vacancy_dicts:
            inc = 0
            vacancy_dict = vacancy_dicts.pop()
            vacancy_attrs = parse_vacancy(vacancy_dict)
            if vacancy_attrs:
                if not Vacancy.query.filter(Vacancy.id == vacancy_attrs[0]).first():
                    vacancy_to_add = Vacancy(*vacancy_attrs)
                    db_session.add(vacancy_to_add)
                    inc = 1
            vacancies_added += inc
            counter += inc
            if counter == commit_each:
                db_session.commit()
                print('Added {} vacancies.'.format(vacancies_added))
                counter = 0
    else:
        db_session.commit()

    print('Added {} vacancies.'.format(vacancies_added))

    for thread in getter_threads:
        thread.join()


def grab(putter=put_vacancies_range, recreate = False):
    if recreate:
        from db import recreate_db
        recreate_db()  # Пересоздаем базу данных
    # get_areas()
    current_max_id = db_session.query(func.max(Vacancy.id)).scalar() or 9000000
    putter(current_max_id, number_to_put=10000, commit_each=500)



if __name__ == '__main__':
    
    grab(put_vacancies_range_2)
