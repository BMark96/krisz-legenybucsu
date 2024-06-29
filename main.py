from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# Simulated Database
users_db = {
    "admin": {
        "username": "admin",
        "password": "admin",
        "token": "BoldogLegenyBucsutKrisz1234"
    }
}

# Simulated Stock Prices
stock_prices = {
    "TSLA": 197.00
}

# OAuth2 Password Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class StockPrice(BaseModel):
    symbol: str
    new_price: float

@app.get("/")
async def root():
    return {"message": "Success"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"access_token": user["token"], "token_type": "bearer"}

@app.get("/get_stock_price")
async def get_stock_price(token: str = Depends(oauth2_scheme)):
    if token != users_db["admin"]["token"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"symbol": "TSLA", "price": stock_prices["TSLA"]}

@app.post("/update_stock_price")
async def update_stock_price(stock_price: StockPrice, token: str = Depends(oauth2_scheme)):
    if token != users_db["admin"]["token"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    if stock_price.symbol != "TSLA":
        raise HTTPException(status_code=400, detail="Invalid stock symbol")
    stock_prices["TSLA"] = stock_price.new_price
    return {"success": True, "message": "Stock price updated."}

# Run the app with: uvicorn main:app --reload
