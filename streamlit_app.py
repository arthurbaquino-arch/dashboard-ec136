import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Painel EC 136/2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar os dados
@st.cache_data
def load_data(uploaded_file):
    try:
        # Tenta ler com ';' primeiro, depois com ',' para CSV
        if uploaded_file.name.endswith('.csv'):
            try:
                df = pd.read_csv(uploaded_file, decimal=',', sep=';')
            except Exception:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, decimal=',')
        else:
            # Para arquivos .xlsx
            df = pd.read_excel(uploaded_file)

        # Encontrar a linha do cabeçalho
        # Procura por uma linha que contenha a coluna "ENTE"
        header_row = df[df.apply(lambda row: 'ENTE' in row.values, axis=1)].index

        if not header_row.empty:
            header_index = header_row[0]
            df = pd.read_excel(uploaded_file, skiprows=header_index + 1)

            # Definir o cabeçalho
            new_header = df
