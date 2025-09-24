import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
import base64

# Nome do arquivo de dados e da imagem no repositório
DATA_FILE = "PAINEL EC 136-2025.xlsx"
BRASAO_IMAGE = "BRASAO TJPE COLORIDO VERTICAL 1080X1080.png"

# Função para carregar a imagem e convertê-la para Base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode('utf-8')
    except FileNotFoundError:
        st.error(f"Arquivo de imagem não encontrado: {bin_file}")
        return None

# Adicionar CSS para o fundo cinza claro e o brasão como plano de fundo
def add_bg_from_local(image_file):
    bin_str = get_base64_of_bin_file(image_file)
    if bin_str:
        page_bg_img = '''
        <style>
        .main {
            background-color: #f0f2f6;
            background-image: url("data:image/png;base64,%s");
            background-repeat: no-repeat;
            background-size: 200px;
            background-position: left top;
            background-attachment: fixed;
        }
        .st-emotion-cache-183q192 {
            padding-top: 100px;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 0;
            margin-bottom: 0;
            padding-top: 0;
            padding-bottom: 0;
        }
        </style>
        ''' % bin_str
        st.markdown(page_bg_img, unsafe_allow_html=True)

# Configuração da página
st.set_page_config(
    page_title="Painel EC 136/2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adicionar o plano de fundo com o brasão
add_bg_from_local(BRASAO_IMAGE)

# Adicionar título e subtítulo
st.title("TRIBUNAL DE JUSTIÇA DE PERNAMBUCO ⚖️")
st.subheader("COORDENADORIA GERAL DE PRECATÓRIOS")

st.markdown("---")

# Botão para recarregar o cache
if st.button('Recarregar Dados 🔄'):
    st.cache_data.clear()
    st.rerun()

# Função para carregar os dados
@st.cache_data
def load_data():
    try:
        # Carrega o arquivo XLSX e pula as 9 primeiras linhas
        df = pd.read_excel(DATA_FILE, header=None)
            
        # Pula as 9 primeiras linhas e não remove a última
        df = df.iloc[9:].copy()
            
        # Remove a primeira coluna, que parece estar vazia no arquivo
        df = df.iloc[:, 1:]

        # Identificar e remover colunas sem nome (geradas por erro de formatação)
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        df = df.drop(columns=unnamed_cols, errors='ignore')

        # Remover linhas que estejam completamente vazias
        df = df.dropna(how='all')

        # Garantir que a quantidade de colunas está correta antes de renomear
        if df.shape[1] != 13:
            st.error(f"O arquivo tem {df.shape[1]} colunas, mas o esperado é 13. Por favor, verifique a estrutura.")
            st.stop()
        
        # Renomear colunas para facilitar o acesso
        df.columns = [
            'ENTE', 'ESTOQUE - EM MORA', 'ESTOQUE - VINCENDOS', 'ENDIVIDAMENTO TOTAL', 
            'QTD DE PRECATORIOS', 'RCL 2024', 'DIVIDA EM MORA / RCL', 
            'APLICADO', 'PARCELA ANUAL', 'APORTES', 'ESTORNO', 'SALDO A PAGAR',
            'SITUACAO DIVIDA'
        ]

        # Substituir valores '-' por NaN e converter para numérico
        df = df.replace('-', pd.NA)
        numeric_cols = [
            'ESTOQUE - EM MORA', 'ESTOQUE - VINCENDOS', 'ENDIVIDAMENTO TOTAL', 
            'QTD DE PRECATORIOS', 'RCL 2024', 'DIVIDA EM MORA / RCL', 
            'APLICADO', 'PARCELA ANUAL', 'APORTES', 'ESTORNO', 'SALDO A PAGAR'
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

        return df

    except Exception as e:
        st.error(f"Houve um erro ao processar o arquivo: {e}")
        st.info("Por favor, verifique se a estrutura da planilha está correta.")
        st.stop()
        return None

# Carrega os dados diretamente do repositório
df = load_data()
if df is not None:
    st.markdown("""
Este dashboard foi gerado automaticamente para visualizar e analisar os dados da planilha de situação dos entes devedores.
""")

    # Filtro no painel principal
    st.header("Filtros 🔎")
    
    # Lógica de ordenação com tratamento de acentos
    ente_list = df['ENTE'].dropna().unique()
    sorted_entes = sorted(ente_list, key=lambda s: unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8'))
    ente_options = ['Todos'] + sorted_entes
    
    selected_ente = st.selectbox('Selecione o Ente', options=ente_options)

    # Aplicar filtros
    filtered_df = df.copy()
    if selected_ente != 'Todos':
        filtered_df = filtered_df[filtered_df['ENTE'] == selected_ente]

    # Colunas de métricas
    st.header("Principais Indicadores 📊")
    col1, col2, col3, col4 = st.columns(4)

    # Métricas
    total_divida = filtered_df['ENDIVIDAMENTO TOTAL'].sum()
    total_precatorios = filtered_df['QTD DE PRECATORIOS'].sum()
    parcela_anual = filtered_df['PARCELA ANUAL'].sum()
    saldo_a_pagar = filtered_df['SALDO A PAGAR'].sum()

    col1.metric("Endividamento Total 💰", f"R$ {total_divida:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("Qtd. de Precatórios 📜", f"{total_precatorios:,.0f}".replace(",", "."))
    col3.metric("Parcela Anual 🗓️", f"R$ {parcela_anual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col4.metric("Saldo a Pagar 💸", f"R$ {saldo_a_pagar:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")

    # Gráfico de pizza de divisão da dívida
    st.header("Divisão da Dívida 📈")
    divida_data = {
        'Tipo': ['Estoque - Em Mora', 'Estoque - Vincendos'],
        'Valor': [filtered_df['ESTOQUE - EM MORA'].sum(), filtered_df['ESTOQUE - VINCENDOS'].sum()]
    }
    divida_df = pd.DataFrame(divida_data)
    
    fig_divida_pie = px.pie(
        divida_df,
        values='Valor',
        names='Tipo',
        title='Divisão da Dívida entre Estoque em Mora e Vincendos',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_divida_pie, use_container_width=True)

    st.markdown("---")
    
    # Tabela de dados
    st.header("Dados Gerais 📋")
    st.dataframe(filtered_df.style.set_table_styles([
        {'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'center')]}
    ]).format(
        {
            "ENDIVIDAMENTO TOTAL": "R$ {:,.2f}",
            "SALDO A PAGAR": "R$ {:,.2f}",
            "ESTOQUE - EM MORA": "R$ {:,.2f}",
            "ESTOQUE - VINCENDOS": "R$ {:,.2f}",
            "RCL 2024": "R$ {:,.2f}",
            "PARCELA ANUAL": "R$ {:,.2f}",
            "APORTES": "R$ {:,.2f}",
            "ESTORNO": "R$ {:,.2f}",
            "DIVIDA EM MORA / RCL": "{:.2%}",
            "APLICADO": "{:.2%}",
            "QTD DE PRECATORIOS": "{:,.0f}"
        }
    ).hide(axis="index"), use_container_width=True)

    # Botão para download
    csv_data = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download dos Dados Filtrados em CSV 📥",
        data=csv_data,
        file_name='dados_filtrados.csv',
        mime='text/csv',
    )
