from sqlalchemy import Column, Integer, String, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from connection.SQL_db import Base
from datetime import datetime

class Status():
    raised = "raised"
    rejected = "rejected"
    inprogress = "inprogress"
    resolved = "resolved"
    delete = "delete"

    def __value__():
        return ["raised", "rejected", "inprogress", "resolved", "delete"]

class Account():
    student = "student"
    teacher = "teacher"
    admin = "admin"

    def __value__():
        return ["student", "teacher", "admin"]


class User(Base):
    __tablename__ = "user_account"

    id = Column(String(12), primary_key=True)
    name = Column(String(50))
    mobile = Column(String(20), unique=True)
    verification = Column(Boolean, default=False)
    code = Column(String(10))
    user_id = Column(String(20), unique=True, nullable=True)
    user_type = Column(String(20))


class Student(Base):
    __tablename__ = "student"

    id = Column(String(10), ForeignKey("user_account.id"), primary_key=True)
    sem = Column(Integer)
    sec = Column(String(10))


class Teacher(Base):
    __tablename__ = "teacher"

    id = Column(String(10), ForeignKey("user_account.id"), primary_key=True)
    branch = Column(String(20))


class Complaint(Base):
    __tablename__ = "complaint"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(10), ForeignKey("user_account.id"))
    subject = Column(String(100))
    description = Column(String(500))
    status = Column(String(10), default=Status.raised)
    date = Column(Date, default=datetime.now().date())
    time = Column(Time, default=datetime.now().time())


class Query(Base):
    __tablename__ = "query"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(10), ForeignKey("student.id"))
    faculty = Column(String(10), ForeignKey("teacher.id"))
    subject = Column(String(100))
    description = Column(String(500))
    status = Column(String(10), default=Status.raised)
    date = Column(Date, default=datetime.now().date())
    time = Column(Time, default=datetime.now().time())


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(10), ForeignKey("user_account.id"))
    subject = Column(String(100))
    description = Column(String(500))
    date = Column(Date, default=datetime.now().date())
    time = Column(Time, default=datetime.now().time())