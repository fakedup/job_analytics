from db import db_session, Vacancy
from sqlalchemy import or_
import pandas as pd
import datetime as dt

# title. area, description, salary_from, salary_to, salary_gross, published_at, experience, employment, employer

def get_vacancies_query(date_from, date_to, keywords, regions=[1, 2], search_fields = 'all'):

    # SELECT * FROM vacancy WHERE text LIKE '%Python%' OR text LIKE '%Django%';
    # args = (regions, datetime.strptime(date_from, '%Y-%m-%d'), date_to, keywords)

    if search_fields == 'all':
        query = Vacancy.query.filter(
            Vacancy.area.in_(regions),
            Vacancy.published_at >= dt.datetime.strptime(date_from, '%Y-%m-%d'),
            Vacancy.published_at <= dt.datetime.strptime(date_to, '%Y-%m-%d'),
            or_(*(Vacancy.description.like('%{}%'.format(keyword)) for keyword in keywords),
                *(Vacancy.title.like('%{}%'.format(keyword)) for keyword in keywords))
        ).statement

    elif search_fields == 'title':
        query = Vacancy.query.filter(
        Vacancy.area.in_(regions),
        Vacancy.published_at >= dt.datetime.strptime(date_from, '%Y-%m-%d'),
        Vacancy.published_at <= dt.datetime.strptime(date_to, '%Y-%m-%d'),
        or_(*(Vacancy.title.like('%{}%'.format(keyword)) for keyword in keywords))
        ).statement

    return query

def get_vacancies_df (query, session):
    return pd.read_sql(query, session.bind, parse_dates = ['published_at'])

if __name__ == '__main__':

    vacancies = get_vacancies_df (
        get_vacancies_query ('2010-01-01','2017-12-31', ['Python']), 
        db_session)

    print (vacancies)