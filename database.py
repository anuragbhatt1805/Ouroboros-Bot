from connection.SQL_db import get_db
from models import User, Student, Teacher, Complaint, Query, Feedback, Status, Account

# Student
def add_student(id, name, mobile, sem, sec):
    try:
        with get_db() as db:
            db.add(User(id=id, name=name, mobile=mobile, user_type=Account.student))
            db.commit()
            db.add(Student(id=id, sem=sem, sec=sec))
            db.commit()
        return None
    except Exception as e:
        print(e)
        return id

def get_student(user_id):
    try:
        with get_db() as db:
            student = db.query(Student, User).join(User, (User.id == Student.id))\
                .filter(User.user_id == user_id).first()
            return student
    except:
        return None

def get_student_detail(id):
    try:
        with get_db() as db:
            student = db.query(Student, User).join(User, (User.id == Student.id))\
                .filter(Student.id == id).first()
            return student
    except:
        return None

def get_all_students(sem=None, sec=None):
    try:
        with get_db() as db:
            if sem is not None:
                if sec is not None:
                    students = db.query(Student, User).join(User, (User.id == Student.id))\
                        .filter(Student.sem == sem, Student.sec == sec).all()
                else:
                    students = db.query(Student, User).join(User, (User.id == Student.id))\
                        .filter(Student.sem == sem).all()
            else:
                students = db.query(Student, User).join(User, (User.id == Student.id)).all()
            return students
    except Exception as e:
        return None

def get_all_verified_students():
    try:
        with get_db() as db:
            student = db.query(User).filter(User.verification == True,\
                User.user_type == Account.student).all()
            return student
    except:
        return None

def get_student_with_query(sem=None, sec=None):
    try:
        with get_db() as db:
            if sem is not None:
                if sec is not None:
                    students = db.query(Student, Query, User).join(Query, (Student.id == Query.user))\
                        .join(User, (User.id == Student.id))\
                        .filter(Student.sem == sem, Student.sec == sec, User.user_id != None).all()
                else:
                    students = db.query(Student, Query, User).join(Query, (Student.id == Query.user))\
                        .join(User, (User.id == Student.id))\
                        .filter(Student.sem == sem, User.user_id != None).all()
            else:
                students = db.query(Student, Query, User).join(Query, (Student.id == Query.user))\
                        .join(User, (User.id == Student.id))\
                        .filter(User.user_id != None).all()
            return students
    except:
        return None

def update_student(id, name=None, mobile=None, sem=None, sec=None):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.id == id).first()
            student = db.query(Student).filter(Student.id == id).first()
            if name is not None:
                user.name = name
            if mobile is not None:
                user.mobile = mobile
                user.verification = False
                user.user_id = None
                user.code = None
            if sem is not None:
                student.sem = sem
            if sec is not None:
                student.sec = sec
            db.commit()
        return None
    except Exception as e:
        return id

def promote_student(id):
    try:
        with get_db() as db:
            student = db.query(Student).filter(Student.id == id).first()
            if student.sem < 9:
                student.sem += 1
                db.commit()
            else:
                raise ValueError("Student has passed out.")
    except Exception as e:
        return None

def demote_student(id):
    try:
        with get_db() as db:
            student = db.query(Student).filter(Student.id == id).first()
            if student.sem > 1:
                student.sem -= 1
                db.commit()
            else:
                raise ValueError("Student is in 1st semester.")
    except Exception as e:
        return None

def delete_student(id):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.id == id).first()
            student = db.query(Student).filter(Student.id == id).first()
            db.delete(user)
            db.delete(student)
            db.commit()
    except Exception as e:
        return None


# Teacher
def add_teacher(id, name, mobile, branch):
    try:
        with get_db() as db:
            db.add(User(id=id, name=name, mobile=mobile, user_type=Account.teacher))
            db.commit()
            db.add(Teacher(id=id, branch=branch))
            db.commit()
        return True
    except:
        return id

def get_teacher(user_id):
    try:
        with get_db() as db:
            teacher = db.query(Teacher, User).join(User, (User.id == Teacher.id))\
                .filter(User.user_id == user_id).first()
            return teacher
    except Exception as e:
        return None

def get_teacher_detail(id):
    try:
        with get_db() as db:
            teacher = db.query(Teacher, User).join(User, (User.id == Teacher.id))\
                .filter(Teacher.id == id).first()
            return teacher
    except Exception as e:
        return None

def get_all_verified_teachers():
    try:
        with get_db() as db:
            print(Account.teacher)
            teachers = db.query(User).filter(User.verification == True,\
                User.user_type == str(Account.teacher)).all()
            return teachers
    except Exception as e:
        print(e)
        return None

def get_all_teachers(branch=None):
    try:
        with get_db() as db:
            if branch is not None:
                teachers = db.query(Teacher, User).join(User, (User.id == Teacher.id))\
                    .filter(Teacher.branch == branch).all()
            else:
                teachers = db.query(Teacher).join(User, (User.id == Teacher.id)).all()
            return teachers
    except Exception as e:
        return None

def get_teacher_with_query(branch=None):
    try:
        with get_db() as db:
            if branch is not None:
                teachers = db.query(Teacher, Query, User).join(Query, (Teacher.id == Query.faculty))\
                    .join(User, (User.id == Teacher.id))\
                    .filter(Teacher.branch == branch, User.user_id != None).all()
            else:
                teachers = db.query(Teacher, Query, User).join(Query, (Teacher.id == Query.faculty))\
                    .join(User, (User.id == Teacher.id))\
                    .filter(Teacher.user_id != None).all()
            return teachers
    except Exception as e:
        return None

def promote_teacher(id):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.id == id, User.user_type == Account.teacher).first()
            if user:
                user.user_type = Account.admin
                db.commit()
                return True
            else:
                return False
    except Exception as e:
        return None

def update_teacher(id, name=None, mobile=None, branch=None):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.id == id).first()
            teacher = db.query(Teacher).filter(Teacher.id == id).first()
            if name is not None:
                user.name = name
            if mobile is not None:
                user.mobile = mobile
                user.verification = False
                user.user_id = None
                user.code = None
            if branch is not None:
                teacher.branch = branch
            db.commit()
    except Exception as e:
        return None

def delete_teacher(id):
    try:
        with get_db() as db:
            user = db.query(Teacher).filter(Teacher.id == id).first()
            teacher = db.query(Teacher).filter(Teacher.id == id).first()
            db.delete(teacher)
            db.delete(user)
            db.commit()
    except Exception as e:
        return None


# User
def add_user(id, name, mobile):
    try:
        with get_db() as db:
            db.add(User(id=id, name=name, mobile=mobile, user_type=Account.admin))
            db.commit()
        return True
    except:
        return id

def check_verfiy(user_id):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user is None:
                return False
            return user.verification
    except Exception as e:
        return None

def add_verify_code(id, user_id, code):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.id == id).first()
            user.user_id = user_id
            user.code = code
            db.commit()
    except Exception as e:
        return None

def verify_code(user_id, code):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user.code == code:
                user.verification = True
                db.commit()
                return True
            else:
                return False
    except:
        return None

def get_user(user_id):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            return user
    except:
        return None

def get_user_by_id(id):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.id == id).first()
            return user
    except:
        return None

def get_admin():
    try:
        with get_db() as db:
            user = db.query(User).filter(User.user_type == Account.admin).first()
            if user:
                return user
            else:
                return None
    except Exception as e:
        return None

def update_user(id, name=None, mobile=None, user_type=None):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.id == id).first()
            if name is not None:
                user.name = name
            if mobile is not None:
                user.mobile = mobile
                user.user_id = None
                user.code = None
                user.verification = False
            if user_type is not None:
                user.user_type = user_type
            db.commit()
    except Exception as e:
        return None

def delete_user(id):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.id == id).first()
            db.delete(user)
            db.commit()
    except:
        return None


# Complaint
def add_complaint(user, title, description):
    try:
        with get_db() as db:
            db.add(Complaint(user=user, subject=title, description=description))
            db.commit()
    except:
        return None

def get_complaint(id):
    try:
        with get_db() as db:
            complaint = db.query(Complaint).filter(Complaint.id == id).first()
            return complaint
    except:
        return None

def get_complaints(user_id = None):
    try:
        with get_db() as db:
            if user_id is None:
                complaints = db.query(Complaint).all()
            else:
                complaints = db.query(Complaint).filter(Complaint.user == user_id).all()
            return complaints
    except:
        return None

def get_active_complaints(user_id = None):
    try:
        with get_db() as db:
            if user_id is None:
                complaints = db.query(Complaint).filter(Complaint.status != Status.resolved).all()
            else:
                complaints = db.query(Complaint).filter(Complaint.user == user_id, Complaint.status != Status.resolved).all()
            return complaints
    except Exception as e:
        return None

def get_resolved_complaints(user_id = None):
    try:
        with get_db() as db:
            if user_id is None:
                complaints = db.query(Complaint).filter(Complaint.status == Status.resolved).all()
            else:
                complaints = db.query(Complaint).filter(Complaint.user == user_id, Complaint.status == Status.resolved).all()
            return complaints
    except:
        return None

def update_complaint(id, status):
    try:
        with get_db() as db:
            if status not in Status.__value__():
                raise ValueError("Invalid status value provided.")
            complaint = db.query(Complaint).filter(Complaint.id == id).first()
            complaint.status = status
            db.commit()
    except Exception as e:
        return None

def delete_complaint(id):
    try:
        with get_db() as db:
            complaint = db.query(Complaint).filter(Complaint.id == id).first()
            db.delete(complaint)
            db.commit()
    except Exception as e:
        return None


# Query
def add_query(user, faculty, subject, description):
    try:
        with get_db() as db:
            db.add(Query(user=user, faculty=faculty, subject=subject, description=description))
            db.commit()
    except:
        return None

def get_query(id):
    try:
        with get_db() as db:
            query = db.query(Query).filter(Query.id == id).first()
            return query
    except:
        return None

def get_queries(user_id = None, faculty = None):
    try:
        with get_db() as db:
            if user_id is None:
                queries = db.query(Query).all()
            elif faculty is not None:
                queries = db.query(Query).filter(Query.user == user_id, Query.faculty == faculty).all()
            else:
                queries = db.query(Query).filter(Query.user == user_id).all()
            return queries
    except:
        return None

def get_active_queries(user_id = None, faculty = None):
    try:
        with get_db() as db:
            if user_id is None:
                queries = db.query(Query).filter(Query.status != Status.resolved).all()
            elif faculty is not None:
                queries = db.query(Query).filter(Query.user == user_id, Query.faculty == faculty, Query.status != Status.resolved).all()
            else:
                queries = db.query(Query).filter(Query.user == user_id, Query.status != Status.resolved).all()
            return queries
    except:
        return None

def get_resolved_queries(user_id = None, faculty = None):
    try:
        with get_db() as db:
            if user_id is None:
                queries = db.query(Query).filter(Query.status == Status.resolved).all()
            elif faculty is not None:
                queries = db.query(Query).filter(Query.user == user_id, Query.faculty == faculty, Query.status == Status.resolved).all()
            else:
                queries = db.query(Query).filter(Query.user == user_id, Query.status == Status.resolved).all()
            return queries
    except Exception as e:
        return None

def update_query(id, faculty, status):
    try:
        with get_db() as db:
            if status not in Status.__value__():
                raise ValueError("Invalid status value provided.")
            query = db.query(Query).filter(Query.id == id, Query.faculty == faculty).first()
            query.status = status
            db.commit()
    except:
        return None

def delete_query(id):
    try:
        with get_db() as db:
            query = db.query(Query).filter(Query.id == id).first()
            db.delete(query)
            db.commit()
    except:
        return None


# Feedback
def add_feedback(user, subject, description):
    try:
        with get_db() as db:
            db.add(Feedback(user=user, subject=subject, description=description))
            db.commit()
    except:
        return None

def get_feedback(id):
    try:
        with get_db() as db:
            feedback = db.query(Feedback).filter(Feedback.id == id).first()
            return feedback
    except:
        return None

def get_feedbacks(user_id = None):
    try:
        with get_db() as db:
            if user_id is None:
                feedbacks = db.query(Feedback).all()
            else:
                feedbacks = db.query(Feedback).filter(Feedback.user == user_id).all()
            return feedbacks
    except Exception as e:
        return None

def delete_feedback(id):
    try:
        with get_db() as db:
            feedback = db.query(Feedback).filter(Feedback.id == id).first()
            db.delete(feedback)
            db.commit()
    except:
        return None