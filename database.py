import os
from deta import Deta
from dotenv import load_dotenv

#--loading deta connection (database)
load_dotenv(".env")
DETA_PROJECT_KEY = os.getenv("DETA_KEY")


deta = Deta(DETA_PROJECT_KEY)

db = deta.Base("scrap_viz_data")

def insert_data(pull_id, symbol, price, change, change_perc, load_ts):
    return db.put({"key": pull_id, "symbol": symbol, "price": price, "change": change, "change_perc": change_perc, "load_ts": load_ts})
    

def fetch_all_periods():
    res = db.fetch()
    return res.items

def get_period(period):
    return db.get(period)

