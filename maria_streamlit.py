import requests
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="María – Oportunidades de Evaluación", layout="wide")

st.title("📋 María – Oportunidades de Evaluación Externa (ReliefWeb)")
st.caption("Agente de apoyo a consultorías – desarrollado por Fernando y ChatGPT")

# Palabras clave
keywords = ["evaluation", "assessment", "tdr"]

# Obtener datos desde la API de ReliefWeb
@st.cache_data(ttl=3600)
def cargar_datos():
    url = "https://api.reliefweb.int/v1/jobs"
    params = {
        "appname": "maria-agent",
        "profile": "full",
        "limit": 100,
        "filter": {
            "conditions": [
                {
                    "field": "title",
                    "value": keywords,
                    "operator": "OR"
                }
            ]
        }
    }

    response = requests.post(url, json=params)
    data = response.json()
    ofertas = data["data"]

    resultados = []
    for oferta in ofertas:
        fields = oferta["fields"]
        resultados.append({
            "Título": fields.get("title", ""),
            "Organización": fields.get("organization", [{}])[0].get("name", ""),
            "País": fields.get("country", [{}])[0].get("name", "No especificado"),
            "Fecha límite": fields.get("closing_date", "No especificada"),
            "Enlace": fields.get("url", "")
        })

    return pd.DataFrame(resultados)

df = cargar_datos()

# Filtros interactivos
st.sidebar.header("🔍 Filtros")
palabra_clave = st.sidebar.text_input("Buscar palabra en título")
pais = st.sidebar.selectbox("Filtrar por país", ["Todos"] + sorted(df["País"].unique().tolist()))
fecha_limite = st.sidebar.date_input("Mostrar hasta fecha límite", value=datetime.today())

# Aplicar filtros
df_filtrado = df.copy()

if palabra_clave:
    df_filtrado = df_filtrado[df_filtrado["Título"].str.contains(palabra_clave, case=False)]

if pais != "Todos":
    df_filtrado = df_filtrado[df_filtrado["País"] == pais]

df_filtrado["Fecha límite"] = pd.to_datetime(df_filtrado["Fecha límite"], errors="coerce")
df_filtrado = df_filtrado[df_filtrado["Fecha límite"] <= pd.to_datetime(fecha_limite)]

# Mostrar tabla
st.markdown(f"### {len(df_filtrado)} oportunidades encontradas")
st.dataframe(df_filtrado, use_container_width=True)

# Descargar CSV
st.download_button("⬇️ Descargar como CSV", df_filtrado.to_csv(index=False), file_name="maria_oportunidades.csv", mime="text/csv")
