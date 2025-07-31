import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Bike Sharing",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚲 Dashboard Peminjaman Sepeda")
st.markdown("Analisis Data Bike Sharing di Washington DC (2011–2012)")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("day.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])

    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weather_map = {
        1: 'Clear',
        2: 'Cloudy',
        3: 'Light Rain/Snow',
        4: 'Heavy Rain/Snow'
    }

    df['season'] = df['season'].map(season_map)
    df['weathersit'] = df['weathersit'].map(weather_map)

    return df

# Load hour dataset untuk analisis per jam
@st.cache_data
def load_hour_data():
    hour_df = pd.read_csv("hour.csv")
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weather_map = {
        1: 'Clear',
        2: 'Cloudy',
        3: 'Light Rain/Snow',
        4: 'Heavy Rain/Snow'
    }
    
    hour_df['season'] = hour_df['season'].map(season_map)
    hour_df['weathersit'] = hour_df['weathersit'].map(weather_map)
    
    return hour_df

df = load_data()
hour_df = load_hour_data()

# Sidebar filter
st.sidebar.header("🔎 Filter Data")

min_date = df['dteday'].min()
max_date = df['dteday'].max()

start_date = st.sidebar.date_input("Mulai Tanggal", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.sidebar.date_input("Sampai Tanggal", min_value=min_date, max_value=max_date, value=max_date)

seasons = st.sidebar.multiselect("Pilih Musim", df['season'].unique(), default=df['season'].unique())
weathers = st.sidebar.multiselect("Pilih Cuaca", df['weathersit'].unique(), default=df['weathersit'].unique())

# Apply filter untuk data harian
filtered_df = df[
    (df['dteday'] >= pd.to_datetime(start_date)) &
    (df['dteday'] <= pd.to_datetime(end_date)) &
    (df['season'].isin(seasons)) &
    (df['weathersit'].isin(weathers))
].copy()

# Apply filter untuk data per jam
filtered_hour_df = hour_df[
    (hour_df['dteday'] >= pd.to_datetime(start_date)) &
    (hour_df['dteday'] <= pd.to_datetime(end_date)) &
    (hour_df['season'].isin(seasons)) &
    (hour_df['weathersit'].isin(weathers))
].copy()

# Statistik Ringkas
st.subheader("📊 Ringkasan Data")
col1, col2, col3 = st.columns(3)
col1.metric("Total Hari", len(filtered_df))
col2.metric("Total Peminjaman", int(filtered_df['cnt'].sum()))
col3.metric("Rata-rata Peminjaman", round(filtered_df['cnt'].mean(), 2))

st.markdown("---")

# Visualisasi 1 - Peminjaman per Musim
st.subheader("🌤️ Total Peminjaman per Musim")
fig1, ax1 = plt.subplots()
sns.barplot(data=filtered_df, x='season', y='cnt', estimator=sum, ax=ax1)
ax1.set_title("Total Peminjaman per Musim")
ax1.set_xlabel("Musim")
ax1.set_ylabel("Total Peminjaman")
st.pyplot(fig1)

# Visualisasi 2 - Pengaruh Cuaca (Pertanyaan 2 - Lengkap sesuai notebook)
st.subheader("🌦️ Pengaruh Cuaca terhadap Peminjaman")

# 2.1 Heatmap Korelasi
st.markdown("**2.1 Matriks Korelasi Variabel Cuaca dan Peminjaman**")
fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
correlation_matrix = filtered_df[['temp', 'atemp', 'hum', 'windspeed', 'cnt']].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax_corr)
ax_corr.set_title('Matriks Korelasi Variabel Cuaca dan Peminjaman')
st.pyplot(fig_corr)

# 2.2 Scatter Plots
st.markdown("**2.2 Hubungan Variabel Cuaca dengan Peminjaman**")
fig_scatter, ((ax1_scatter, ax2_scatter), (ax3_scatter, ax4_scatter)) = plt.subplots(2, 2, figsize=(12, 10))

# Suhu vs Peminjaman
ax1_scatter.scatter(filtered_df['temp'], filtered_df['cnt'], alpha=0.5)
ax1_scatter.set_xlabel('Suhu (Dinormalisasi)')
ax1_scatter.set_ylabel('Jumlah Peminjaman Sepeda')
ax1_scatter.set_title('Hubungan Suhu dengan Peminjaman Sepeda')

# Kelembapan vs Peminjaman
ax2_scatter.scatter(filtered_df['hum'], filtered_df['cnt'], alpha=0.5, color='green')
ax2_scatter.set_xlabel('Kelembapan')
ax2_scatter.set_ylabel('Jumlah Peminjaman Sepeda')
ax2_scatter.set_title('Hubungan Kelembapan dengan Peminjaman Sepeda')

# Kecepatan Angin vs Peminjaman
ax3_scatter.scatter(filtered_df['windspeed'], filtered_df['cnt'], alpha=0.5, color='red')
ax3_scatter.set_xlabel('Kecepatan Angin')
ax3_scatter.set_ylabel('Jumlah Peminjaman Sepeda')
ax3_scatter.set_title('Hubungan Kecepatan Angin dengan Peminjaman Sepeda')

# Boxplot Cuaca
sns.boxplot(data=filtered_df, x='weathersit', y='cnt', ax=ax4_scatter)
ax4_scatter.set_title('Distribusi Peminjaman berdasarkan Kondisi Cuaca')
ax4_scatter.set_xlabel('Kondisi Cuaca')
ax4_scatter.set_ylabel('Jumlah Peminjaman')
ax4_scatter.tick_params(axis='x', rotation=45)

plt.tight_layout()
st.pyplot(fig_scatter)

# 2.3 Analisis Kategori Suhu
st.markdown("**2.3 Analisis Peminjaman berdasarkan Kategori Suhu**")

# Kategorisasi peminjaman berdasarkan kondisi cuaca
filtered_df['temp_category'] = pd.cut(filtered_df['temp'],
    bins=[0, 0.2, 0.4, 0.6, 0.8, 1],
    labels=['Sangat Dingin', 'Dingin', 'Sedang', 'Hangat', 'Panas'])

# Rata-rata peminjaman per kategori suhu
peminjaman_per_suhu = filtered_df.groupby('temp_category')['cnt'].mean().sort_values(ascending=False)

fig_temp_cat, ax_temp_cat = plt.subplots(figsize=(10, 6))
peminjaman_per_suhu.plot(kind='bar', ax=ax_temp_cat, color='skyblue')
ax_temp_cat.set_title('Rata-rata Peminjaman Sepeda per Kategori Suhu')
ax_temp_cat.set_xlabel('Kategori Suhu')
ax_temp_cat.set_ylabel('Rata-rata Jumlah Peminjaman')
ax_temp_cat.tick_params(axis='x', rotation=45)
plt.tight_layout()
st.pyplot(fig_temp_cat)

# Insight statistik
st.markdown("**📊 Insight Statistik:**")
corr_cnt = filtered_df[['temp', 'atemp', 'hum', 'windspeed', 'cnt']].corr()['cnt']
st.write("**Korelasi dengan Jumlah Peminjaman:**")
st.write(f"- Suhu: {corr_cnt['temp']:.3f}")
st.write(f"- Suhu Terasa: {corr_cnt['atemp']:.3f}")
st.write(f"- Kelembapan: {corr_cnt['hum']:.3f}")
st.write(f"- Kecepatan Angin: {corr_cnt['windspeed']:.3f}")

st.write("**Rata-rata Peminjaman per Kategori Suhu:**")
for category, value in peminjaman_per_suhu.items():
    st.write(f"- {category}: {value:.0f}")

# Visualisasi 3 - Tren Bulanan
st.subheader("📈 Tren Peminjaman Sepeda Bulanan")
monthly_df = filtered_df.resample('M', on='dteday').agg({'cnt': 'sum'}).reset_index()
monthly_df['label'] = monthly_df['dteday'].dt.strftime('%Y-%b')

fig3, ax3 = plt.subplots(figsize=(10,5))
sns.lineplot(data=monthly_df, x='label', y='cnt', marker='o', ax=ax3)
ax3.set_title("Total Peminjaman per Bulan")
ax3.set_ylabel("Jumlah Peminjaman")
ax3.set_xlabel("Bulan")
plt.xticks(rotation=45)
st.pyplot(fig3)

# Visualisasi 4 - Hari Libur vs Hari Kerja (menggunakan data per jam)
st.subheader("📅 Perbandingan Peminjaman: Hari Libur vs Hari Kerja (per Jam)")

working_map = {0: 'Libur', 1: 'Hari Kerja'}
filtered_hour_df['workingday_label'] = filtered_hour_df['workingday'].map(working_map)

fig4, ax4 = plt.subplots()
sns.boxplot(data=filtered_hour_df, x='workingday_label', y='cnt', palette='Set2', ax=ax4)
ax4.set_title("Distribusi Jumlah Peminjaman per Jam: Hari Kerja vs Libur")
ax4.set_xlabel("Jenis Hari")
ax4.set_ylabel("Jumlah Peminjaman per Jam")
st.pyplot(fig4)

# Insight tambahan menggunakan data per jam
avg_working_hour = filtered_hour_df.groupby('workingday_label')['cnt'].mean().to_dict()
st.markdown(f"""
**💡 Insight Tambahan:**  
- Rata-rata peminjaman per jam pada **hari kerja**: `{avg_working_hour.get('Hari Kerja', 0):,.0f}`  
- Rata-rata peminjaman per jam pada **hari libur**: `{avg_working_hour.get('Libur', 0):,.0f}`
""")

st.markdown("---")
st.info("Gunakan filter di sebelah kiri untuk mengeksplorasi data secara interaktif 🎯")
