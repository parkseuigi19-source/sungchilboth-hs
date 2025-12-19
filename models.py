from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

# Enums
class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class MasteryLevel(str, enum.Enum):
    PASS = "P"        # 충족
    PARTIAL = "I"     # 부분 충족
    FAIL = "F"        # 미충족

# Core Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(200)) # Simple password or hash
    name = Column(String(50))
    email = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    classes_managed = relationship("Class", back_populates="teacher")
    class_memberships = relationship("ClassMember", back_populates="student")
    submissions = relationship("Submission", back_populates="student")
    reports = relationship("Report", back_populates="student")

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100)) # e.g. "1학년 3반"
    grade = Column(Integer)
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    teacher = relationship("User", back_populates="classes_managed")
    members = relationship("ClassMember", back_populates="_class")
    assignments = relationship("Assignment", back_populates="_class")

class ClassMember(Base):
    __tablename__ = "class_members"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    _class = relationship("Class", back_populates="members")
    student = relationship("User", back_populates="class_memberships")

# Content & Assignment Models
class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    title = Column(String(200))
    description = Column(Text, nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    _class = relationship("Class", back_populates="assignments")
    questions = relationship("Question", back_populates="assignment")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    content = Column(Text) # 문제 지문
    question_type = Column(String(50), default="essay") # essay, choice
    difficulty = Column(String(20), default="medium")
    standard_code = Column(String(50), nullable=True) # 성취기준 코드
    
    assignment = relationship("Assignment", back_populates="questions")
    rubrics = relationship("Rubric", back_populates="question")
    submissions = relationship("Submission", back_populates="question")

class Rubric(Base):
    __tablename__ = "rubrics"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    criteria_text = Column(Text) # 평가 기준 내용
    min_score = Column(Float, default=0) # 해당 기준의 배점
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("Question", back_populates="rubrics")

# Assessment Models
class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    answer_text = Column(Text)
    media_urls = Column(JSON, nullable=True) # List of image URLs
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    retry_count = Column(Integer, default=0)
    
    question = relationship("Question", back_populates="submissions")
    student = relationship("User", back_populates="submissions")
    feedback = relationship("Feedback", uselist=False, back_populates="submission")

class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    mastery_level = Column(Enum(MasteryLevel), default=MasteryLevel.FAIL)
    overall_comment = Column(Text) # 학생에게 보여줄 종합 코멘트
    teacher_summary = Column(Text) # 교사에게 보여줄 요약
    
    # AI Analysis Raw Data
    analysis_json = Column(JSON) # 사고 과정, 논리 구조 등
    misconceptions = Column(JSON) # 태깅된 오개념 리스트
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    submission = relationship("Submission", back_populates="feedback")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200))
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    file_path = Column(String(500)) # PDF path
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="reports")

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    question = Column(Text)
    reply = Column(Text)
    category = Column(String(100))
    score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ClassReport(Base):
    __tablename__ = "class_reports"
    id = Column(Integer, primary_key=True, index=True)
    teacher_username = Column(String(50))
    class_name = Column(String(100))
    subject = Column(String(50))
    report_type = Column(String(20))
    total_students = Column(Integer)
    average_score = Column(Float)
    top_achievers = Column(JSON)
    struggling_students = Column(JSON)
    unit_analysis = Column(JSON)
    leading_points = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    pdf_path = Column(String(500), nullable=True)

class EssayGrading(Base):
    __tablename__ = "essay_gradings"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    subject = Column(String(50))
    question = Column(Text)
    student_answer = Column(Text)
    model_answer = Column(Text)
    score = Column(Float)
    grading_reason = Column(Text)
    feedback = Column(Text)
    graded_by = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())



class AchievementRecord(Base):
    __tablename__ = "achievement_records"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    subject = Column(String(50))
    standard_code = Column(String(50))
    score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())



class Portfolio(Base):
    __tablename__ = "portfolios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    subject = Column(String(50))
    total_questions = Column(Integer)
    total_score = Column(Float)
    average_score = Column(Float)
    strong_areas = Column(JSON)
    weak_areas = Column(JSON)
    learning_progress = Column(JSON)
    pdf_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

