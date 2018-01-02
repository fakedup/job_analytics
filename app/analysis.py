from db import db_session, Vacancy
from sqlalchemy import or_
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

# Reminder for table columns:
# title. area, description, salary_from, salary_to, salary_gross, published_at, experience, employment, employer

def get_vacancies_query(date_from, date_to, keywords, regions, search_fields):

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

    else:  # search_fields == 'title':
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
    df['YearMonth'] = df['published_at'].map(
        lambda x: str(x.year) + 
        '-' + 
        (str(x.month) if len(str(x.month)) == 2 else '0' + str(x.month)))
    df['salary'] = df[['salary_from', 'salary_to', 'salary_gross']].apply(calc_avg_salary, axis = 1)

    return df

def main_analysis(date_from, date_to, keywords, regions = [1, 2], search_fields = 'all'):

    vacancies = get_vacancies_df (
        get_vacancies_query (date_from, date_to, keywords, regions, search_fields), 
        db_session)

    # number of vacancies plot
    sample = vacancies['salary'].groupby(vacancies['YearMonth']).count()
    title = 'Number of vacancies by months with keywords: ' + ', '.join(keywords)
    number_vacancies_bar = sample.plot(
        kind="bar", 
        title=title, 
        color='blue', 
        figsize = (12, 8)
        )
    plt.savefig('foo.png')
    
    # salaries boxplot
    salaries_boxplot = vacancies[vacancies.salary>0].boxplot(
        column = 'salary', 
        by = 'YearMonth',
        rot = 90,
        figsize = (12, 8),
        grid = False
        )
    plt.savefig('bar.png')



if __name__ == '__main__':

    main_analysis ('2010-01-01','2017-12-31', ['менеджер'])