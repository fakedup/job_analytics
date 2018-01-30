from .db import Vacancy
from .db import db_session as dbs
from sqlalchemy import or_
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from sqlalchemy import func
import mpld3

# Reminder for table columns:
# title. area, description, salary_from, salary_to, salary_gross, published_at, experience, employment, employer
# args = (regions, datetime.strptime(date_from, '%Y-%m-%d'), date_to, keywords)

def get_vacancies_query(date_from, date_to, keywords, regions, search_fields):

    '''
    Возвращает sql-запрос со всеми параметрами для передачи в бд
    '''

    # В зависимости от набора полей, в которых искать: только заголовок или заголовок+описание
    if search_fields == 'all':
        query = Vacancy.query.filter(
            Vacancy.area.in_(regions),
            Vacancy.published_at >= dt.datetime.strptime(date_from, '%Y-%m-%d'),
            Vacancy.published_at <= dt.datetime.strptime(date_to, '%Y-%m-%d'),
            or_(*(Vacancy.description.like('%{}%'.format(keyword)) for keyword in keywords),
                *(Vacancy.description.like('%{}%'.format(keyword.lower())) for keyword in keywords),  # Кириллица в SQLite не переводится в нижний регистр
                *(Vacancy.title.like('%{}%'.format(keyword)) for keyword in keywords),
                *(Vacancy.title.like('%{}%'.format(keyword.lower())) for keyword in keywords))
        ).statement

    else:  # search_fields == 'title':
        query = Vacancy.query.filter(
            Vacancy.area.in_(regions),
            Vacancy.published_at >= dt.datetime.strptime(date_from, '%Y-%m-%d'),
            Vacancy.published_at <= dt.datetime.strptime(date_to, '%Y-%m-%d'),
            or_(*(Vacancy.title.like('%{}%'.format(keyword)) for keyword in keywords),
                *(Vacancy.title.like('%{}%'.format(keyword.lower())) for keyword in keywords))
        ).statement

    return query

def get_vacancies_df (query, session = dbs):
    '''
    Возвращает dataframe, соответствующий переданному запросу
    '''

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

def get_number_vacancies_plot (df, keywords):

    # Построение гистограммы с количеством вакансий по месяцам
    # Создание набора данных для графика: период - количество
    plot_data = df['title'].groupby(df['YearMonth']).count()
    
    #Создание фигуры
    fig = plt.figure()

    # Добавление заголовка
    title = 'Number of vacancies with keywords: ' + ', '.join(keywords)
    plt.title (title)

    # Добавление самого графика
    plt.bar(plot_data.index.values, plot_data.values)

    # Возвращается html с графиком
    return mpld3.fig_to_html(fig)

def get_salaries_boxplot (df):

    # Построение боксплота зарплат по месяцам

    fig = plt.figure()

    data = []

    labels = sorted(df.YearMonth.unique())

    fig.autofmt_xdate()

    print (labels)

    for ym in labels:
        data.append(df[(df.YearMonth == ym) & (df.salary > 10000)].salary)
        # data.append(np.nonzero(df[(df.YearMonth == ym)]).salary)

    plt.boxplot(data)

    plt.xticks(np.arange(1,len(labels)+1), labels, rotation='vertical')

    return mpld3.fig_to_html(fig)

def get_titles_pivot (df):

    def min_greater_zero (x):
        try:
            return min(i for i in x if i>0)
        except ValueError:
            return 0

    # med = lambda x: np.median(x[np.nonzero(x)])

    def med(x):
        return np.median([i for i in x if i>0])

    # pivot table by titles and months with count, min, med, max salary
    pivot = pd.pivot_table(df, 
        values = 'salary', 
        index = ['title'],
        fill_value = 0, 
        aggfunc = [len, 
        min_greater_zero,  
        med,
        max])
    pivot = pivot.sort_values([('len', 'salary')], ascending = False )

    return pivot


# def main_analysis(date_from, date_to, keywords, regions = [1, 2], search_fields = 'all'):

#     vacancies = get_vacancies_df (
#         get_vacancies_query (date_from, date_to, keywords, regions, search_fields), 
#         dbs)

#     with open('nv.html', 'w') as nv_file:
#         nv_file.write(get_number_vacancies_plot (vacancies, keywords)) 


#     with open('bp.html', 'w') as nv_file:
#         nv_file.write(get_salaries_boxplot (vacancies))

#     print (get_titles_pivot (vacancies))
