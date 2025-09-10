# --- IMPORTAÇÕES ---
import discord
import os
import google.generativeai as genai
from dotenv import load_dotenv
import io
from PIL import Image
import asyncio
#import wavelink  # BIBLIOTECA TESTE PARA MÚSICA

# --- CONFIGURAÇÃO INICIAL ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# --- CONFIGURAÇÃO DA IA GEMINI ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    generation_config = {"temperature": 1.0, "top_p": 1, "top_k": 1, "max_output_tokens": 2048}
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest', generation_config=generation_config, safety_settings=safety_settings)
    print("API do Gemini configurada com sucesso.")
except Exception as e:
    print(f"Erro ao configurar a API do Gemini: {e}")
    exit()

# --- ESTRUTURA PRINCIPAL DO BOT (CLASSE) ---
class LuqueraBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_sessions = {}  # Armazena o histórico de chat da IA para cada canal

    async def on_ready(self):
        print('---')
        print(f'Bot conectado como: {self.user}')
        print(f'ID do Bot: {self.user.id}')
        print('---')
        await self.setup_wavelink()

    async def setup_wavelink(self):
        print("Iniciando o nó do Wavelink...")
        node = wavelink.Node(uri='http://localhost:2333', password='youshallnotpass')
        try:
            await wavelink.NodePool.connect(client=self, nodes=[node])
        except Exception as e:
            print(f"Erro ao conectar ao nó do Wavelink: {e}")
            print("Certifique-se de que o servidor Lavalink.jar está rodando!")

    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f'Nó do Wavelink "{node.identifier}" está pronto e conectado!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if self.user.mentioned_in(message):
            content = message.content.lower().replace("você", "vc")
            frases_analise = ["o que vc acha de mim", "me analise", "me descreva", "qual a sua opinião sobre mim"]

            if "#entrar" in content or "#tocar" in content:
                await handle_play(self, message)
            elif "#sair" in content:
                await handle_leave(self, message)
            elif "#resumir" in content:
                await handle_summarize(self, message)
            elif "#limpar" in content:
                await handle_clear(self, message)
            elif any(frase in content for frase in frases_analise):
                await handle_analyze_user(self, message)
            else:
                await handle_chat(self, message)

# --- FUNÇÕES DE LÓGICA DO BOT ---
async def handle_chat(bot, message):
    async with message.channel.typing():
        channel_id = str(message.channel.id)
        if channel_id not in bot.chat_sessions:
            bot.chat_sessions[channel_id] = gemini_model.start_chat(history=[])
        chat = bot.chat_sessions[channel_id]
        prompt = message.content.replace(f'<@!{bot.user.id}>', '').strip()
        system_instruction = (
            "Você é um assistente de Discord com uma personalidade tranquila e amigável. Seu nome é Gemini. Seu objetivo é conversar como uma pessoa real, não como um robô.\n\nSiga estas diretrizes de comportamento:\n\n1.  **Comportamento Padrão (95% do tempo):**\n    - **Humildade e Leveza:** Converse de igual para igual. Evite se gabar ou soar como um sabe-tudo.\n    - **Humor Sutil e Situacional:** Use ironias leves ou observações engraçadas APENAS quando fizer sentido na conversa.\n\n2.  **REGRA ESPECIAL: RESPOSTA A OFENSAS:**\n    - Se um usuário tentar te ofender, ative o modo 'Debochado', respondendo de forma irônica e inteligente, sem usar ofensas.\n\n3.  **REGRA DE ESTILO:**\n    - Fale sempre na primeira pessoa ('Eu acho', 'Na minha opinião'). Nunca se refira a si mesmo pelo nome 'Gemini' ou na terceira pessoa.\n\nResponda sempre em português do Brasil, de forma fluida e natural."
        )
        full_prompt = f"{system_instruction}\n\nO histórico da nossa conversa até agora é este:\n{chat.history}\n\nMinha nova pergunta é: {prompt}"
        try:
            response = await chat.send_message_async(full_prompt)
            await message.channel.send(f"{message.author.mention} {response.text}")
        except Exception as e:
            await message.channel.send(f"{message.author.mention} Ih, deu um bug na minha cabeça. Tenta de novo aí.")
            print(f"Ocorreu um erro ao chamar a API: {e}")

async def handle_summarize(bot, message):
    await message.channel.send("Entendido! Analisando o histórico do canal, incluindo as imagens... Isso pode levar um momento.")
    try:
        parts = message.content.split()
        limite = 50
        for part in parts:
            if part.isdigit():
                limite = int(part)
                break
        prompt_parts = [
            "Você é um especialista em análise de conversas multimodais. Sua tarefa é ler o log de uma conversa do Discord, que inclui texto e imagens, e criar um resumo claro e conciso. Descreva o conteúdo das imagens e como elas se relacionam com o texto.\n\nA conversa é a seguinte:\n---------------------\n"
        ]
        historico_mensagens = [msg async for msg in message.channel.history(limit=limite)]
        historico_mensagens.reverse()
        for msg in historico_mensagens:
            if msg.content:
                prompt_parts.append(f"{msg.author.display_name}: {msg.content}\n")
            if msg.attachments:
                for attachment in msg.attachments:
                    if attachment.content_type in ['image/png', 'image/jpeg', 'image/gif', 'image/webp']:
                        try:
                            prompt_parts.append(f"({msg.author.display_name} enviou uma imagem:)\n")
                            image_bytes = await attachment.read()
                            img = Image.open(io.BytesIO(image_bytes))
                            prompt_parts.append(img)
                        except Exception as e:
                            print(f"Não foi possível processar a imagem {attachment.filename}: {e}")
        prompt_parts.append("\n---------------------\n\nPor favor, gere um resumo dos tópicos principais, decisões tomadas e descreva as imagens importantes e o contexto delas na conversa.")
        response = gemini_model.generate_content(prompt_parts)
        resumo = response.text[:1990] + "..." if len(response.text) > 2000 else response.text
        await message.channel.send(f"{message.author.mention}\n### Resumo das últimas {len(historico_mensagens)} mensagens:\n{resumo}")
    except Exception as e:
        print(f"Erro ao executar o resumo: {e}")
        await message.channel.send(f"{message.author.mention} Ocorreu um erro ao tentar resumir o canal. Tente novamente.")

async def handle_clear(bot, message):
    if not message.channel.permissions_for(message.guild.me).manage_messages:
        await message.channel.send(f"{message.author.mention} Eu não tenho a permissão de `Gerenciar Mensagens` neste canal para fazer isso.")
        return
    parts = message.content.split()
    limite = 100
    if len(parts) > 1 and parts[-1].isdigit():
        limite = int(parts[-1])
        if limite > 200:
            limite = 200
            await message.channel.send("Opa, o máximo que consigo limpar por vez é 200 mensagens.")
    def is_user_message(m):
        return not m.author.bot
    try:
        deleted = await message.channel.purge(limit=limite + 1, check=is_user_message)
        await message.channel.send(f"{message.author.mention} Faxina completa! {len(deleted)} mensagens de usuários foram apagadas.", delete_after=10)
    except Exception as e:
        print(f"Erro ao executar a limpeza: {e}")
        await message.channel.send(f"{message.author.mention} Ocorreu um erro durante a limpeza.")

async def handle_analyze_user(bot, message):
    author = message.author
    await message.channel.send(f"Deixa eu ver, {author.display_name}... Puxando sua capivara aqui no canal pra ver do que você fala tanto... 🤔")
    try:
        user_messages = []
        async for msg in message.channel.history(limit=200):
            if msg.author == author:
                user_messages.append(msg.content)
                if len(user_messages) >= 50:
                    break
        if not user_messages:
            await message.channel.send(f"Ué, {author.display_name}, parece que você é uma pessoa de poucas palavras. Não achei mensagens suas por aqui pra analisar.")
            return
        historico_formatado = "\n - ".join(user_messages)
        prompt_para_analise = (
            "Você é um 'psicólogo de bot', com um senso de humor afiado, um pouco sarcástico, mas nunca maldoso. Sua tarefa é analisar o histórico de mensagens de um usuário do Discord e criar um perfil curto, engraçado e perspicaz sobre ele.\n\n**REGRAS IMPORTANTES:**\n1.  **Baseie-se APENAS no texto fornecido.**\n2.  **Seja bem-humorado.**\n3.  **Seja breve e direto.**\n4.  **O tom é de brincadeira.**\n\n--- HISTÓRICO DE MENSAGENS DO USUÁRIO ---\n- " + historico_formatado + "\n------------------------------------------\n\nAgora, com base nesse histórico, o que você diria sobre essa pessoa?"
        )
        response = gemini_model.generate_content(prompt_para_analise)
        analise = response.text
        await message.channel.send(f"Ok, {author.mention}, analisei o que você escreve e cheguei a uma conclusão...\n\n{analise}")
    except Exception as e:
        print(f"Erro ao executar a análise de usuário: {e}")
        await message.channel.send(f"{author.mention} Tentei te analisar, mas minha bola de cristal queimou. Tenta de novo.")

# --- NOVAS FUNÇÕES DE MÚSICA COM WAVELINK ---
async def handle_play(bot, message):
    query = ' '.join(message.content.split()[1:]).replace('#tocar', '').replace('#entrar', '').strip()
    if not query:
        await message.channel.send(f"{message.author.mention}, você precisa me dizer o que tocar!")
        return
        
    if not message.author.voice:
        await message.channel.send(f"{message.author.mention}, você precisa estar em um canal de voz.")
        return

    vc: wavelink.Player = message.guild.voice_client
    if not vc:
        try:
            vc = await message.author.voice.channel.connect(cls=wavelink.Player)
        except Exception as e:
            print(f"Erro ao conectar ao canal de voz: {e}")
            await message.channel.send("Não consegui me conectar ao seu canal de voz.")
            return
    
    await message.channel.send(f":mag_right: Procurando por: `{query}`...")
    try:
        tracks = await wavelink.YouTubeTrack.search(query)
        if not tracks:
            await message.channel.send(f"{message.author.mention}, não achei nada com esse nome.")
            # Se não achar a música e o bot estiver sozinho, ele sai
            if not vc.is_playing() and not vc.queue:
                await vc.disconnect()
            return

        track = tracks[0]
        
        if vc.is_playing() or not vc.queue.is_empty:
             # Adiciona na fila se já estiver tocando
            await vc.queue.put_wait(track)
            await message.channel.send(f'Adicionado à fila: **{track.title}**')
        else:
            # Toca a música imediatamente se não houver nada na fila
            await vc.play(track)
            await message.channel.send(f':notes: Tocando agora: **{track.title}**')

    except Exception as e:
        print(f"Erro durante a busca ou reprodução: {e}")
        await message.channel.send("Ocorreu um erro ao tentar tocar a música.")

async def handle_leave(bot, message):
    vc: wavelink.Player = message.guild.voice_client
    if vc:
        await vc.disconnect()
        await message.channel.send("Até a próxima! 👋")


# --- INICIAR O BOT ---
if __name__ == "__main__":
    client = LuqueraBot(intents=intents)
    client.run(DISCORD_TOKEN)