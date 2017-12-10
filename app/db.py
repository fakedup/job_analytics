from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import os.path

db_path = 'db/vacancies.db'
engine = create_engine('sqlite:///'+db_path)

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    city = Column(String(50))
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

def add_vacancy_data (id, title, city, description, salary_from, salary_to, publish_date, db_session = db_session,):
    db_session.add(Vacancy(id, title, city, description, salary_from, salary_to, publish_date))
    db_session.commit()

if __name__ == "__main__":

    if os.path.exists(db_path):
        print ('Database exists already. Skip creating.')
    else:
        Base.metadata.create_all(bind=engine)
        print ('Database created.')