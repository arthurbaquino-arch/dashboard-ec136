# Dicas de Privacidade e Segurança

**Dados Privados no Streamlit Cloud**

O `streamlit_app.py` que gerei para você inclui um **botão de upload de arquivo**.

**Isso significa que o arquivo de dados original (o .csv) não precisa ser armazenado no seu repositório público do GitHub.**

O fluxo de trabalho recomendado para manter seus dados privados é:

1.  Siga o guia de deploy e publique o aplicativo (`streamlit_app.py` e `requirements.txt`) no Streamlit Community Cloud.
2.  Quando o aplicativo estiver online, ele solicitará que você faça o upload da sua planilha (`.csv` ou `.xlsx`) para visualizar os dados.
3.  Os dados da sua planilha serão processados na memória do aplicativo Streamlit e não serão armazenados permanentemente ou tornados públicos.

Se você tem planos de integrar o dashboard com uma fonte de dados privada, como uma planilha do Google Sheets que você sincroniza, é possível usar o Streamlit Cloud com um repositório privado, mas isso requer um processo de configuração mais avançado para autenticação.