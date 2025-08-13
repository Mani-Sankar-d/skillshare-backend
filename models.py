from sqlalchemy import Column,Integer,ForeignKey,Table,String
from sqlalchemy.orm import relationship, declarative_base
from database import engine
Base = declarative_base()
skill_user = Table(
    "skill_user",
    Base.metadata,
    Column("skill_id",ForeignKey("skills.id"),primary_key=True),
    Column("user_id",ForeignKey("users.id"),primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    id  =  Column(Integer,primary_key=True)
    email  =  Column(String)
    hashed_password  = Column(String)
    skills = relationship("Skill", secondary = skill_user, back_populates="users")
    posts = relationship("Post",back_populates="user")

class Skill(Base):
    __tablename__ = 'skills' 
    id =  Column(Integer, primary_key=True)
    title = Column(String)
    users = relationship("User", secondary=skill_user, back_populates="skills")

class Post(Base):
    __tablename__ ="posts"
    id = Column(Integer, primary_key=True)
    post = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User",back_populates="posts")
