import os
import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import ButtonStyle
from flask import Flask
from threading import Thread

# ================= TOKEN =================
TOKEN = "TOKEN"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= KEEP ALIVE =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

# 🔥 Not Found çözümü için ekstra ping route
@app.route("/ping")
def ping():
    return "OK"

def keep_alive():
    Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()

# ================= AYARLAR =================
TICKET_CHANNEL_1 = 1457381313018593421
TICKET_CHANNEL_2 = 1445515675262128219
TICKET_CATEGORY_ID = 1474659641781911623

# ==================================================

@bot.event
async def on_ready():
    print(f"{bot.user} aktif!")

# ================= TICKET BUTONU =================
class TicketButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Ticket Aç", style=ButtonStyle.green)
    async def open_ticket(self, interaction: discord.Interaction, button: Button):

        guild = interaction.guild
        user = interaction.user

        # Kullanıcının açık ticketı var mı?
        for channel in guild.text_channels:
            if channel.topic == str(user.id):
                await interaction.response.send_message(
                    "❌ Zaten açık ticketın var!",
                    ephemeral=True
                )
                return

        category = guild.get_channel(TICKET_CATEGORY_ID)

        if category is None:
            await interaction.response.send_message(
                "❌ Ticket kategorisi bulunamadı!",
                ephemeral=True
            )
            return

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            topic=str(user.id)
        )

        # İzinler
        await ticket_channel.set_permissions(user, read_messages=True, send_messages=True)
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(guild.owner, read_messages=True, send_messages=True)

        await ticket_channel.send(
            f"👋 {user.mention} Ticket açıldı!\n"
            "🔒 Kapatmak için: `!kapat`"
        )

        await interaction.response.send_message(
            "✅ Ticket oluşturuldu!",
            ephemeral=True
        )

# ================= PANEL =================
@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):

    view = TicketButton()

    kanal1 = bot.get_channel(TICKET_CHANNEL_1)
    kanal2 = bot.get_channel(TICKET_CHANNEL_2)

    if kanal1:
        await kanal1.send("🎫 Ticket Açmak İçin Butona Basın", view=view)

    if kanal2:
        await kanal2.send("🎫 Ticket Açmak İçin Butona Basın", view=view)

    await ctx.send("✅ Butonlar 2 kanala gönderildi.")

# ================= TICKET KAPAT =================
@bot.command()
async def kapat(ctx):

    if ctx.channel.topic is None:
        await ctx.send("❌ Bu kanal ticket değil!")
        return

    await ctx.send("⏳ Ticket 5 saniye sonra kapanıyor...")

    await discord.utils.sleep_until(discord.utils.utcnow())

    await ctx.channel.delete()

# ================= BOT BAŞLAT =================
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: app.run(host="0.0.0.0", port=port)).start()
bot.run("TOKEN")
