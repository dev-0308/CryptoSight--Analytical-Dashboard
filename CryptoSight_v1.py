import sqlite3
import requests
from datetime import datetime, timedelta
import pandas as pd
import panel as pn
import plotly.graph_objs as go
from sklearn.linear_model import LinearRegression
import numpy as np
import io

# ---------------- PANEL CONFIG ----------------
pn.extension(
    sizing_mode="stretch_width",
    design="material",
    extensions=["tabulator"]
)

DEBUG_MODE = True
DB_FILE = "crypto_data.db"
CRYPTO_LIST = ["bitcoin", "ethereum", "dogecoin", "solana", "tether"]
API_URL = "https://api.coingecko.com/api/v3/coins/{crypto}/market_chart/range"


def log_debug(msg):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")


# ---------------- DATABASE ----------------
def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for crypto in CRYPTO_LIST:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {crypto}_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL UNIQUE,
                price REAL,
                market_cap REAL,
                volume REAL
            )
        """)

    conn.commit()
    conn.close()


def fetch_crypto_data(crypto):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=365)).timestamp())

        response = requests.get(
            API_URL.format(crypto=crypto),
            params={
                "vs_currency": "usd",
                "from": start_time,
                "to": end_time
            }
        )
        response.raise_for_status()
        data = response.json()

        for i in range(len(data["prices"])):
            timestamp = datetime.utcfromtimestamp(
                data["prices"][i][0] / 1000
            ).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(f"""
                INSERT OR IGNORE INTO {crypto}_data
                (timestamp, price, market_cap, volume)
                VALUES (?, ?, ?, ?)
            """, (
                timestamp,
                data["prices"][i][1],
                data["market_caps"][i][1],
                data["total_volumes"][i][1]
            ))

        conn.commit()
        conn.close()

    except Exception as e:
        log_debug(f"Fetch error ({crypto}): {e}")


def remove_duplicate_data(crypto):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(f"""
        DELETE FROM {crypto}_data
        WHERE rowid NOT IN (
            SELECT MAX(rowid)
            FROM {crypto}_data
            GROUP BY timestamp
        )
    """)

    conn.commit()
    conn.close()


def get_data_from_db(crypto, days):
    conn = sqlite3.connect(DB_FILE)
    start_time = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    df = pd.read_sql_query(
        f"""
        SELECT timestamp, price, market_cap, volume
        FROM {crypto}_data
        WHERE timestamp >= ?
        ORDER BY timestamp
        """,
        conn,
        params=(start_time,)
    )

    conn.close()
    return df


# ---------------- DASHBOARD ----------------
def create_dashboard():
    crypto_dropdown = pn.widgets.Select(
        name="Cryptocurrency",
        options=CRYPTO_LIST
    )

    duration_dropdown = pn.widgets.Select(
        name="Duration (days)",
        options=[7, 30, 180, 365],
        value=7
    )

    download_button = pn.widgets.FileDownload(
        label="Download CSV",
        button_type="success",
        filename="crypto_data.csv",
        callback=lambda: io.StringIO("")
    )

    table = pn.widgets.Tabulator(
        pagination="remote",
        page_size=10,
        height=320,
        sizing_mode="stretch_width",
        disabled=True
    )

    plot_pane = pn.pane.Plotly(height=420)
    summary = pn.pane.Markdown()

    def update_dashboard(event=None):
        crypto = crypto_dropdown.value
        days = duration_dropdown.value

        df = get_data_from_db(crypto, days)

        if df.empty:
            plot_pane.object = None
            table.value = pd.DataFrame()
            summary.object = "No data available."
            return

        table.value = df

        # ----- Plot -----
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["price"],
            mode="lines",
            name="Price (USD)"
        ))

        fig.update_layout(
            template="plotly_dark",
            title=f"{crypto.capitalize()} Price Trend ({days} Days)",
            xaxis_title="Date",
            yaxis_title="Price (USD)"
        )

        plot_pane.object = fig

        # ----- Stats & Prediction -----
        min_price = df["price"].min()
        max_price = df["price"].max()

        X = np.arange(1, len(df) + 1).reshape(-1, 1)
        y = df["price"].values

        model = LinearRegression()
        model.fit(X, y)

        future_days = np.arange(1, days + 1).reshape(-1, 1)
        predicted_avg = np.mean(model.predict(future_days))

        summary.object = (
            f"## 📊 Market Summary\n\n"
            f"**Min Price:** ${min_price:.2f}  \n"
            f"**Max Price:** ${max_price:.2f}  \n"
            f"**Predicted Avg (Next {days} Days):** ${predicted_avg:.2f}"
        )

        # ----- CSV Download -----
        def generate_csv():
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            return buffer

        download_button.filename = f"{crypto}_{days}_days_data.csv"
        download_button.callback = generate_csv

    crypto_dropdown.param.watch(update_dashboard, "value")
    duration_dropdown.param.watch(update_dashboard, "value")
    update_dashboard()

    template = pn.template.MaterialTemplate(
        title="CryptoSight Dashboard"
    )

    template.main.append(
        pn.Column(
            pn.Card(
                pn.Row(crypto_dropdown, duration_dropdown, download_button),
                title="Controls",
                margin=(10, 10)
            ),
            pn.Card(
                plot_pane,
                title="Price Trend",
                margin=(10, 10)
            ),
            pn.Card(
                summary,
                title="Insights",
                margin=(10, 10)
            ),
            pn.Card(
                table,
                title="Historical Data",
                collapsible=True,
                margin=(10, 10)
            )
        )
    )

    return template


# ---------------- MAIN ----------------
def main():
    setup_database()

    for crypto in CRYPTO_LIST:
        fetch_crypto_data(crypto)
        remove_duplicate_data(crypto)

    app = create_dashboard()
    app.show()


if __name__ == "__main__":
    main()
