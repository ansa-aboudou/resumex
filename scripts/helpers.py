# -*- coding: utf-8 -*-

from scripts import tabledef
from flask import session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import bcrypt


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    s = get_session()
    s.expire_on_commit = False
    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()


def get_session():
    return sessionmaker(bind=tabledef.engine)()


def get_user():
    username = session['username']
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
        return user


def add_user(username, password, email):
    with session_scope() as s:
        u = tabledef.User(username=username, password=password.decode('utf8'), email=email)
        s.add(u)
        s.commit()


def change_user(**kwargs):
    username = session['username']
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
        for arg, val in kwargs.items():
            if val != "":
                setattr(user, arg, val)
        s.commit()


def get_project_list():
    username = session['username']
    with session_scope() as s:
        project = s.query(tabledef.Project).filter(tabledef.Project.username.in_([username])).all()
        return project


def add_project(username, title, description):
    with session_scope() as s:
        u = tabledef.Project(username=username, title=title, description=description)
        s.add(u)
        s.commit()


def get_pay():
    username = session['username']
    with session_scope() as s:
        user = s.query(tabledef.Pay).filter(tabledef.Pay.username.in_([username])).first()
        return user


def add_pay(username):
    with session_scope() as s:
        u = tabledef.Pay(username=username)
        s.add(u)
        s.commit()


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())


def credentials_valid(username, password):
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
        if user:
            return bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8'))
        else:
            return False


def username_taken(username):
    with session_scope() as s:
        return s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()

project_exemple = {"title" : "Software Engineer (Exemple)",
"description" : """You’ll join one of MyGreatCompagny’s software engineering teams for a paid 12-14 week internship that offers hands-on experience with an organization actively changing the face of medicine. You’ll be paired with a summer mentor who will help you get on-boarded, develop your summer project(s) and will help guide your professional development throughout the internship. MyGreatCompagny interns will be placed into one of a variety of teams including Cloud, iOS, Android, Embedded, and Deep Learning.

As part of our team, some example projects include:

Speeding up real-time, machine learning models on mobile platforms
Building infrastructure to securely connect our cloud to hospital systems
Adding features to our cloud-based remote video guidance platform

Qualifications

Baseline skills/experiences/attributes:

Working on Computer Science, Computer Engineering or related undergraduate or graduate degree
Interns: Graduating between December 2020 - June 2022
Full Time: Graduating between December 2019 - June 2020 Experience programming in one of: Python, Kotlin, Java, Swift, Objective-C, C++
Ideally, you also have these skills/experiences/attributes (but it’s ok if you don’t!):

Designing elastic and resilient distributed systems in a cloud environment such as AWS, GCP, or Azure
Containerization and orchestration technologies such as Docker, Kubernetes, ECS, EKS
SQL (especially modern versions of PostgreSQL) and NoSQL databases
A solid understanding of Foundation, UIKit, and Core Graphics
Experience training machine learning models with TensorFlow or TensorFlow Lite

Additional Information

We offer great perks:

Fully covered medical insurance plan, and dental & vision coverage - as a health-tech company, we place great worth on our teams’ well-being
Competitive salaried compensation - we value our employees and show it
Equity - we want every employee to be a stakeholder
Pre-tax commuter benefits - we make your commute more reasonable
Free onsite meals + kitchen stocked with snacks.
401k plan - we facilitate your retirement goals
Beautiful office overlooking the Flatiron building in NYC
The opportunity to build a revolutionary healthcare product and save millions of lives!
For this role, we provide visa assistance for qualified candidates.

MyGreatCompagny network does not accept agency resumes.

MyGreatCompagny Network Inc. is an E-Verify Company and is an equal opportunity employer regardless of race, color, ancestry, religion, gender, national origin, sexual orientation, age, citizenship, marital status, disability or Veteran status. All your information will be kept confidential according to EEO guidelines."""}
