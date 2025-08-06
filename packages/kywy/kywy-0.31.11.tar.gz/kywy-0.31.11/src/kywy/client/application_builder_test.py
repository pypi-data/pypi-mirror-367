from faker import Faker
import pandas as pd
import numpy as np
from random import randint, choice
from datetime import datetime, timedelta, date
import random
from ..client.kawa_client import KawaClient
from .application.application_builder import ApplicationBuilder, DataSet, DataModel
from ..client.kawa_decorators import kawa_tool

# TODO: Capacity to make charts directly on top of data sources
# SO: Init sheets automatically - or find a way to do it lazily
# kawa = KawaClient(kawa_api_url='https://crypto.kawa.ai')
# kawa.set_api_key(api_key_file='/Users/emmanuel/doc/crypto/.key')

kawa = KawaClient(kawa_api_url='http://localhost:4200')
kawa.set_api_key(api_key_file='/Users/emmanuel/doc/local-pristine/.key')
kawa.set_active_workspace_id(workspace_id='75')

#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
from kywy.client.kawa_decorators import kawa_tool
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from faker import Faker

app = kawa.app(
    application_name='Suspicious Trading Activity Detection',
    palette_name='autumn'
)


@kawa_tool(
    outputs={
        'trade_id': str,
        'trade_date': date,
        'trader_id': str,
        'stock': str,
        'quantity': float,
        'price': float,
        'investment': float,
        'profit': float,
        'anomaly_score': float
    }
)
def trades_generator():
    fake = Faker()
    nasdaq_stocks = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'FB', 'TSLA', 'NVDA', 'PYPL', 'NFLX', 'INTC',
                     'ADBE', 'PEP', 'CSCO', 'AVGO', 'TMUS', 'CMCSA', 'COST', 'TXN', 'QCOM', 'CHTR']
    data = []
    for i in range(1000):
        trade_date = fake.date_between(start_date='-3y', end_date='today')
        quantity = fake.random_int(min=1, max=1000)
        price = fake.pyfloat(left_digits=3, right_digits=2, positive=True, min_value=50, max_value=1000)
        investment = price * quantity
        max_profit_value = min(99999.99, investment * 0.3)  # Adjust max value to be within left digits
        min_profit_value = max(-99999.99, -investment * 0.3)  # Adjust min value to be within left digits
        profit = fake.pyfloat(left_digits=5, right_digits=2, positive=False, min_value=min_profit_value,
                              max_value=max_profit_value)
        anomaly_score = fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=0.1, max_value=1)
        if fake.boolean(chance_of_getting_true=15):
            profit = investment * 0.5
            anomaly_score += 0.5
        data.append({
            'trade_id': f'trade{str(i).zfill(4)}',
            'trade_date': trade_date,
            'trader_id': f'trader{str(fake.random_int(min=1, max=50)).zfill(3)}',
            'stock': fake.random_element(nasdaq_stocks),
            'quantity': float(quantity),
            'price': float(price),
            'investment': float(investment),
            'profit': float(profit),
            'anomaly_score': min(anomaly_score, 1.0)
        })
    return pd.DataFrame(data)


trades_dataset = app.create_dataset(
    name='Trades',
    generator=trades_generator,
)


@kawa_tool(
    outputs={
        'trader_id': str,
        'name': str,
        'age': float,
        'experience_years': float,
        'total_trades': float
    }
)
def traders_generator():
    fake = Faker()
    data = []
    for i in range(50):
        data.append({
            'trader_id': f'trader{str(i + 1).zfill(3)}',
            'name': fake.name(),
            'age': float(fake.random_int(min=21, max=65)),
            'experience_years': float(fake.random_int(min=1, max=40)),
            'total_trades': float(fake.random_int(min=100, max=1000))
        })
    return pd.DataFrame(data)


traders_dataset = app.create_dataset(
    name='Traders',
    generator=traders_generator,
)

model = app.create_model(
    dataset=trades_dataset,
)

rel_traders = model.create_relationship(
    name='TradersRelationship',
    dataset=traders_dataset,
    link={'trader_id': 'trader_id'}
)

rel_traders.add_column(
    name='name',
    aggregation='FIRST',
    new_column_name='trader_name',
)

rel_traders.add_column(
    name='age',
    aggregation='FIRST',
    new_column_name='trader_age',
)

rel_traders.add_column(
    name='experience_years',
    aggregation='FIRST',
    new_column_name='trader_experience_years',
)

rel_traders.add_column(
    name='total_trades',
    aggregation='FIRST',
    new_column_name='total_trades',
)

app.create_text_filter(
    name='Stock Filter',
    filtered_column='stock',
    source=trades_dataset,
)

app.create_text_filter(
    name='Trader Filter',
    filtered_column='name',
    source=traders_dataset,
)

app.create_text_filter(
    name='Anomaly Score Filter',
    filtered_column='anomaly_score',
    source=trades_dataset,
)

anomalies_page = app.create_page('Trade Anomalies Detection')

col1 = anomalies_page.create_section(title='Description', num_columns=1)
col1.text_widget('''
This dashboard aims to detect suspicious trading activities such as insider trading and market manipulations.
The charts illustrate anomalies in trade patterns, which are analyzed using various parameters.
Pay special attention to scatter plots which may indicate unusual trade patterns.
''')

col1, col2 = anomalies_page.create_section(title='Main', num_columns=2)

col1.indicator_chart(
    title='Total Profit',
    indicator='profit',
    aggregation='SUM',
)

col1.scatter_chart(
    source=model,
    title='Investment vs. Profit',
    granularity='trader_id',
    x='investment',
    aggregation_x='SUM',
    y='profit',
    aggregation_y='SUM',
    color='anomaly_score',
    aggregation_color='AVERAGE',
)

col2.scatter_chart(
    source=model,
    title='Profit vs. Quantity',
    granularity='stock',
    x='profit',
    aggregation_x='SUM',
    y='quantity',
    aggregation_y='SUM',
    color='anomaly_score',
    aggregation_color='AVERAGE',
)

col1.bar_chart(
    source=model,
    title='Average Anomaly Score per Stock',
    x='stock',
    y='anomaly_score',
    aggregation='AVERAGE'
)

col2.line_chart(
    source=trades_dataset,
    title='Average Price Per Trader Over Time',
    x='trade_date',
    y='price',
    aggregation='AVERAGE',
    time_sampling='YEAR_AND_MONTH'
)

col1.pie_chart(
    source=model,
    title='Total Investment by Trader',
    x='trader_id',
    y='investment',
    aggregation='SUM'
)

col2.line_chart(
    source=model,
    title='Investment Trends by Stock',
    x='trade_date',
    y='investment',
    aggregation='SUM',
    time_sampling='YEAR'
)

col1.scatter_chart(
    source=model,
    title='Profit vs. Trader Experience',
    granularity='trader_id',
    x='profit',
    aggregation_x='SUM',
    y='trader_experience_years',
    aggregation_y='FIRST',
    color='total_trades',
    aggregation_color='FIRST',
)

col2.scatter_chart(
    source=model,
    title='Quantity vs. Anomaly Score',
    granularity='stock',
    x='quantity',
    aggregation_x='SUM',
    y='anomaly_score',
    aggregation_y='AVERAGE',
    color='trader_age',
    aggregation_color='FIRST',
)

col1.table(
    source=traders_dataset,
    title='Trader Information'
)

col2.table(
    source=trades_dataset,
    title='Trade Details'
)

col1, col2, col3, col4 = anomalies_page.create_section(title='Main', num_columns=4)

col1.scatter_chart(
    source=model,
    title='Profit vs. Trader Experience',
    granularity='trader_id',
    x='profit',
    aggregation_x='SUM',
    y='trader_experience_years',
    aggregation_y='FIRST',
    color='total_trades',
    aggregation_color='FIRST',
)

col2.scatter_chart(
    source=model,
    title='Quantity vs. Anomaly Score',
    granularity='stock',
    x='quantity',
    aggregation_x='SUM',
    y='anomaly_score',
    aggregation_y='AVERAGE',
    color='trader_age',
    aggregation_color='FIRST',
)

col3.table(
    source=traders_dataset,
    title='Trader Information'
)

col4.table(
    source=trades_dataset,
    title='Trade Details'
)

app.publish()
