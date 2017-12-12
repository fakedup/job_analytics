from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import os.path

db_path = 'db/hh_base.db'
engine = create_engine('sqlite:///'+db_path)

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    area = Column(Integer, ForeignKey('areas.id'))
    description = Column(String(1000))
    salary_from = Column(Integer)
    salary_to = Column(Integer)
    publish_date = Column(DateTime)

    def __init__(self, id, title = None, city = None, 
                description = None, salary_from = None,
                salary_to = None, publish_date = None):
        self.id = id
        self.title = title
        self.city = city
        self.description = description
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.publish_date = publish_date
    
    def __repr__(self):
        return '<{}, {}, {} - {}>'.format(self.title, self.city, self.salary_from, self.salary_to)

class Area(Base):
    __tablename__ = 'areas'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('areas.id'))
    name = Column(String(50))

    def __init__(self, id, parent_id, name):
        self.id = id
        self.parent_id = parent_id
        self.name = name

    def __repr__(self):
        return 'Area: ({}) {}'.format(self.id, self.name)

class Industry(Base):
    __tablename__ = 'industries'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('industries.id'))
    name = Column(String(50))

    def __init__(self, id, parent_id, name):
        self.id = id
        self.parent_id = parent_id
        self.name = name

    def __repr__(self):
        return 'Industry: ({}) {}'.format(self.id, self.name)

# class VacancyIndustry(Base):
#     __tablename__ = 'vacancies_industries'
#     vacancy_id = Column(Integer, ForeignKey('vacancies.id'))
#     industry_id = Column(Integer, ForeignKey('industries.id'))

#     def __init__(self, vacancy_id, industry_id):
#         self.vacancy_id = vacancy_id
#         self.industry_id = industry_id

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
