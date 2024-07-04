from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Dict
from fastapi import FastAPI
from starlette.websockets import WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class LoginRequest(BaseModel):
    username: str
    password: str

class Symbol(BaseModel):
    symbol: str

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
    "TSLA": 246
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
async def login(login_request: LoginRequest):
    user = users_db.get(login_request.username)
    if not user or user["password"] != login_request.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"access_token": user["token"], "token_type": "bearer"}

@app.get("/get_stock_price")
async def get_stock_price(token: str = Depends(oauth2_scheme)):
    if token != users_db["admin"]["token"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"symbol": "TSLA", "price": stock_prices["TSLA"]}

@app.post("/update_stock_price", include_in_schema=False)
async def update_stock_price(stock_price: StockPrice, token: str = Depends(oauth2_scheme)):
    if token != users_db["admin"]["token"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    if stock_price.symbol != "TSLA":
        raise HTTPException(status_code=400, detail="Invalid stock symbol")
    stock_prices["TSLA"] = stock_price.new_price
    await notify_price_update(stock_prices["TSLA"])
    return {"success": True, "message": "Stock price updated."}

@app.post("/increment_stock_price")
async def increment_stock_price(symbol: Symbol, token: str = Depends(oauth2_scheme)):
    if token != users_db["admin"]["token"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    if symbol.symbol != "TSLA":
        raise HTTPException(status_code=400, detail="Invalid stock symbol")
    stock_prices["TSLA"] += 1
    await notify_price_update(stock_prices["TSLA"])
    return {"success": True, "message": "Stock price incremented by 1.", "new_price": stock_prices["TSLA"]}

@app.get("/tsla")
async def display_stock_price(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "stock_price": stock_prices["TSLA"]})

clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

async def notify_price_update(new_price):
    for client in clients:
        await client.send_text(str(new_price))
