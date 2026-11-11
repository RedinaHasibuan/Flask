import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
df = pd.read_csv("data/coffeshop.csv")

# Menambahkan kolom pendapatan (revenue)
df["revenue"] = df["transaction_qty"] * df["unit_price"]

def filter_data():
    """Ambil filter ?lokasi=... dari URL (opsional)."""
    data = df
    lokasi = request.args.get("lokasi", type=str)
    if lokasi:
        data = data[data["store_location"] == lokasi]
    return data

@app.route("/")
def dashboard():
    # Mengambil daftar lokasi unik untuk opsi filter di frontend
    daftar_lokasi = sorted(df["store_location"].dropna().unique().tolist())
    return render_template("dashboard.html", daftar_lokasi=daftar_lokasi)

@app.route("/api/ringkasan")
def ringkasan():
    data = filter_data()
    return jsonify(
        total_transaksi=int(len(data)),
        total_pendapatan=round(float(data["revenue"].sum()), 2),
        rata_rata_qty=round(float(data["transaction_qty"].mean()), 1),
    )

@app.route("/api/pendapatan-kategori")
def pendapatan_kategori():
    # Menggantikan route rata_prodi
    hasil = filter_data().groupby("product_category")["revenue"].sum().round(2)
    return jsonify(labels=hasil.index.tolist(), data=hasil.tolist())

@app.route("/api/top-produk")
def top_produk():
    # Menggantikan route distribusi-grade (mengambil 5 tipe produk paling sering dibeli)
    hasil = filter_data()["product_type"].value_counts().head(5)
    return jsonify(labels=hasil.index.tolist(), data=hasil.tolist())

@app.route("/api/tren-harian")
def tren_harian():
    # Menggantikan route tren-semester (melihat pendapatan per tanggal)
    hasil = filter_data().groupby("transaction_date")["revenue"].sum().round(2)
    return jsonify(
        labels=hasil.index.tolist(),
        datasets=[{"label": "Pendapatan Harian", "data": hasil.tolist()}],
    )

@app.route("/api/jam-sibuk")
def jam_sibuk():
    data = filter_data().copy()
    # Mengambil angka jam dari transaction_time (contoh "7:06:11" menjadi 7)
    data['hour'] = data['transaction_time'].astype(str).str.split(':').str[0].astype(int)
    hasil = data.groupby('hour')['transaction_qty'].sum().sort_index()
    
    # Memformat label jam agar lebih rapi (contoh: 7 menjadi "07:00")
    labels = [f"{str(h).zfill(2)}:00" for h in hasil.index]
    return jsonify(
        labels=labels,
        datasets=[{"label": "Cup Terjual", "data": hasil.tolist()}]
    )

if __name__ == "__main__":
    app.run(debug=True)