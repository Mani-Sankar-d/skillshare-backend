from fastapi import FastAPI, Depends, HTTPException, status, Response, Request , UploadFile, File
import schemas, database,models,authenticate
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import os
import aiofiles
from uuid import uuid4
from create_db import create_all_tables


app = FastAPI()
get_db = database.get_db


@app.on_event("startup")
async def on_startup():
    await create_all_tables()


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # your Streamlit origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
async def login(request : schemas.Create_data, response:Response, db:database.AsyncSession = Depends(get_db)):
    data = request.dict()
    
    result = await db.execute(select(models.User).where(models.User.email == data["email"]))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="register first")
    
    if(authenticate.pwd_context.verify(data['hashed_password'], user.hashed_password)):
        access_token = authenticate.generate_access_token(data)
        refresh_token = authenticate.generate_refresh_token(data)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax"
        )
        return {"message":"Welcome to skillshare"}

    else:
        return {"message":"Wrong password"}

@app.get("/refresh")
async def refresh_token(request:Request, response:Response):
    ref_token = request.cookies.get("refresh_token")
    if not ref_token:
        raise HTTPException(status_code=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED, detail="no refresh token")
    payload = authenticate.verify_token(ref_token)
    access_token = authenticate.generate_access_token(payload) 
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax"
    )
    return {"message":"refreshsed successfully"}

@app.post("/create_account")
async def create_account(request : schemas.Create_data, db: database.AsyncSession =  Depends(get_db)):
    data = request.dict()
    data["hashed_password"] = authenticate.hash_password(data["hashed_password"])
    user = models.User(**data)
    db.add(user)
    await db.commit()
    return {"message": "successful"}

@app.post("/logout")
async def logout(request:Request, response:Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message":"logout succesfull"}

@app.post("/post")
async def post_(request : schemas.PostOut, email:str=Depends(authenticate.get_email_from_token), db:database.AsyncSession=Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="missing user")
    data=request.dict()
    data["user_id"] = user.id
    new_post = models.Post(**data)
    db.add(new_post)
    await db.commit()
    return {"added successfully"}

@app.post("/post-skill")
async def post_skill(request:schemas.Post_skills ,email:str=Depends(authenticate.get_email_from_token), db:database.AsyncSession=Depends(get_db)):
    user = await db.execute(select(models.User).options(selectinload(models.User.skills)).where(models.User.email==email))
    user = user.scalars().first()
    existing_skills_rows = user.skills
    new_skills = request.skills
    existing_skills = []

    for row in existing_skills_rows:
        existing_skills.append(row.title)
    for new_skill in new_skills:
        if new_skill not in existing_skills:
            skill = await db.execute(select(models.Skill).where(models.Skill.title==new_skill))
            skill = skill.scalars().first()
            if not skill:
                a = models.Skill(title = new_skill,users=[user])
                db.add(a)
            else:
                user.skills.append(skill)
    await db.commit()
    return {"message":"done"}

@app.get('/search',response_model=schemas.User_profile)
async def search(username:str, email:str=Depends(authenticate.get_email_from_token), db:database.AsyncSession=Depends(get_db)):
    user = await db.execute(select(models.User).options(selectinload(models.User.posts),selectinload(models.User.skills)).where(models.User.email == username))
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user

