# -*- coding: utf-8 -*-
"""Untitled0.ipynb   

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1en-pd87SPtNEsAJgXXzT_ncTnde_TPM2
"""

# @title Default title text
# from google.colab import drive
# drive.mount('/content/drive')



import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import itertools
from prophet import Prophet
from plotly.subplots import make_subplots
import matplotlib.dates as mdates

data = pd.read_csv("C:/Users/Hp/OneDrive/Desktop/data.csv")
print(data.head())

data["Discount"] = (data['original_price'] - data['offer_price']) / data['original_price'] * 100

top_deals = data.sort_values(by="Discount", ascending=False)
deals = top_deals["name"][:15].value_counts()
label = deals.index
counts = top_deals["Discount"][:15].values
colors = ['gold','lightgreen']
fig = go.Figure(data=[go.Pie(labels=label, values=counts)])
fig.update_layout(title_text='Highest Discount Deals in the Flipkart Big Billion Days Sale')
fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=30,marker=dict(colors=colors, line=dict(color='black', width=3)))
fig.show()

highest_rated = data.sort_values(by="rating", ascending=False)
deals = highest_rated["name"][:10].value_counts()
label = deals.index
counts = highest_rated["rating"][:10].values
colors = ['gold','lightgreen']
fig = go.Figure(data=[go.Pie(labels=label, values=counts)])
fig.update_layout(title_text='Highest Rated Discount Deals in the Flipkart Big Billion Days Sale')
fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=30,marker=dict(colors=colors, line=dict(color='black', width=3)))
fig.show()

most_expensive = data.sort_values(by="offer_price", ascending=False)
deals = most_expensive["name"][:10].value_counts()
label = deals.index
counts = most_expensive["offer_price"][:10].values
colors = ['gold','lightgreen']
fig = go.Figure(data=[go.Pie(labels=label, values=counts)])
fig.update_layout(title_text='Most Expensive Offers in the Flipkart Big Billion Days Sale')
fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=30,marker=dict(colors=colors, line=dict(color='black', width=3)))
fig.show()

label = ["Total of Offer Prices in Sales", "Total of Original Prices (MRP)"]
counts = [sum(data["offer_price"]), sum(data["original_price"])]
colors = ['gold','lightgreen']
fig = go.Figure(data=[go.Pie(labels=label, values=counts)])
fig.update_layout(title_text='Total Discounts Offered Vs. MRP')
fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=30,marker=dict(colors=colors, line=dict(color='black', width=3)))
fig.show()

print("Cost of big billion days sale to flipkart on smartphones = ", 12876594 - 10522822)

print(data.head())

data['created_at'] = pd.to_datetime(data['created_at'])

# Select relevant columns for analysis
df = data[['created_at', 'name', 'offer_price']]

# Rename columns as per Prophet requirements (ds for date, y for target variable)
df = df.rename(columns={'created_at': 'ds', 'offer_price': 'y'})

# Handle missing values if any
df = df.dropna()

df['ds'] = df['ds'].dt.tz_localize(None)

# Initialize and fit the Prophet model
model = Prophet()
model.fit(df)

# Create a DataFrame for future dates to make predictions
future = model.make_future_dataframe(periods=365)
forecast = model.predict(future)
fig = px.line(forecast, x='ds', y='yhat', title='Flipkart Sales Forecast',labels={'yhat': 'Predicted Offer Price'},line_shape='linear', render_mode='svg')
fig.update_traces(line_color='rgb(59,63,10,69)', mode='lines+markers')

fig.update_layout(title_text='Flipkart Sales Forecast', title_x=0.5,xaxis_title='Date', yaxis_title='Offer Price',font=dict(family='Arial, sans-serif', size=12, color='blue'),paper_bgcolor='rgba(450,50,100,25)', plot_bgcolor='rgba(164,241,167,50)')

daily_sales = df.groupby(['ds', 'name']).sum().reset_index()

product_counts = daily_sales['name'].value_counts()
valid_products = product_counts[product_counts >= 2].index
filtered_sales = daily_sales[daily_sales['name'].isin(valid_products)]

# Initialize a dictionary to store Prophet models for each product
prophet_models = {}

for product in valid_products:
  product_data = filtered_sales[filtered_sales['name'] == product]
  model = Prophet()
  model.fit(product_data)
  prophet_models[product] = model

future_dates = pd.DataFrame({'ds': pd.date_range(start=daily_sales['ds'].max(), periods=365, freq='D')})

product_predictions = []

for product, model in prophet_models.items():
  future = model.make_future_dataframe(periods=365)
  forecast = model.predict(future)
  forecast['name'] = product  # Add product name to the forecast DataFrame
  product_predictions.append(forecast)

# Concatenate the product-wise forecasts into a single DataFrame
all_predictions = pd.concat(product_predictions, ignore_index=True)


# Find the dates with the highest predicted sales for each product
#best_selling_dates = all_predictions.loc[all_predictions.groupby('name')['yhat'].idxmax()]
fig = go.Figure()

# Iterate through each product for plotting
for idx, product in enumerate(valid_products):
  sales_distribution = all_predictions[all_predictions['name'] == product]
  fig.add_trace(go.Scatter(x=sales_distribution['ds'], y=sales_distribution['yhat'],
                           mode='lines', name=product,
                           line=dict(color=f'rgba({idx * 50 % 256}, {idx * 100 % 256}, {idx * 150 % 256}, 1)'),
                           ))
fig.update_layout(title='Sales Prediction for Different Products',
                  xaxis_title='Date',
                  yaxis_title='Predicted Sales',
                  legend_title='Products',
                  height=500,
                  width=1000)

# Visualize the products with the highest predicted sales using a bar chart
#fig = px.bar(best_selling_dates, x='name', y='yhat',
#title='Best Selling Products Forecast',
#labels={'yhat': 'Predicted Sales', 'name': 'Product Name'},
#color='yhat',
#color_continuous_scale='Viridis')


#fig.update_layout(title_text='Best Selling Products Forecast', title_x=0.5,
#xaxis_title='Product Name', yaxis_title='Predicted Sales',
#font=dict(family='Arial, sans-serif', size=12, color='RebeccaPurple'),
#paper_bgcolor='rgba(254, 254, 254, 0.8)', plot_bgcolor='rgba(0,0,0,0)')
# Show the interactive bar chart
fig.show()

projected_sales_revenue = all_predictions.copy()
for product in valid_products:
    projected_sales_revenue.loc[projected_sales_revenue['name'] == product, 'sales_revenue'] = projected_sales_revenue.loc[projected_sales_revenue['name'] == product, 'yhat'] * df[df['name'] == product]['y'].values[0]

total_sales_revenue = projected_sales_revenue.groupby('ds')['sales_revenue'].sum().reset_index()
# Plot the projected sales revenue for a specific product
plt.figure(figsize=(12, 6))
product = valid_products[0]  # Choose a specific product to plot
plt.bar(projected_sales_revenue[projected_sales_revenue['name'] == product]['ds'],
        projected_sales_revenue[projected_sales_revenue['name'] == product]['sales_revenue'],
        color='skyblue')
plt.xlabel('Date')
plt.ylabel('Projected Sales Revenue')
plt.title(f'Projected Sales Revenue for {product} in the Coming Year')

# Format the labels for total sales revenue
total_sales = total_sales_revenue['sales_revenue'].sum()

# Format x-axis as dates and show monthly ticks
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Calculate Mean Absolute Percentage Error (MAPE) for each product
mape_per_product = {}

for product in valid_products:
    actual_sales = df[df['name'] == product]['y'].values
    predicted_sales = projected_sales_revenue[projected_sales_revenue['name'] == product]['yhat'].values[:len(actual_sales)]

    # Ensure the lengths match before calculating MAPE
    if len(actual_sales) == len(predicted_sales):
        mape = np.mean(np.abs((actual_sales - predicted_sales) / actual_sales)) * 100
        mape_per_product[product] = mape
    else:
        print(f"Skipping MAPE calculation for {product}. Lengths of actual and predicted sales don't match.")

# Calculate MAPE for total sales revenue
actual_total_sales = total_sales_revenue['sales_revenue'].values[0]
predicted_total_sales = total_sales
# Calculate MAPE for total sales revenue
mape_total_sales = np.abs((actual_total_sales - predicted_total_sales) / actual_total_sales) * 100

mape_per_product, mape_total_sales
