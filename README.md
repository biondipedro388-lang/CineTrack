# 🎬 CineTrack

**Seus filmes, suas séries, sua história.**

O CineTrack é uma aplicação web desenvolvida em Python com Streamlit, criada para organizar filmes e séries em uma biblioteca pessoal.

Integrado à API do TMDB, o sistema permite explorar títulos, consultar informações detalhadas, gerenciar uma coleção pessoal, registrar avaliações e acompanhar o histórico de filmes assistidos.

## ✨ Funcionalidades

- 🎞️ Catálogo de filmes e séries integrado ao TMDB.
- 📚 Biblioteca pessoal para organizar seus títulos.
- 🏷️ Organização por status: Quero assistir, Assistindo e Concluído.
- ⭐ Avaliações pessoais dos títulos.
- ❤️ Sistema de favoritos.
- 🔎 Consulta de sinopses, notas, pôsteres e informações detalhadas.
- 🎥 Exibição de trailers e vídeos.
- 🎭 Consulta de elenco e equipe de produção.
- 📊 Painel de estatísticas da coleção.
- 📖 Diário para registrar filmes assistidos, avaliações, datas e comentários.
- 🔐 Cadastro e autenticação de usuários com Supabase.
- 💾 Persistência de dados com SQLite.
- 🎨 Interface personalizada com CSS.

## 🛠️ Tecnologias utilizadas

- **Python** — lógica e desenvolvimento da aplicação.
- **Streamlit** — construção da interface web.
- **SQLite** — armazenamento de dados.
- **Supabase** — autenticação de usuários.
- **TMDB API** — consulta de informações sobre filmes e séries.
- **Requests** — comunicação com APIs externas.
- **HTML e CSS** — personalização visual.
- **Git e GitHub** — versionamento e hospedagem do código.

## 📁 Estrutura do projeto

```text
CineTrack/
├── .streamlit/
│   └── secrets.toml
├── components/
│   └── navbar.py
├── pages/
│   ├── 1_Catalogo.py
│   ├── 2_Minha_Colecao.py
│   ├── 3_Detalhes.py
│   ├── 4_Estatisticas.py
│   └── 5_Diario.py
├── services/
│   ├── database.py
│   └── supabase_client.py
├── .gitignore
├── app.py
├── styles.css
└── README.md
```

## ⚙️ Como executar o projeto

### 1. Pré-requisitos

- Python instalado.
- Git instalado.
- Conta e chave de API do [The Movie Database (TMDB)](https://www.themoviedb.org/).
- Projeto configurado no [Supabase](https://supabase.com/).

### 2. Clone o repositório

```bash
git clone https://github.com/biondipedro388-lang/CineTrack.git
cd CineTrack
```

### 3. Crie e ative um ambiente virtual

No Windows, usando PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Instale as dependências

```powershell
python -m pip install streamlit requests supabase
```

### 5. Configure as credenciais

Crie o arquivo `.streamlit/secrets.toml` e configure suas credenciais:

```toml
TMDB_API_KEY = "SUA_CHAVE_API"
SUPABASE_URL = "SUA_URL_SUPABASE"
SUPABASE_KEY = "SUA_CHAVE_SUPABASE"
```

Substitua os valores pelas suas próprias credenciais do TMDB e Supabase.

**Importante:** nunca publique esse arquivo ou compartilhe suas chaves de acesso.

### 6. Execute a aplicação

```powershell
python -m streamlit run app.py
```

O Streamlit abrirá o CineTrack no navegador.

## 🔐 Segurança

As credenciais de acesso são armazenadas em arquivos de configuração locais e não devem ser enviadas ao repositório.

O arquivo `.streamlit/secrets.toml`, o ambiente virtual e os arquivos locais de banco de dados devem permanecer protegidos pelo `.gitignore`.

A autenticação de usuários é realizada por meio do Supabase.

## 🎯 Objetivo do projeto

O CineTrack foi desenvolvido como projeto de aprendizado e aplicação prática de desenvolvimento de software.

Seu desenvolvimento permitiu trabalhar com Python, construção de interfaces web, integração com APIs externas, bancos de dados, autenticação de usuários, organização de aplicações em múltiplas páginas e controle de versão com Git.

## 👨‍💻 Desenvolvedor

**Pedro Biondi**

GitHub: [@biondipedro388-lang](https://github.com/biondipedro388-lang)

---

As informações de filmes e séries são fornecidas pelo [TMDB](https://www.themoviedb.org/). Este produto utiliza a API do TMDB, mas não é endossado nem certificado pelo TMDB.
