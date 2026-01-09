import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path("/data/library.db")

# ---- Safety check -------------------------------------------------
if not DB_PATH.exists():
    st.error(f"Database not found at {DB_PATH}")
    st.stop()

# ---- DB helpers ---------------------------------------------------
@st.cache_data
def get_tables():
    with sqlite3.connect(DB_PATH) as conn:
        query = """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name;
        """
        return pd.read_sql(query, conn)["name"].tolist()

@st.cache_data
def load_table(table_name):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(f"SELECT * FROM {table_name}", conn)

# ---- UI -----------------------------------------------------------
st.title("📚 Library Metrics Viewer")

tables = get_tables()
if not tables:
    st.warning("No tables found in database.")
    st.stop()

table = st.selectbox("Select a table", tables)
df = load_table(table)

st.subheader(f"Table: `{table}`")
st.write(f"Rows: {len(df)} | Columns: {len(df.columns)}")
st.dataframe(df, use_container_width=True)

# ---- BASIC ANALYSIS: Dropped Records ------------------------------
if table == "books_dropped_records" and "drop_reason" in df.columns:
    st.divider()
    st.subheader("📉 Dropped Records Analysis")

    drop_counts = (
    df.groupby("drop_reason")
      .size()
      .reset_index(name="count")
      .sort_values("count", ascending=False)
    )


    st.write("Drop reason counts")
    st.dataframe(drop_counts, use_container_width=True)

    st.write("Drop reason distribution")
    st.pyplot(
        drop_counts
        .set_index("drop_reason")["count"]
        .plot.pie(autopct="%1.1f%%", ylabel="")
        .get_figure()
    )
