
# 🎬 CineTrack

**Seus filmes, suas séries, sua história.**

O CineTrack é uma aplicação desenvolvida em Python com Streamlit para organizar filmes e séries em uma biblioteca pessoal. O projeto integra a API do TMDB para consultar informações sobre títulos e permite acompanhar o que você deseja assistir, está assistindo ou já concluiu.

## ✨ Funcionalidades

- 🎞️ Catálogo de filmes e séries.
- 📚 Biblioteca pessoal para organizar títulos.
- 📊 Painel com estatísticas da coleção.
- 🏷️ Organização por status: Quero assistir, Assistindo e Concluído.
- ⭐ Registro de avaliação pessoal.
- 🔎 Consulta de informações, sinopses, notas e pôsteres através do TMDB.
- 🎥 Exibição de trailers e vídeos.
- 🎭 Consulta de elenco e equipe de produção.
- 💾 Armazenamento local com SQLite.
- 🎨 Interface personalizada com CSS.

## 🛠️ Tecnologias utilizadas

- **Python** — lógica da aplicação.
- **Streamlit** — interface web.
- **SQLite** — banco de dados local.
- **TMDB API** — informações sobre filmes e séries.
- **Requests** — comunicação com a API.
- **HTML e CSS** — personalização visual.
- **Git e GitHub** — versionamento do código.

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
│   └── 3_Detalhes.py
├── services/
│   └── database.py
├── .gitignore
├── app.py
├── styles.css
└── README.md
```

## ⚙️ Como executar o projeto

### 1. Pré-requisitos

- Python instalado.
- Git instalado.
- Uma chave de API do [The Movie Database (TMDB)](https://www.themoviedb.org/).

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
python -m pip install streamlit requests
```

### 5. Configure a chave da API

Crie o arquivo `.streamlit/secrets.toml` e adicione:

```toml
TMDB_API_KEY = "SUA_CHAVE_API"
```

Substitua `SUA_CHAVE_API` pela sua chave pessoal do TMDB.

**Importante:** não publique esse arquivo nem compartilhe sua chave de API.

### 6. Execute a aplicação

```powershell
python -m streamlit run app.py
```

O Streamlit abrirá a aplicação no navegador.

## 🔐 Segurança

O arquivo `.streamlit/secrets.toml`, o ambiente virtual e o banco de dados local são excluídos do versionamento pelo `.gitignore`.

Nunca compartilhe chaves de API ou outras credenciais no repositório.

## 🚀 Objetivo do projeto

O CineTrack é um projeto de desenvolvimento de software criado para praticar Python, construção de interfaces web, integração com APIs externas, persistência de dados e organização de aplicações em múltiplas páginas.

## 📌 Próximas melhorias

- [ ] Aprimorar a navegação e a experiência visual.
- [ ] Adicionar filtros e opções de pesquisa.
- [ ] Melhorar a organização e a visualização da coleção.
- [ ] Implementar novas funcionalidades conforme a evolução do projeto.

## 👨‍💻 Desenvolvedor

**Pedro Biondi**

GitHub: [@biondipedro388-lang](https://github.com/biondipedro388-lang)

---

As informações de filmes e séries são fornecidas pelo [TMDB](https://www.themoviedb.org/). Este produto utiliza a API do TMDB, mas não é endossado nem certificado pelo TMDB.
