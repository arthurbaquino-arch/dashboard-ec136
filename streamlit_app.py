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
                df = pd.read_csv(uploaded_file, skiprows=9, decimal=',', sep=';', skipfooter=1, engine='python')
            except Exception:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, skiprows=9, decimal=',', skipfooter=1, engine='python')
        else:
            # Para arquivos .xlsx, pula as 9 primeiras linhas e a última
            df = pd.read_excel(uploaded_file, skiprows=9, skipfooter=1, engine='python')
            
        # Remove a primeira coluna, que parece estar vazia no arquivo
        df = df.iloc[:, 1:]

        # Identificar e remover colunas sem nome (geradas por erro de formatação)
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        df = df.drop(columns=unnamed_cols, errors='ignore')

        # Remover linhas que estejam completamente vazias
        df = df.dropna(how='all')

        # Garantir que a quantidade de colunas está correta antes de renomear
        if df.shape[1] != 13:
            raise ValueError(f"O arquivo tem {df.shape[1]} colunas, mas o esperado é 13. Por favor, verifique a estrutura.")
        
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

    except Exception as e:
        st.error(f"Houve um erro ao processar o arquivo: {e}")
        st.info("Por favor, verifique se a estrutura da planilha está correta.")
        st.stop()
        return None

# Layout da aplicação
st.title('📊 Painel de Análise - EC 136/2025')
st.markdown("""
Este dashboard foi gerado automaticamente para visualizar e analisar os dados da planilha de situação dos entes devedores.
Use o filtro na barra lateral para explorar os dados de forma interativa.
""")

# Upload de arquivo na barra lateral
st.sidebar.header("Passo 1: Envie a Planilha")
uploaded_file = st.sidebar.file_uploader("Selecione o arquivo .csv ou .xlsx", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        # Filtros na barra lateral (apenas ENTE)
        st.sidebar.header("Passo 2: Filtros")
        ente_options = ['Todos'] + sorted(df['ENTE'].dropna().unique())
        selected_entes = st.sidebar.multiselect('Selecione o(s) Ente(s)', options=ente_options, default=ente_options[0])

        # Aplicar filtros
        filtered_df = df.copy()
        if 'Todos' not in selected_entes:
            filtered_df = filtered_df[filtered_df['ENTE'].isin(selected_entes)]

        # Colunas de métricas
        st.header("Principais Indicadores")
        col1, col2, col3, col4 = st.columns(4)

        # Métricas
        total_divida = filtered_df['ENDIVIDAMENTO_TOTAL'].sum()
        total_precatorios = filtered_df['QTD_DE_PRECATORIOS'].sum()
        parcela_anual = filtered_df['PARCELA_ANUAL'].sum()
        saldo_a_pagar = filtered_df['SALDO_A_PAGAR'].sum()

        col1.metric("Endividamento Total", f"R$ {total_divida:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col2.metric("Qtd. de Precatórios", f"{total_precatorios:,.0f}".replace(",", "."))
        col3.metric("Parcela Anual", f"R$ {parcela_anual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col4.metric("Saldo a Pagar", f"R$ {saldo_a_pagar:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.markdown("---")

        # Gráfico de pizza de divisão da dívida
        st.header("Divisão da Dívida")
        divida_data = {
            'Tipo': ['Estoque em Mora', 'Estoque Vincendos'],
            'Valor': [filtered_df['ESTOQUE_EM_MORA'].sum(), filtered_df['ESTOQUE_VINCENDOS'].sum()]
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
        st.header("Tabela de Dados Detalhada")
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
                "DIVIDA_EM_MORA_RCL": "{:.2%}",
                "APLICADO": "{:.2%}",
                "QTD_DE_PRECATORIOS": "{:,.0f}"
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
