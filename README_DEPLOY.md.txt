# Guia de Publicação do Dashboard Streamlit

Este guia explica como publicar o seu dashboard online de forma gratuita e rápida.

**Passo 1: Instale o Git e Crie uma Conta no GitHub**

1.  **Instale o Git:** Se você não tiver o Git instalado, baixe-o [aqui](https://git-scm.com/downloads) e siga as instruções.
2.  **Crie uma conta no GitHub:** Acesse [github.com](https://github.com) e crie uma conta gratuita.

**Passo 2: Crie um Repositório no GitHub**

1.  Faça login no GitHub e clique no botão verde **"New"** para criar um novo repositório.
2.  Dê um nome ao seu repositório (ex: `meu_dashboard_ec136`).
3.  Escolha a opção **"Public"** para que o Streamlit possa acessá-lo.
4.  Marque a caixa **"Add a README file"**.
5.  Clique em **"Create repository"**.

**Passo 3: Adicione seus Arquivos ao Repositório**

1.  Na página do seu novo repositório, clique em **"Add file"** e depois em **"Upload files"**.
2.  Arraste e solte os arquivos `streamlit_app.py` e `requirements.txt` para a área de upload.
3.  Na parte inferior da página, adicione uma mensagem curta (ex: "Adicionando arquivos do dashboard") e clique em **"Commit changes"**.

**Passo 4: Publicação no Streamlit Community Cloud**

1.  Acesse o [Streamlit Community Cloud](https://share.streamlit.io/) e faça login com sua conta do GitHub.
2.  No seu painel, clique em **"New app"** no canto superior direito.
3.  Preencha os detalhes do aplicativo:
    * **Repository:** Selecione o repositório que você acabou de criar.
    * **Branch:** Mantenha `main`.
    * **Main file path:** Digite `streamlit_app.py`.
4.  Clique em **"Deploy!"**.

O Streamlit levará alguns minutos para construir e publicar o seu aplicativo. Assim que terminar, você receberá um link público para o seu dashboard, que pode ser compartilhado com qualquer pessoa.

---

### Observação

Para atualizar o dashboard com novos dados, basta fazer o upload do arquivo `PAINEL EC 136-2025.xlsx - PLANILHA PEC 136.csv` diretamente no navegador, usando a interface do Streamlit. Se você atualizar o código, basta fazer um novo commit no GitHub.