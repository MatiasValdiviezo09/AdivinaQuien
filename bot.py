import discord
from discord.ext import commands
import pyttsx3
import asyncio
import random
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

RUTA_PERSONAJES = "personajes.json"
RUTA_DATOS = "data.json"


juego = {
    "personaje": None,
    "indice_pista": 0,
    "jugando": False,
    "restantes": []
}

def cargar_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def hablar(texto, voz={}):
    engine = pyttsx3.init()
    if "rate" in voz:
        engine.setProperty("rate", voz["rate"])
    engine.save_to_file(texto, "voz.mp3")
    engine.runAndWait()

personajes_completos = cargar_json(RUTA_PERSONAJES)
datos = cargar_json(RUTA_DATOS)

def iniciar_lista_personajes():
    juego["restantes"] = personajes_completos.copy()
    random.shuffle(juego["restantes"])

def seleccionar_nuevo_personaje():
    if not juego["restantes"]:
        return None
    return juego["restantes"].pop()

@bot.command()
async def jugar(ctx):
    global juego
    if juego["jugando"]:
        await ctx.send("Ya estás jugando.")
        return

    iniciar_lista_personajes()
    nuevo = seleccionar_nuevo_personaje()
    if not nuevo:
        await ctx.send("No hay personajes disponibles.")
        return

    juego["personaje"] = nuevo
    juego["indice_pista"] = 0
    juego["jugando"] = True

    pista = nuevo["pistas"][0]
    hablar(pista, nuevo.get("voz", {}))
    await asyncio.sleep(1)
    await ctx.send("Primera pista:")
    await ctx.send(file=discord.File("voz.mp3"))

@bot.command()
async def pista(ctx):
    global juego
    if not juego["jugando"]:
        await ctx.send("No hay juego activo.")
        return

    juego["indice_pista"] += 1
    pistas = juego["personaje"]["pistas"]

    if juego["indice_pista"] >= len(pistas):
        await ctx.send("No hay más pistas.")
        return

    pista = pistas[juego["indice_pista"]]
    hablar(pista, juego["personaje"].get("voz", {}))
    await asyncio.sleep(1)
    await ctx.send("Nueva pista:")
    await ctx.send(file=discord.File("voz.mp3"))

@bot.command()
async def respuesta(ctx, *, intento: str):
    global juego
    if not juego["jugando"]:
        await ctx.send("No hay juego activo.")
        return

    correcta = juego["personaje"]["nombre"].lower().strip()
    if intento.lower().strip() == correcta:
        await ctx.send("¡Correcto!")

        user_id = str(ctx.author.id)
        datos[user_id] = datos.get(user_id, 0) + 1
        guardar_json(RUTA_DATOS, datos)

        if not juego["restantes"]:
            await ctx.send("¡Felicidades! Adivinaste todos los personajes.")
            juego["jugando"] = False
            return

        juego["personaje"] = seleccionar_nuevo_personaje()
        juego["indice_pista"] = 0

        pista = juego["personaje"]["pistas"][0]
        hablar(pista, juego["personaje"].get("voz", {}))
        await asyncio.sleep(1)
        await ctx.send("Nuevo personaje:")
        await ctx.send(file=discord.File("voz.mp3"))
    else:
        await ctx.send("Incorrecto.")
        hablar(f"La respuesta era: {juego['personaje']['nombre']}", juego["personaje"].get("voz", {}))
        await asyncio.sleep(1)
        await ctx.send(file=discord.File("voz.mp3"))
        juego["jugando"] = False

@bot.command()
async def skip(ctx):
    global juego
    if not juego["jugando"]:
        await ctx.send("No hay juego activo.")
        return

    if not juego["restantes"]:
        await ctx.send("Ya no quedan personajes. ¡Ganaste!")
        juego["jugando"] = False
        return

    juego["personaje"] = seleccionar_nuevo_personaje()
    juego["indice_pista"] = 0

    pista = juego["personaje"]["pistas"][0]
    hablar(pista, juego["personaje"].get("voz", {}))
    await asyncio.sleep(1)
    await ctx.send("Personaje saltado. Aquí tienes uno nuevo:")
    await ctx.send(file=discord.File("voz.mp3"))

@bot.command()
async def puntos(ctx):
    user_id = str(ctx.author.id)
    puntos = datos.get(user_id, 0)
    await ctx.send(f"{ctx.author.display_name} tiene {puntos} punto(s).")

@bot.command()
async def ayuda(ctx):
    mensaje = """
Comandos disponibles:

!jugar — Inicia un nuevo juego  
!pista — Muestra otra pista  
!respuesta <nombre> — Responde quién crees que es  
!skip — Salta al personaje actual  
!puntos — Muestra tus puntos
"""
    await ctx.send(mensaje)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


bot.run("MTM5OTQ5MzIzMDQ3ODg4NTA2NQ.GIi8Cc.1PZXbAvUGIov0SA_yqmFUkzWm1A2qQ1km5ncsY")