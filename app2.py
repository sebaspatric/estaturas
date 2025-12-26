import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title("Ingreso de estaturas en clase 📊")

# --- Conexión a Google Sheets ---
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

sheet = None
try:
    creds_dict = st.secrets["gcp_service_account"]  # ✅ leer credenciales desde Secrets
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Estaturas").sheet1
except Exception as e:
    st.warning("⚠️ No se pudo conectar con Google Sheets. Se mostrará una tabla vacía.")
    st.text(f"Detalle técnico: {e}")

# --- Formulario ---
with st.form("form_estaturas"):
    nombre = st.text_input("Nombre del estudiante")
    estatura = st.number_input("Estatura (cm)", min_value=100, max_value=250)
    submitted = st.form_submit_button("Enviar")

# --- Guardar datos ---
if submitted:
    if sheet:
        try:
            sheet.append_row([nombre, estatura])
            st.success("✅ Datos enviados correctamente a Google Sheets")
        except Exception as e:
            st.error("❌ No se pudo guardar en Google Sheets")
            st.text(f"Detalle técnico: {e}")
    else:
        st.error("❌ No hay conexión con Google Sheets, los datos no se guardaron")

# --- Leer datos ---
if sheet:
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
    except Exception as e:
        st.error("❌ No se pudo leer datos de Google Sheets")
        st.text(f"Detalle técnico: {e}")
        df = pd.DataFrame(columns=["Nombre", "Estatura"])
else:
    df = pd.DataFrame(columns=["Nombre", "Estatura"])

# --- Mostrar tabla ---
st.subheader("Datos enviados por todos los estudiantes")
st.dataframe(df)

# --- Estadísticas y gráfico ---
if not df.empty:
    media = df["Estatura"].mean()
    desv = df["Estatura"].std()
    max_val = df["Estatura"].max()
    min_val = df["Estatura"].min()

    colA, colB, colC, colD = st.columns(4)
    colA.metric("📊 Media", f"{media:.2f}")
    colB.metric("📈 Des. Estan", f"{desv:.2f}")
    colC.metric("🔺 Máx", f"{max_val}")
    colD.metric("🔻 Mín", f"{min_val}")

 
    st.subheader("Distribución de estaturas")

    # --- Slider para elegir el tamaño del intervalo ---
    paso = st.slider("Tamaño del intervalo (cm)", min_value=1, max_value=10, value=5)

    # --- Construcción de intervalos y frecuencias ---
    intervalos = np.arange(100, 250, paso)
    freq, bins = np.histogram(df["Estatura"], bins=intervalos)

    mu, sigma = df["Estatura"].mean(), df["Estatura"].std()
    distrib = norm.pdf(intervalos[:-1], mu, sigma) * paso  # ajusta según el paso

    # --- Gráfico ---
    fig, ax1 = plt.subplots(figsize=(10,5))
    ax1.bar(intervalos[:-1], freq, width=paso, color="skyblue", alpha=0.6, label="Frecuencia")
    ax1.set_ylabel("Frecuencia", color="blue")
    ax1.set_xlabel("Intervalos (cm)")

    ax2 = ax1.twinx()
    ax2.plot(intervalos[:-1], distrib, color="red", marker="o", linewidth=2, label="Distribución Normal")
    ax2.set_ylabel("Distribución", color="red")

    fig.suptitle("Distribución Normal vs Frecuencia de Estaturas", fontsize=14)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    st.pyplot(fig)
