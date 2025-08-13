from pydantic import BaseModel
from typing import List
import models
class Create_data(BaseModel):
    email : str
    hashed_password : str

class PostOut(BaseModel):
    post:str

class SkillOut(BaseModel):
    title:str
class Post_skills(BaseModel):
    skills:List[str]
class User_profile(BaseModel):
    email:str
    id:int
    posts:List[PostOut]
    skills:List[SkillOut]