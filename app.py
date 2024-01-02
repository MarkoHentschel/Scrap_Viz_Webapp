import streamlit as st
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from datetime import datetime
import database as db
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# --- Initial Settings for the st webapp ---
page_title = "Scrap and visualize Stock Data"
#page_icon = ":money_bag:" # buggy atm, maybe add later https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered"
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}

def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods   
    
hide_st_style = """
            <style>
            #MainMenu {visibilitiy: hidden;}
            footer {visibilitiy: hidden;}
            header {visibilitiy: hidden;}
            </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --------------------------------------------------------

st.title(page_title)

selected = option_menu(
    menu_title=None,
    options=["Query Parameters", "Data Visualization"],
    icons=["bi bi-binoculars", "bar-chart-fill"], #for a list of icons https://icons.getbootstrap.com/
    orientation="horizontal"
)

# --- Form to input query parameters and start query ---
if selected == "Query Parameters":
    st.header(f"Query Parameters")
    with st.form("entry_form", clear_on_submit=True):

        mystocks_name = st.text_input('Name of Stock', '')
        symbol = st.text_input('Stock Symbol', '')
    
        "---"  #this is an optical divider
# --- BS scrap of previous defined informations from yahoo finance based on input stock symbol and insert into deta-db  
        submitted = st.form_submit_button("Start Query")
        if submitted:
            dt = datetime.now()
            load_ts = json.dumps(dt.strftime("%Y-%m-%d %H:%M:%S"))
            pull_id = str(mystocks_name) + "|" + str(load_ts)       
            url = f'https://finance.yahoo.com/quote/{symbol}'
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            price = soup.find('div', {'class':'D(ib) Mend(20px)'}).find_all('fin-streamer')[0].text
            change = soup.find('div', {'class':'D(ib) Mend(20px)'}).find_all('fin-streamer')[1].text
            change_perc = soup.find('div', {'class':'D(ib) Mend(20px)'}).find_all('fin-streamer')[2].text
            db.insert_data(pull_id, symbol, price, change, change_perc, load_ts)
            st.success("Data scraped and saved")    
        
# ---- Plotting -----
if selected == "Data Visualization":
    st.header("Data Visualization")
    with st.form("saved_periods"):
        period = st.selectbox("Select Period:", get_all_periods())
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            period_data = db.get_period(period)
            comment = period_data.get("comment")
            expenses = period_data.get("expenses") 
            incomes = period_data.get("incomes")     
            
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining_budget = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income} {currency}")
            col2.metric("Total Expense", f"{total_expense} {currency}")
            col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
            st.text(f"Comment: {comment}")
            
            # Create sankey chart
            label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
            value = list(incomes.values()) + list(expenses.values())
            
            link = dict(source = source, target = target, value = value)
            node = dict(label = label, pad=50, thickness=5, color="#E694FF")
            data = go.Sankey(link = link, node = node)

            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            st.plotly_chart(fig, use_container_width=True)
