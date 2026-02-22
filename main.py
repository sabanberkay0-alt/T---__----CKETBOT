import os
import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import ButtonStyle

# ================= TOKEN =================
TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    print("TOKEN bulunamadı!")
    exit()

# ================= INTENTS =================
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= AYARLAR =================
TICKET_CHANNEL_1 = 1457381313018593421
TICKET_CHANNEL_2 = 1445515675262128219
TICKET_CATEGORY_ID = 1474659641781911623

# ================= BOT READY =================
@bot.event
async def on_ready():
    print(f"{bot.user} aktif 🚀")

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

        if not category:
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

        await ticket_channel.set_permissions(user, read_messages=True, send_messages=True)
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(guild.me, read_messages=True)

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

    await ctx.send("✅ Panel gönderildi.")

# ================= TICKET KAPAT =================
@bot.command()
async def kapat(ctx):

    if not ctx.channel.topic:
        await ctx.send("❌ Bu kanal ticket değil!")
        return

    await ctx.send("⏳ Ticket 5 saniye sonra kapanıyor...")

    await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=5))

    await ctx.channel.delete()

# ================= BOT BAŞLAT =================
bot.run(TOKEN)
