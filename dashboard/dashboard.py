import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# =========================================================
# KONFIGURASI DASHBOARD
# =========================================================

st.set_page_config(
    page_title="Dashboard Analisis E-Commerce Olist",
    page_icon="📊",
    layout="wide"
)

sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 5)

# =========================================================
# LOAD DATA
# =========================================================

delivery_df = pd.read_csv("dashboard/main_data.csv")
category_df = pd.read_csv("dashboard/category_data.csv")

# =========================================================
# PREPROCESSING
# =========================================================

# Membuat delay_group agar sama dengan notebook
bins = [-100, 0, 3, 7, 14, 30, 100]
labels = [
    "On Time",
    "1-3 Days",
    "4-7 Days",
    "8-14 Days",
    "15-30 Days",
    ">30 Days"
]

delivery_df["delay_group"] = pd.cut(
    delivery_df["delivery_delay"],
    bins=bins,
    labels=labels
)

# =========================================================
# HEADER
# =========================================================

st.title("📊 Dashboard Analisis E-Commerce Olist")

st.markdown("""
Dashboard ini dibuat untuk menjawab business question:

1. Pengaruh keterlambatan pengiriman terhadap penurunan review score pelanggan.
2. Kategori produk dengan penurunan penjualan >10% dan review score <4.
""")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("🔎 Filter Dashboard")

selected_status = st.sidebar.multiselect(
    "Pilih Status Pengiriman",
    options=delivery_df["delivery_status"].unique(),
    default=delivery_df["delivery_status"].unique()
)

selected_delay = st.sidebar.slider(
    "Maksimum Delivery Delay",
    min_value=int(delivery_df["delivery_delay"].min()),
    max_value=int(delivery_df["delivery_delay"].max()),
    value=int(delivery_df["delivery_delay"].max())
)

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = delivery_df[
    (delivery_df["delivery_status"].isin(selected_status)) &
    (delivery_df["delivery_delay"] <= selected_delay)
]

# =========================================================
# METRICS
# =========================================================

st.subheader("📌 Statistik Utama")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Orders",
    f"{len(filtered_df):,}"
)

col2.metric(
    "Average Review Score",
    round(filtered_df["review_score"].mean(), 2)
)

col3.metric(
    "Average Delivery Delay",
    round(filtered_df["delivery_delay"].mean(), 2)
)

# =========================================================
# BUSINESS QUESTION 1
# =========================================================

st.header("1️⃣ Pengaruh Keterlambatan Pengiriman terhadap Review Score")

# =========================================================
# VISUALISASI BARPLOT REVIEW
# =========================================================

review_comparison_df = filtered_df.groupby(
    "delivery_status"
)["review_score"].mean().reset_index()

fig1, ax1 = plt.subplots(figsize=(8, 5))

sns.barplot(
    data=review_comparison_df,
    x="delivery_status",
    y="review_score",
    ax=ax1
)

ax1.set_title(
    "Average Review Score Based on Delivery Status (2017-2018)"
)

ax1.set_xlabel("Delivery Status")
ax1.set_ylabel("Average Review Score")

for container in ax1.containers:
    ax1.bar_label(container, fmt="%.2f")

st.pyplot(fig1)

# =========================================================
# INSIGHT REVIEW DROP
# =========================================================

if len(review_comparison_df) == 2:

    on_time_review = review_comparison_df[
        review_comparison_df["delivery_status"] == "On Time"
    ]["review_score"].values[0]

    late_review = review_comparison_df[
        review_comparison_df["delivery_status"] == "Late"
    ]["review_score"].values[0]

    review_drop = on_time_review - late_review

    st.markdown(f"""
### Insight

- Pengiriman tepat waktu memiliki rata-rata review score sebesar **{on_time_review:.2f}**
- Pengiriman terlambat memiliki rata-rata review score sebesar **{late_review:.2f}**
- Terjadi penurunan review score sebesar **{review_drop:.2f} poin**
""")

# =========================================================
# VISUALISASI LINEPLOT DELAY GROUP
# =========================================================

delay_group_df = filtered_df.groupby(
    "delay_group"
)["review_score"].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(10, 5))

sns.lineplot(
    data=delay_group_df,
    x="delay_group",
    y="review_score",
    marker="o",
    ax=ax2
)

ax2.set_title("Trend of Review Score Based on Delivery Delay")
ax2.set_xlabel("Delay Group")
ax2.set_ylabel("Average Review Score")

st.pyplot(fig2)

st.markdown("""
### Insight

Semakin lama keterlambatan pengiriman,
rata-rata review score pelanggan cenderung semakin rendah.
""")

# =========================================================
# BUSINESS QUESTION 2
# =========================================================

st.header("2️⃣ Kategori Produk dengan Penurunan Penjualan >10%")

# =========================================================
# BARPLOT SALES DECLINE
# =========================================================

fig3, ax3 = plt.subplots(figsize=(12, 6))

sns.barplot(
    data=category_df.sort_values(by="sales_change_pct"),
    x="sales_change_pct",
    y="product_category_name_english",
    ax=ax3
)

ax3.set_title(
    "Product Categories with Sales Decline >10% and Review Score <4"
)

ax3.set_xlabel("Sales Change Percentage (%)")
ax3.set_ylabel("Product Category")

for container in ax3.containers:
    ax3.bar_label(container, fmt="%.1f%%")

st.pyplot(fig3)

st.markdown("""
### Insight

Kategori produk pada visualisasi di atas mengalami:

- Penurunan penjualan lebih dari 10%
- Memiliki review score di bawah 4

Hal ini menunjukkan adanya hubungan antara rendahnya kepuasan pelanggan dengan penurunan performa penjualan produk.
""")

# =========================================================
# PERBANDINGAN SALES 2017 VS 2018
# =========================================================

comparison_sales_df = category_df.melt(
    id_vars="product_category_name_english",
    value_vars=["sales_2017", "sales_2018"],
    var_name="year",
    value_name="sales"
)

category_order = category_df.sort_values(
    by="sales_change_pct"
)["product_category_name_english"]

fig4, ax4 = plt.subplots(figsize=(14, 8))

sns.barplot(
    data=comparison_sales_df,
    y="product_category_name_english",
    x="sales",
    hue="year",
    order=category_order,
    ax=ax4
)

ax4.set_title(
    "Sales Comparison Between 2017 and 2018",
    fontsize=16,
    fontweight="bold"
)

ax4.set_xlabel("Total Sales")
ax4.set_ylabel("Product Category")

ax4.ticklabel_format(style='plain', axis='x')

for container in ax4.containers:
    ax4.bar_label(
        container,
        fmt="%.0f",
        padding=3,
        fontsize=8
    )

plt.tight_layout()

st.pyplot(fig4)

# =========================================================
# DATAFRAME
# =========================================================

with st.expander("📄 Lihat Data Delivery"):
    st.dataframe(filtered_df)

with st.expander("📄 Lihat Data Kategori Produk"):
    st.dataframe(category_df)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Proyek Analisis Data E-Commerce Olist - Dicoding"
)