# 📜 Consulta Pública: Estatuto AMABRE

Este é o repositório da plataforma interativa de consulta pública para a revisão do estatuto da **Associação de Moradores e Amigos do Bairro Bom Retiro (AMABRE)** de Blumenau/SC.

A plataforma permite que os moradores se identifiquem, analisem e votem em cada artigo do estatuto de forma simples e rápida, permitindo inclusive o envio de feedbacks por áudio ou texto.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **Streamlit** (Interface Web)
* **Turso / libSQL** (Banco de Dados na Nuvem para as respostas)
* **Supabase** (Armazenamento em Nuvem para os arquivos de áudio gravados)

---

## 📁 Estrutura de Arquivos

* `app.py`: O código-fonte principal da aplicação Streamlit.
* `data.py`: Contém a lista completa com todos os artigos do estatuto e as ruas do bairro Bom Retiro.
* `requirements.txt`: Lista de dependências do Python para a aplicação funcionar.
* `.gitignore`: Evita o envio de chaves privadas, logs e pastas locais (como o ambiente virtual) para o GitHub.

---

## 🚀 Como Executar Localmente

1. **Clone o seu repositório do GitHub:**
   ```bash
   git clone <link-do-seu-repositorio>
   cd Estatuto_AMABRE
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # No Windows (PowerShell)
   source .venv/bin/activate # No Linux/macOS
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure os segredos locais:**
   Crie uma pasta chamada `.streamlit` e, dentro dela, um arquivo `secrets.toml`:
   ```toml
   # .streamlit/secrets.toml
   TURSO_URL = "https://amabre-db-olafotte.aws-us-east-1.turso.io"
   TURSO_AUTH_TOKEN = "SEU_TOKEN_DO_TURSO"

   SUPABASE_URL = "https://heehxkvwazudjvnzzies.supabase.co"
   SUPABASE_KEY = "SUA_CHAVE_DO_SUPABASE"
   ```

5. **Rode o Streamlit:**
   ```bash
   streamlit run app.py
   ```

---

## 🌐 Como Publicar no Streamlit Community Cloud

### 1. Criar o Repositório no GitHub
Se você ainda não enviou os arquivos para o GitHub, rode os seguintes comandos no terminal do seu projeto:

```bash
# Inicializa o repositório Git local
git init

# Adiciona todos os arquivos (o .gitignore evitará o envio do .venv e secrets.toml)
git add .

# Faz o primeiro commit
git commit -m "First commit: app structure, data, requirements"

# Renomeia a branch principal para main
git branch -M main

# Associa ao seu repositório remoto criado no GitHub
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git

# Envia os arquivos
git push -u origin main
```

### 2. Implantar no Streamlit Cloud
1. Acesse [share.streamlit.io](https://share.streamlit.io/) e faça login com sua conta do GitHub.
2. Clique em **New app** (Novo app).
3. Selecione o repositório (`NOME_DO_REPOSITORIO`), a branch (`main`) e o arquivo principal (`app.py`).
4. **Configurar os Segredos (Secrets):**
   * Antes de clicar em Deploy, clique em **Advanced settings...** (Configurações Avançadas).
   * Na seção **Secrets**, cole o conteúdo abaixo, preenchendo com as suas chaves reais:
     ```toml
     TURSO_URL = "https://amabre-db-olafotte.aws-us-east-1.turso.io"
     TURSO_AUTH_TOKEN = "SUA_TURSO_AUTH_TOKEN_AQUI"

     SUPABASE_URL = "https://heehxkvwazudjvnzzies.supabase.co"
     SUPABASE_KEY = "SUA_SUPABASE_KEY_AQUI"
     ```
5. Clique em **Deploy!** 🚀
