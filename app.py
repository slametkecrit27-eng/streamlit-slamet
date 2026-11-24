import pickle
import pandas as pd
import streamlit as st

# ---------- Konfigurasi halaman ----------
st.set_page_config(
    page_title="Valuasi Mobil Bekas",
    page_icon="🚘",
    layout="wide"
)

# ---------- Load model (Aman dengan cache agar tidak reload berulang) ----------
@st.cache_resource
def load_model():
    return pickle.load(open("estimasi_mobil.sav", "rb"))

model = load_model()
KURS = 20000  # 1 Pound ≈ Rp20.000, ganti sesuai kurs terbaru

def rupiah(x):
    return "Rp " + f"{x:,.0f}".replace(",", ".")

# ---------- CSS Custom (Tema Slate Dark & Amber/Emerald) ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.block-container {
    padding-top: 2rem;
    max-width: 1050px;
}

/* Header Banner */
.banner-box {
    background: linear-gradient(120deg, #0f172a 0%, #1e293b 60%, #065f46 100%);
    padding: 32px 36px;
    border-radius: 20px;
    color: #f8fafc;
    border: 1px solid #334155;
    margin-bottom: 28px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
}
.banner-badge {
    display: inline-block;
    background: rgba(16, 185, 129, 0.2);
    color: #34d399;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
    border: 1px solid rgba(52, 211, 153, 0.3);
}
.banner-box h1 {
    margin: 0;
    font-size: 2.1rem;
    font-weight: 800;
    color: #ffffff;
}
.banner-box p {
    margin: 8px 0 0;
    color: #cbd5e1;
    font-size: 0.98rem;
}

/* Kartu Hasil Prediksi */
.result-card {
    background: linear-gradient(145deg, #064e3b, #022c22);
    border: 1px solid #10b981;
    border-radius: 20px;
    padding: 28px 24px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(6, 78, 59, 0.25);
    margin-bottom: 16px;
}
.result-title {
    color: #a7f3d0;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}
.result-idr {
    color: #ffffff;
    font-size: 2.2rem;
    font-weight: 800;
    margin: 8px 0;
}
.result-gbp {
    display: inline-block;
    background: rgba(255, 255, 255, 0.12);
    color: #6ee7b7;
    padding: 4px 14px;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
}

/* Placeholder sebelum klik tombol */
.empty-card {
    border: 2px dashed #475569;
    border-radius: 20px;
    padding: 45px 24px;
    text-align: center;
    color: #94a3b8;
    background: rgba(30, 41, 59, 0.25);
}

/* Tombol Submit */
div.stFormSubmitButton > button {
    width: 100%;
    background: linear-gradient(90deg, #10b981, #059669);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 14px;
    font-weight: 700;
    font-size: 1.05rem;
    transition: all 0.2s ease;
    margin-top: 8px;
}
div.stFormSubmitButton > button:hover {
    background: linear-gradient(90deg, #059669, #047857);
    color: white;
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

# ---------- Header Banner ----------
st.markdown("""
<div class="banner-box">
    <div class="banner-badge">MACHINE LEARNING • LINEAR REGRESSION</div>
    <h1>🚘 Kalkulator Valuasi Mobil Bekas</h1>
    <p>Masukkan spesifikasi kendaraan Toyota bekas untuk menghitung estimasi nilai jual secara instan.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Layout 2 Kolom Utama (Kiri: Form, Kanan: Hasil) ----------
col_kiri, col_kanan = st.columns([1.25, 1], gap="large")

with col_kiri:
    with st.form("form_mobil"):
        st.subheader("🛠️ Spesifikasi Kendaraan")
        c1, c2 = st.columns(2)
        with c1:
            year = st.number_input("Tahun Produksi", min_value=1990, max_value=2026, value=2019)
            tax = st.number_input("Pajak Tahunan (£)", min_value=0, value=145)
            engineSize = st.number_input("Kapasitas Mesin (L)", min_value=0.0, value=1.5, step=0.1)
        with c2:
            mileage = st.number_input("Jarak Tempuh (mil)", min_value=0, value=5000, step=500)
            mpg = st.number_input("Efisiensi BBM (mpg)", min_value=0.0, value=50.0, step=0.5)

        submit = st.form_submit_button("⚡ Hitung Estimasi Harga")

with col_kanan:
    st.subheader("💰 Hasil Valuasi")
    if submit:
        data = pd.DataFrame(
            [[year, mileage, tax, mpg, engineSize]],
            columns=["year", "mileage", "tax", "mpg", "engineSize"]
        )
        harga = model.predict(data)[0]

        if harga <= 0:
            st.error("⚠️ Kombinasi data berada di luar jangkauan prediksi model. Silakan sesuaikan angka input.")
        else:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-title">Estimasi Harga Pasar</div>
                <div class="result-idr">{rupiah(harga * KURS)}</div>
                <div class="result-gbp">Setara £{harga:,.2f} GBP</div>
            </div>
            """, unsafe_allow_html=True)

            # Ringkasan Metrik
            m1, m2, m3 = st.columns(3)
            m1.metric("Usia", f"{2026 - year} Thn")
            m2.metric("Odometer", f"{mileage:,} mi".replace(",", "."))
            m3.metric("Mesin", f"{engineSize} L")
    else:
        st.markdown("""
        <div class="empty-card">
            <h4 style="margin-bottom:8px;">Belum Ada Perhitungan</h4>
            <p style="font-size:0.9rem; margin:0;">Lengkapi spesifikasi mobil di panel sebelah kiri, lalu tekan tombol <b>Hitung Estimasi Harga</b>.</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ---------- Informasi Tambahan di Bagian Bawah (Pengganti Sidebar) ----------
tab1, tab2 = st.tabs(["ℹ️ Tentang Model", "💱 Informasi Kurs & Fitur"])
with tab1:
    st.write(
        "Aplikasi ini menggunakan algoritma **Regresi Linear (Linear Regression)** yang dilatih menggunakan "
        "dataset historis penjualan mobil bekas Toyota untuk memprediksi harga berdasarkan 5 parameter utama."
    )
with tab2:
    st.write(f"- **Konversi Kurs Aktif:** `1 GBP (£) = {rupiah(KURS)}`")
    st.write("- **Parameter Input:** Tahun (`year`), Jarak Tempuh (`mileage`), Pajak (`tax`), Konsumsi BBM (`mpg`), dan Ukuran Mesin (`engineSize`).")

st.caption("Dibuat dengan Python • Scikit-learn • Streamlit")