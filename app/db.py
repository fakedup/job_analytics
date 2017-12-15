from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
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
    salary_gross = Column(Boolean)
    published_at = Column(DateTime)
    experience = Column(String(15))
    employment = Column(String(10))
    employer = Column(String(200))


    def __init__(self, id, title = None, area = None, 
                description = None, salary_from = None,
                salary_to = None, salary_gross = None, 
                published_at = None, experience = None, 
                employment = None, employer = None):
        self.id = id
        self.title = title
        self.area = area
        self.description = description
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.published_at = published_at
        self.experience = experience
        self.employment = employment
        self.employer = employer
    
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
    id = Column(String(10), primary_key=True)
    name = Column(String(50))

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return 'Industry: ({}) {}'.format(self.id, self.name)

class Profarea(Base):
    __tablename__ = 'vacancies_profareas'
    vacancy_id = Column(Integer, ForeignKey('vacancies.id'), primary_key = True)
    profarea = Column(String(50), primary_key = True)
    specialization = Column(String(100), primary_key = True)

    def __init__(self, vacancy_id, profarea, specialization):
        self.vacancy_id = vacancy_id
        self.profarea = profarea
        self.specialization = specialization

class KeySkills(Base):
    __tablename__ = 'vacancies_skills'
    vacancy_id = Column(Integer, ForeignKey('vacancies.id'), primary_key = True)
    skill = Column(String(50), primary_key = True)

    def __init__ (self, vacancy_id, skill):
        self.vacancy_id = vacancy_id
        self.skill = skill


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
