import pandas as pd
from datetime import date, datetime
from .application_builder import ApplicationBuilder, DataSet, DataModel
from ...client.kawa_client import KawaClient
from ...client.kawa_decorators import kawa_tool


def kawa():
    k = KawaClient(kawa_api_url='http://localhost:4200')
    k.set_api_key(api_key_file='/Users/emmanuel/doc/local-pristine/.key')
    k.set_active_workspace_id(workspace_id='75')
    return k


app = kawa().app(
    application_name='Client Monitoring Dashboard',
    sidebar_color='#2c3e50',
)


# -- DATA SECTION: start

@kawa_tool(
    outputs={
        'client_id': str,
        'company_name': str,
        'industry': str,
        'contact_person': str,
        'email': str,
        'phone': str,
        'country': str,
        'city': str,
        'registration_date': date,
        'last_contact_date': date,
        'contract_value': float,
        'monthly_revenue': float,
        'satisfaction_score': float,
        'support_tickets': float,
        'account_status': str
    }
)
def client_data_generator():
    fake = Faker()
    data = []

    industries = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Education', 'Real Estate',
                  'Consulting']
    countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Australia', 'Japan', 'Brazil']
    statuses = ['Active', 'Inactive', 'Pending', 'Churned']

    for i in range(150):
        client_id = f"client{i + 1:03d}"
        company_name = fake.company()
        industry = np.random.choice(industries)
        contact_person = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        country = np.random.choice(countries)
        city = fake.city()

        # Registration date between 2020 and 2024
        registration_date = fake.date_between(start_date=date(2020, 1, 1), end_date=date(2024, 12, 31))

        # Last contact date should be after registration
        last_contact_date = fake.date_between(start_date=registration_date, end_date=date(2024, 12, 31))

        # Contract value with some outliers
        if np.random.random() < 0.1:  # 10% high-value clients
            contract_value = np.random.uniform(500000, 2000000)
        else:
            contract_value = np.random.uniform(10000, 200000)

        monthly_revenue = contract_value / 12 * np.random.uniform(0.8, 1.2)

        # Satisfaction score 1-10
        satisfaction_score = np.random.uniform(1, 10)

        # Support tickets - more for unsatisfied clients
        if satisfaction_score < 5:
            support_tickets = np.random.uniform(10, 50)
        else:
            support_tickets = np.random.uniform(0, 15)

        # Account status weighted by satisfaction
        if satisfaction_score < 3:
            account_status = np.random.choice(['Churned', 'Inactive'], p=[0.7, 0.3])
        elif satisfaction_score < 6:
            account_status = np.random.choice(['Active', 'Pending'], p=[0.6, 0.4])
        else:
            account_status = 'Active'

        data.append([
            client_id, company_name, industry, contact_person, email, phone,
            country, city, registration_date, last_contact_date, contract_value,
            monthly_revenue, satisfaction_score, support_tickets, account_status
        ])

    df = pd.DataFrame(data, columns=[
        'client_id', 'company_name', 'industry', 'contact_person', 'email', 'phone',
        'country', 'city', 'registration_date', 'last_contact_date', 'contract_value',
        'monthly_revenue', 'satisfaction_score', 'support_tickets', 'account_status'
    ])

    return df


client_dataset = app.create_dataset(
    name='Client Data',
    generator=client_data_generator,
)

# -- DATA SECTION: end


# -- MODEL SECTION: start

model = app.create_model(
    dataset=client_dataset,
)

model.create_variable(
    name='Satisfaction Threshold',
    kawa_type='decimal',
    initial_value=7.0,
)

model.create_variable(
    name='High Value Threshold',
    kawa_type='integer',
    initial_value=100000,
)

model.create_metric(
    name='total_clients',
    formula="""
    COUNT("client_id")
    """,
)

model.create_metric(
    name='total_contract_value',
    formula="""
    SUM("contract_value")
    """,
)

model.create_metric(
    name='average_satisfaction',
    formula="""
    AVG("satisfaction_score")
    """,
)

model.create_metric(
    name='high_satisfaction_clients',
    formula="""
    SUM(CASE WHEN "satisfaction_score" >= "Satisfaction Threshold" THEN 1 ELSE 0 END)
    """,
)

model.create_metric(
    name='high_value_clients',
    formula="""
    SUM(CASE WHEN "contract_value" >= "High Value Threshold" THEN 1 ELSE 0 END)
    """,
)

model.create_metric(
    name='at_risk_clients',
    formula="""
    SUM(CASE WHEN "satisfaction_score" < 5 AND "account_status" = 'Active' THEN 1 ELSE 0 END)
    """,
)

model.create_metric(
    name='average_monthly_revenue',
    formula="""
    AVG("monthly_revenue")
    """,
)

# -- MODEL SECTION: end


# -- DASHBOARD SECTION: start

overview_page = app.create_page('Client Overview')

explanation_col = overview_page.create_section('Dashboard Overview', 1)
explanation_col.text_widget(
    content='This dashboard provides comprehensive monitoring of your client portfolio. Track client satisfaction, contract values, and identify potential risks.\n\nThe dashboard is interactive through two key variables: the Satisfaction Threshold determines which clients are considered highly satisfied (impacts the High Satisfaction Clients indicator), while the High Value Threshold defines your premium client segment (affects the High Value Clients count).\n\nUse these controls to analyze different scenarios and adjust your client management strategies accordingly. Monitor satisfaction trends, geographic distribution, and industry performance to make data-driven decisions.\n\nThe At Risk Clients metric automatically identifies active clients with satisfaction scores below 5, helping you prioritize retention efforts.'
)

col1, col2, col3 = overview_page.create_section('Key Metrics', num_columns=3)

col1.indicator_chart(
    title='Total Clients',
    indicator='total_clients',
    aggregation='SUM',
    source=model,
)

col2.indicator_chart(
    title='Average Satisfaction Score',
    indicator='average_satisfaction',
    aggregation='SUM',
    source=model,
)

col3.indicator_chart(
    title='Total Contract Value ($)',
    indicator='total_contract_value',
    aggregation='SUM',
    source=model,
)

col1, col2 = overview_page.create_section('Client Segmentation', num_columns=2)

col1.indicator_chart(
    title='High Satisfaction Clients',
    indicator='high_satisfaction_clients',
    aggregation='SUM',
    source=model,
)

col2.indicator_chart(
    title='At Risk Clients',
    indicator='at_risk_clients',
    aggregation='SUM',
    source=model,
)

col1, col2 = overview_page.create_section('Revenue Analysis', num_columns=2)

col1.bar_chart(
    title='Total Contract Value by Industry',
    x='industry',
    y='contract_value',
    aggregation='SUM',
    show_values=True,
    source=model,
)

col2.pie_chart(
    title='Client Distribution by Account Status',
    labels='account_status',
    values='client_id',
    aggregation='COUNT',
    show_values=True,
    show_labels=True,
    source=model,
)

col1, col2 = overview_page.create_section('Geographic & Satisfaction Analysis', num_columns=2)

col1.bar_chart(
    title='Client Count by Country',
    x='country',
    y='client_id',
    aggregation='COUNT',
    show_values=True,
    source=model,
)

col2.scatter_chart(
    title='Contract Value vs Satisfaction Score',
    granularity='client_id',
    x='contract_value',
    y='satisfaction_score',
    color='industry',
    aggregation_color='COUNT',
    source=model,
)

col1, col2 = overview_page.create_section('Temporal & Support Analysis', num_columns=2)

col1.line_chart(
    title='Client Registrations Over Time',
    x='registration_date',
    y='client_id',
    aggregation='COUNT',
    time_sampling='YEAR_AND_MONTH',
    area=True,
    source=model,
)

col2.boxplot(
    title='Support Tickets Distribution by Industry',
    x='industry',
    y='support_tickets',
    source=model,
)

# -- DASHBOARD SECTION: end

app.publish()
