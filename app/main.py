from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import google.generativeai as genai
from dotenv import load_dotenv
import os
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, selects
from database import get_engine

load_dotenv()  # take environment variables from .env

class GoogleChat(BaseModel):
    ingredients: Optional[list] = None

class Recipe(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    description: str

engine = get_engine()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/recipes/")
async def recipe_list(session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Recipe]:
    recipes = session.exec(select(Recipe).offset(offset).limit(limit)).all()
    return recipes

@app.post("/recipe/")
async def recipe_maker(prompt: GoogleChat, session: SessionDep) -> Recipe:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    my_recipe_prompt = """
Eres un cocinero de varias estrellas Michelín. 

Te voy a dar un listado de ingredientes y lo que debes generar es una receta
de alguna estrella Michelín que contenga estos ingredientes. 
Además debes indicar cuanto tiempo tarda en hacer el cocinero esta receta.

Los ingredientes son los siguientes: 

%s

Aquí te paso un ejemplo de receta:

Pasos de la receta:
Tiempo : 3 minutos
Paso 1: Ingredientes listos.
Paso 2: Pon un hilito de aove en una sartén y echa los huevos un poco batidos. Echa también la latita de atún. Remueve despacio.
Paso 3: En cuanto cuaje el huevo, pon una ramita de orégano y sírvelo.
Ingredientes: Huevo y atún.

Devuelveme la receta en formato markdown.

""" % (prompt.ingredients)
    response = model.generate_content(my_recipe_prompt)
    json_compatible_item_data = jsonable_encoder(response.text)

    recipe = Recipe()
    recipe.description = response.text
    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return JSONResponse(content=json_compatible_item_data)
    
