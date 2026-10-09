import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

def create_daily_rentals_df(df):
    daily_rentals_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",
        "registered": "sum",
        "casual": "sum"
    })
    daily_rentals_df = daily_rentals_df.reset_index()
    daily_rentals_df.rename(columns={
        "cnt": "rental_count",
        "registered": "registered_count",
        "casual": "casual_count"
    }, inplace=True)
    return daily_rentals_df


def create_workingday_df(df):
    daily_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",
        "registered": "sum",
        "casual": "sum",
        "workingday": "max"
    }).reset_index()
 
    oktober_desember_2011_df = daily_df[(daily_df['dteday'] >= '2011-10-01') & (daily_df['dteday'] <= '2011-12-31') & (daily_df['workingday'] == 1)]
    januari_maret_2012_df = daily_df[(daily_df['dteday'] >= '2012-01-01') & (daily_df['dteday'] <= '2012-03-31') & (daily_df['workingday'] == 1)]
 
    oktober_desember_2011_df["periode"] = "Okt-Des 2011"
    januari_maret_2012_df["periode"] = "Jan-Mar 2012"
 
    workingday_df = pd.merge(
        left=oktober_desember_2011_df,
        right=januari_maret_2012_df,
        how="outer"
    )
    workingday_df = workingday_df.groupby(by="periode")[["cnt", "registered", "casual"]].mean().reset_index()
    return workingday_df


def create_holiday_df(df):
    holiday_df = df[df.holiday == 1].groupby(by="hr").cnt.mean().reset_index()
    holiday_df.sort_values(by="cnt", ascending=True, inplace=True)
    holiday_df["hr"] = holiday_df["hr"].astype(str)
    return holiday_df

# Load data
all_df = pd.read_csv("main_data.csv")
 
datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])


#Membuat komponen filter
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
 
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
 
main_df = all_df[(all_df["dteday"] >= str(start_date)) &
                (all_df["dteday"] <= str(end_date))]
 
daily_rentals_df = create_daily_rentals_df(main_df)
workingday_df = create_workingday_df(main_df)
holiday_df = create_holiday_df(main_df)


#Menambah visual dashboard
st.header('Peminjaman Sepeda Dashboard :sparkles:')
 
st.subheader('Peminjaman Harian')
 
col1, col2, col3 = st.columns(3)
 
with col1:
    total_rentals = daily_rentals_df.rental_count.sum()
    st.metric("Total rentals", value=total_rentals)
 
with col2:
    total_registered = daily_rentals_df.registered_count.sum()
    st.metric("Total registered", value=total_registered)
 
with col3:
    total_casual = daily_rentals_df.casual_count.sum()
    st.metric("Total casual", value=total_casual)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rentals_df["dteday"],
    daily_rentals_df["rental_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

#membenarkan rentang biar tidak ngambil pertengahan hari misal rentang cuman 5 hari karena matplotlib
if len(daily_rentals_df) <= 31:
    ax.set_xticks(daily_rentals_df["dteday"])
 
st.pyplot(fig)

# Visual Menjawab Pertanyaan 1
st.subheader("Working Day: Oktober-Desember 2011 vs Januari-Maret 2012")
 
if workingday_df.empty:
    st.warning("Rentang waktu yang dipilih tidak mencakup periode Okt-Des 2011 atau Jan-Mar 2012.")
else:
    fig, ax = plt.subplots(figsize=(16, 8))
 
    sns.barplot(data=workingday_df, x="periode", y="cnt", label="Total (cnt)", color="green", errorbar=None, ax=ax)
    sns.barplot(data=workingday_df, x="periode", y="registered", label="Registered", color="blue", errorbar=None, ax=ax)
    sns.barplot(data=workingday_df, x="periode", y="casual", label="Casual", color="orange", errorbar=None, ax=ax)
 
    ax.set_title("Kontribusi Tipe Pengguna terhadap Peminjaman Sepeda (Working Day)", loc="center", fontsize=30)
    ax.set_xlabel("Periode", fontsize=25)
    ax.set_ylabel("Rata-Rata Jumlah Peminjaman", fontsize=25)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=20)
    ax.legend(fontsize=20)
 
    st.pyplot(fig)


# Visual Menjawab Pertanyaan 2
st.subheader("Jam Tersibuk pada Hari Libur")
 
if holiday_df.empty:
    st.warning("Tidak ada hari libur pada rentang waktu yang dipilih!")
else:
    fig, ax = plt.subplots(figsize=(16, 12))
 
    ax.barh(y=holiday_df["hr"], width=holiday_df["cnt"], color="#90CAF9")
    ax.set_title("Rata-Rata Peminjaman Sepeda per Jam pada Hari Libur", loc="center", fontsize=30)
    ax.set_xlabel("Rata-Rata Peminjaman (cnt)", fontsize=25)
    ax.set_ylabel("Jam (hr)", fontsize=25)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=20)
 
    st.pyplot(fig)
 
st.caption('Copyright (c) Hariz Hussain 2026')