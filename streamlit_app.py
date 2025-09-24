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
    
    df = pd.read_csv(uploaded_file, skiprows=5, decimal=',')
    
    # Remover a primeira coluna extra que não tem nome
    df = df.iloc[:, 1:]

    # Limpeza e tratamento de dados
    # Remover colunas vazias
    df = df.dropna(axis=1, how='all')

    # Renomear colunas para facilitar o acesso
    df.columns = [
        'ENTE', 'ESTOQUE_EM_MORA', 'ESTOQUE_VINCENDOS', 'ENDIVIDAMENTO_TOTAL', 
        'QTD_DE_PRECATORIOS', 'RCL_2024', 'DIVIDA_EM_MORA_RCL', 
        'APLICADO', 'PARCELA_ANUAL', 'APORTES', 'ESTORNO', 'SALDO_A_PAGAR',
        'SITUACAO_DIVIDA'
    ]

    # Substituir valores '-' por NaN
    df = df.replace('-', pd.NA)

    # Converter colunas numéricas
    numeric_cols = [
        'ESTOQUE_EM_MORA', 'ESTOQUE_VINCENDOS', 'ENDIVIDAMENTO_TOTAL', 
        'QTD_DE_PRECATORIOS', 'RCL_2024', 'DIVIDA_EM_MORA_RCL', 
        'APLICADO', 'PARCELA_ANUAL', 'APORTES', 'ESTORNO', 'SALDO_A_PAGAR'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

    return df

# Layout da aplicação
st.title('📊 Painel de Análise - EC 136/2025')
st.markdown("""
Este dashboard foi gerado automaticamente para visualizar e analisar os dados da planilha de situação dos entes devedores.
Use os filtros na barra lateral para explorar os dados de forma interativa.
""")

# Upload de arquivo na barra lateral
st.sidebar.header("Passo 1: Envie a Planilha")
uploaded_file = st.sidebar.file_uploader("Selecione o arquivo .csv ou .xlsx", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = load_data(uploaded_file)
        else:
            # Para arquivos .xlsx, ler a primeira aba
            df = pd.read_excel(uploaded_file, skiprows=5)
            df.columns = [
                'ENTE', 'ESTOQUE_EM_MORA', 'ESTOQUE_VINCENDOS', 'ENDIVIDAMENTO_TOTAL', 
                'QTD_DE_PRECATORIOS', 'RCL_2024', 'DIVIDA_EM_MORA_RCL', 
                'APLICADO', 'PARCELA_ANUAL', 'APORTES', 'ESTORNO', 'SALDO_A_PAGAR',
                'SITUACAO_DIVIDA'
            ]
            numeric_cols = [
                'ESTOQUE_EM_MORA', 'ESTOQUE_VINCENDOS', 'ENDIVIDAMENTO_TOTAL', 
                'QTD_DE_PRECATORIOS', 'RCL_2024', 'DIVIDA_EM_MORA_RCL', 
                'APLICADO', 'PARCELA_ANUAL', 'APORTES', 'ESTORNO', 'SALDO_A_PAGAR'
            ]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')

    except Exception as e:
        st.error(f"Houve um erro ao processar o arquivo: {e}")
        st.info("Por favor, verifique se a estrutura da planilha está correta (5 linhas de cabeçalho antes dos dados).")
        st.stop()

    # Filtros na barra lateral
    st.sidebar.header("Passo 2: Filtros")
    ente_options = ['Todos'] + sorted(df['ENTE'].dropna().unique())
    selected_entes = st.sidebar.multiselect('Selecione o(s) Ente(s)', options=ente_options, default=ente_options[0])

    situacao_options = ['Todas'] + sorted(df['SITUACAO_DIVIDA'].dropna().unique())
    selected_situacao = st.sidebar.multiselect('Selecione a Situação', options=situacao_options, default=situacao_options[0])

    # Aplicar filtros
    filtered_df = df.copy()
    if 'Todos' not in selected_entes:
        filtered_df = filtered_df[filtered_df['ENTE'].isin(selected_entes)]
    if 'Todas' not in selected_situacao:
        filtered_df = filtered_df[filtered_df['SITUACAO_DIVIDA'].isin(selected_situacao)]

    # Colunas de métricas
    col1, col2, col3 = st.columns(3)

    # Métricas
    total_divida = filtered_df['ENDIVIDAMENTO_TOTAL'].sum()
    saldo_a_pagar = filtered_df['SALDO_A_PAGAR'].sum()
    total_precatorios = filtered_df['QTD_DE_PRECATORIOS'].sum()

    col1.metric("Endividamento Total", f"R$ {total_divida:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("Saldo a Pagar", f"R$ {saldo_a_pagar:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col3.metric("Total de Precatórios", f"{total_precatorios:,.0f}".replace(",", "."))

    st.markdown("---")

    # Gráficos
    st.header("Análise Visual dos Dados")
    col_graph1, col_graph2 = st.columns(2)

    with col_graph1:
        st.subheader("Top 10 Endividamento por Ente")
        top_10 = filtered_df.groupby('ENTE')['ENDIVIDAMENTO_TOTAL'].sum().nlargest(10).reset_index()
        fig_bar = px.bar(
            top_10,
            x='ENDIVIDAMENTO_TOTAL',
            y='ENTE',
            title='Top 10 Envidamentos Totais',
            orientation='h',
            labels={'ENTE': 'Ente', 'ENDIVIDAMENTO_TOTAL': 'Endividamento Total'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_graph2:
        st.subheader("Distribuição por Situação")
        situacao_counts = filtered_df['SITUACAO_DIVIDA'].value_counts().reset_index()
        situacao_counts.columns = ['Situacao', 'Contagem']
        fig_pie = px.pie(
            situacao_counts,
            values='Contagem',
            names='Situacao',
            title='Distribuição da Situação da Dívida',
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")

    # Tabela de dados
    st.subheader("Tabela de Dados Detalhada")
    st.dataframe(filtered_df.style.format(
        {
            "ENDIVIDAMENTO_TOTAL": "R$ {:,.2f}",
            "SALDO_A_PAGAR": "R$ {:,.2f}",
            "ESTOQUE_EM_MORA": "R$ {:,.2f}",
            "ESTOQUE_VINCENDOS": "R$ {:,.2f}",
            "RCL_2024": "R$ {:,.2f}",
            "PARCELA_ANUAL": "R$ {:,.2f}",
            "APORTES": "R$ {:,.2f}",
            "ESTORNO": "R$ {:,.2f}",
            "DIVIDA_EM_MORA_RCL": "{:,.5f}",
            "APLICADO": "{:,.2f}"
        }
    ).hide(axis="index"), use_container_width=True)

    # Botão para download
    csv_data = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download dos Dados Filtrados em CSV",
        data=csv_data,
        file_name='dados_filtrados.csv',
        mime='text/csv',
    )
else:
    st.info("Por favor, faça o upload da sua planilha para começar.")