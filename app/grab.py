import requests
import json

base_url = 'https://api.hh.ru/vacancies'

headers = {
    'User-Agent':'test job analytics (sokolov.nikita@gmail.com)'
}

def get_vacancies_ids (datefrom, dateto, search_item, base_url = base_url):
    ids = []
    per_page = 50
    page = 0
    count = per_page
    while count == per_page:
        options = ('?text={}&datefrom={}&dateto={}&per_page={}&page={}'.
                    format (search_item, datefrom, dateto, per_page, page))
        try:
            current_search = json.loads(requests.get(base_url+options, headers = headers).text)['items']
        except KeyError:
            current_search = []
        count = len(current_search)
        page += 1
        for item in current_search:
            ids.append(item['id'])
    return ids

print (get_vacancies_ids('2016-09-01', '2016-09-02', 'Python'))