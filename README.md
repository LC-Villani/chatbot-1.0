# Assistente Multifuncional para Discord com IA Gemini

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![Discord.py](https://img.shields.io/badge/Discord.py-2.6.3-7289DA?style=for-the-badge&logo=discord&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)

Este projeto é um bot multifuncional para Discord, desenvolvido em Python, que integra a poderosa API de IA generativa do Google Gemini para criar uma experiência de usuário rica e interativa. O bot combina funcionalidades de um chatbot avançado, um player de música robusto e ferramentas de utilidade, servindo como um assistente completo para servidores de Discord.

## ✨ Principais Funcionalidades

-   **🤖 IA de Conversação com Personalidade:** Utilizando a API do Google Gemini, o bot é capaz de manter conversas naturais, lembrar o contexto do chat e adotar uma persona customizável com regras de comportamento (humor, deboche, humildade) através de *prompt engineering*.

-   **🖼️ Análise Multi-modal de Canais:** Uma função de resumo que analisa o histórico de um canal, processando não apenas o **texto**, mas também o **conteúdo visual de imagens** (`JPG`, `PNG`, etc.) para criar sínteses contextuais sobre os tópicos discutidos.

-   **🎵 Player de Música:** Sistema de streaming de áudio para canais de voz, integrado ao **Wavelink** e um servidor **Lavalink** externo. Essa arquitetura, usada por bots profissionais, garante um streaming estável e de baixa latência a partir de fontes como o YouTube.

-   **👤 Análise de Perfil de Usuário:** Uma funcionalidade única onde o bot analisa as últimas 50 mensagens de um usuário (a pedido dele) e gera um perfil cômico e perspicaz sobre sua personalidade e padrões de fala.

-   **🛠️ Ferramentas de Moderação:** Inclui comandos úteis como `#limpar`, que apaga uma quantidade definida de mensagens no canal, com filtros inteligentes para ignorar mensagens de outros bots.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Bibliotecas Principais:** `Discord.py`, `google-generativeai`, `Wavelink`, `yt-dlp`, `Pillow (PIL)`, `python-dotenv`
* **APIs e Serviços:** Discord API, Google Gemini API
* **Infraestrutura de Áudio:** Servidor Lavalink (Java), FFmpeg

## 🚀 Começando

Para rodar este projeto localmente, siga os passos abaixo.

### Pré-requisitos

-   [Python 3.10+](https://www.python.org/)
-   [Java 17+](https://adoptium.net/) (para rodar o Lavalink)
-   [FFmpeg](https://ffmpeg.org/download.html) adicionado ao PATH do sistema.

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/nome-do-repositorio.git](https://github.com/seu-usuario/nome-do-repositorio.git)
    cd nome-do-repositorio
    ```

2.  **Crie o arquivo de credenciais:**
    Renomeie o arquivo `.env.example` para `.env` e preencha com suas chaves de API:
    ```ini
    DISCORD_TOKEN=SEU_TOKEN_DO_DISCORD_AQUI
    GEMINI_API_KEY=SUA_CHAVE_DA_API_GEMINI_AQUI
    ```

3.  **Configure e inicie o Lavalink:**
    - Baixe o `Lavalink.jar` (da [página de releases](https://github.com/lavalink-devs/Lavalink/releases/)) e coloque-o em uma pasta `lavalink`.
    - Crie um arquivo `application.yml` na mesma pasta.
    - Em um terminal separado, inicie o servidor Lavalink:
      ```bash
      java -jar Lavalink.jar
      ```

4.  **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

5.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Inicie o bot:**
    - Abra um segundo terminal, ative o `venv`.
    - Lembre-se de preencher o `application_id` no final do arquivo `main.py`.
    - Rode o bot:
      ```bash
      python main.py
      ```

## 🤖 Como Usar o Bot

-   **Conversar:** `@NomeDoBot Olá, tudo bem?`
-   **Tocar música:** `@NomeDoBot #tocar [nome da música ou link do YouTube]`
-   **Resumir o canal:** `@NomeDoBot #resumir 50`
-   **Limpar mensagens:** `@NomeDoBot #limpar 25`
-   **Analisar seu perfil:** `@NomeDoBot o que você acha de mim?`
-   **Sair da chamada de voz:** `@NomeDoBot #sair`
