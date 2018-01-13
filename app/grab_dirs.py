import requests
import json
from db import db_session, Vacancy, Area, Industry
import sqlalchemy.exc

base_url = 'https://api.hh.ru/'

headers = {
    'User-Agent':'test job analytics (sokolov.nikita@gmail.com)',
    'Authorization':'Bearer V1CFTBLRP08MMF4UR2209C8LSVJ8E5J9QF96LTO6CEEG10EF513NEIJNAK6TN4TR'
}


def get_areas():
    null = None
    def handle_area(areas_list):
        for item in areas_list:
            yield (item.get('id'), item.get('parent_id'), item.get('name'))
            if len(item.get('areas'))>0:
                areas_list += item.get('areas')

    request = requests.get(base_url+'areas', headers = headers)
    areas_list = json.loads(request.text)

    for an_area in handle_area(areas_list):
        if not Area.query.filter(Area.id == an_area[0]).first():
            area_to_add = Area(id = an_area[0], parent_id = an_area[1], name = an_area[2])
            db_session.add(area_to_add)

    db_session.commit()
    print ('Areas updated')

def get_industries():
    null=None
    def handle_industry(industries_list):
        for item in industries_list:
            yield (str(item.get('id')), item.get('name'))
            if item.get('industries'):
                industries_list += item.get('industries')
    
    request = requests.get(base_url+'industries', headers = headers)
    industries_list = json.loads(request.text)

    for industry in handle_industry(industries_list):
        if not Industry.query.filter(Industry.id == industry[0]).first():
            industry_to_add = Industry(id = industry[0], name = industry[1])
            db_session.add(industry_to_add)

    db_session.commit()
    print ('Industries updated')


if __name__ == '__main__':
    get_areas()
    get_industries()