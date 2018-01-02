from db import db_session, Vacancy
from sqlalchemy import or_
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

# Reminder for table columns:
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

    def calc_avg_salary(row):
    if pd.isnull(row['salary_from'])  and pd.isnull(row['salary_to']):
        return 0
    if row['salary_gross'] == True:
        multiplier = 0.87
    else:
        multiplier = 1
    if pd.isnull(row['salary_to']):
        return row['salary_from'] * multiplier
    if pd.isnull(row['salary_from']):
        return row['salary_to'] * multiplier
    return (row['salary_from'] + row['salary_to'])/2*multiplier

    df = pd.read_sql(query, session.bind, parse_dates = ['published_at'])
    df['YearMonth'] = df['published_at'].map(lambda x: str(x.year) + '-' +str(x.month))
    df['salary'] = df[['salary_from', 'salary_to', 'salary_gross']].apply(calc_avg_salary, axis = 1)

    return df

if __name__ == '__main__':

    vacancies = get_vacancies_df (
        get_vacancies_query ('2010-01-01','2017-12-31', ['Python'], search_fields = 'title'), 
        db_session)

    sample = vacancies.groupby(vacancies["YearMonth"]).count()

    sample.plot(kind="bar")

    plt.show()