import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from pathlib import Path
import requests
import base64
from openai import OpenAI

# cargar .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("TOKEN OK:", bool(DISCORD_TOKEN))
print("OPENAI OK:", bool(OPENAI_API_KEY))

if not DISCORD_TOKEN or not OPENAI_API_KEY:
    raise Exception("Falta DISCORD_TOKEN o OPENAI_API_KEY en .env")

client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ BOT CONECTADO COMO {bot.user}")


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    print("📩 Mensaje recibido")

    if message.attachments:

        file = message.attachments[0]

        if file.content_type and "image" in file.content_type:

            await message.channel.send("🔍 Analizando imagen...")

            try:
                # descargar imagen
                image_bytes = requests.get(file.url).content
                image_b64 = base64.b64encode(image_bytes).decode("utf-8")

                # pedir a OpenAI
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """
Eres un experto en reciclaje.

Analiza la imagen y responde EXACTAMENTE:

Objeto:
Material:
Contenedor de reciclaje:
Confianza:
Consejo ecológico:

Reglas:
- Sé preciso
- No inventes
- Si dudas, baja la confianza
"""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_b64}"
                                    }
                                }
                            ]
                        }
                    ]
                )

                resultado = response.choices[0].message.content

                await message.channel.send("♻️ Resultado:\n\n" + resultado)

            except Exception as e:
                await message.channel.send(f"❌ Error: {e}")

    await bot.process_commands(message)


bot.run(DISCORD_TOKEN)