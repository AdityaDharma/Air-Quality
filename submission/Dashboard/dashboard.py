import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_sum_PM2dot5_station_month_df(df):
    sum_PM2dot5_station_month_df = df.groupby(["station", "month"])['PM2.5'].sum().reset_index()
    return sum_PM2dot5_station_month_df

def create_sum_PM2dot5_station_year_df(df):
    sum_PM2dot5_station_year_df = df.groupby(["station", "year"])['PM2.5'].sum().reset_index()
    return sum_PM2dot5_station_year_df

def create_sum_PM2dot5_station_df(df):
    sum_PM2dot5_station_df = df.groupby(["station"])['PM2.5'].sum().reset_index()
    return sum_PM2dot5_station_df

all_df = pd.read_csv("all_data.csv")
all_df["datetime"] = pd.to_datetime(all_df[["year", "month", "day", "hour"]])
all_df = all_df.drop(["year", "month", "day", "hour"], axis=1)

def create_rfm_air_quality_df(df):
    rfm_df = df.groupby(by="station", as_index=False).agg({
        "datetime": "max",
        "PM2.5": "count",
        "CO": "sum"
    })
    
    rfm_df.columns = ["station", "max_datetime", "frequency", "monetary"]
    
    rfm_df["max_datetime"] = pd.to_datetime(rfm_df["max_datetime"]).dt.date
    recent_date = df["datetime"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_datetime"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_datetime", axis=1, inplace=True)
    
    return rfm_df

min_date = all_df["datetime"].min()
max_date = all_df["datetime"].max()

with st.sidebar:
    st.image("https://hlassets.paessler.com/common/files/graphics/iot/sub-visual_iot-monitoring_air-quality-monitoring-v1.png")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

main_df = all_df[(all_df["datetime"] >= start_date) & 
                (all_df["datetime"] <= end_date)]
main_df["month"] = main_df["datetime"].dt.month
main_df["year"] = main_df["datetime"].dt.year

sum_PM2dot5_station_month_df = create_sum_PM2dot5_station_month_df(main_df)
sum_PM2dot5_station_year_df = create_sum_PM2dot5_station_year_df(main_df)
sum_PM2dot5_station_df = create_sum_PM2dot5_station_df(main_df)
rfm_df = create_rfm_air_quality_df(main_df)

st.header('Data Air Quality')
st.subheader('Total PM2.5 per Bulan')
fig, ax = plt.subplots(figsize=(16, 8))
sns.lineplot(x='month', y='PM2.5', hue='station', data=sum_PM2dot5_station_month_df, marker='o', ax=ax)
ax.set_title('Total PM2.5 per Bulan')
ax.set_xlabel('Bulan')
ax.set_ylabel('Total PM2.5')
ax.legend(title='Stasiun')
st.pyplot(fig)

st.subheader('Total PM2.5 per Tahun')
fig, ax = plt.subplots(figsize=(16, 8))
sns.lineplot(x='year', y='PM2.5', hue='station', data=sum_PM2dot5_station_year_df, marker='o', ax=ax)
ax.set_title('Total PM2.5 per Tahun')
ax.set_xlabel('Tahun')
ax.set_ylabel('Total PM2.5')
ax.legend(title='Stasiun')
st.pyplot(fig)

st.subheader('Total PM2.5 per Stasiun')
fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(x='station', y='PM2.5', data=sum_PM2dot5_station_df, ax=ax)
ax.set_title('Total PM2.5 per Stasiun')
ax.set_xlabel('Stasiun')
ax.set_ylabel('Total PM2.5')
st.pyplot(fig)

st.subheader("Best Station Based on RFM Parameters")
    
col1, col2, col3 = st.columns(3)
    
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
    
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
    
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
    
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
    
sns.barplot(y="recency", x="station", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Station", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
    
sns.barplot(y="frequency", x="station", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Station", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
    
sns.barplot(y="monetary", x="station", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Station", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
    
st.pyplot(fig)