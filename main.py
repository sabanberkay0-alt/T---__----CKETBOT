import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio
import io
from datetime import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="ESH!", intents=intents)

# ================= AYARLAR =================
TICKET_CATEGORY_ID = 1474659641781911623
TICKET_LOG_CHANNEL_ID = 1474656783082459320
SUPPORT_ROLE_ID = 1457121772515098779

# ===========================================

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Destek", description="Genel destek talebi"),
            discord.SelectOption(label="Şikayet", description="Bir kullanıcıyı şikayet et"),
            discord.SelectOption(label="Yetkili Başvuru", description="Yetkili olmak için başvur")
        ]

        super().__init__(
            placeholder="Bir kategori seçin...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        # Kullanıcının açık ticketı var mı?
        for channel in guild.text_channels:
            if channel.topic == str(user.id):
                return await interaction.response.send_message(
                    "❌ Zaten açık bir ticketın var!",
                    ephemeral=True
                )

        category = guild.get_channel(TICKET_CATEGORY_ID)
        support_role = guild.get_role(SUPPORT_ROLE_ID)

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            topic=str(user.id)
        )

        await ticket_channel.set_permissions(user, read_messages=True, send_messages=True)
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(support_role, read_messages=True, send_messages=True)

        embed = discord.Embed(
            title="🎫 Ticket Oluşturuldu",
            description=f"{user.mention} talebiniz alındı.\nKategori: **{self.values[0]}**",
            color=discord.Color.green()
        )

        await ticket_channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message("✅ Ticket oluşturuldu!", ephemeral=True)

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"📩 Yeni Ticket: {ticket_channel.mention} | Açan: {user.mention}")


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Ticket Kapat", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: Button):

        channel = interaction.channel
        guild = interaction.guild
        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

        await interaction.response.send_message("⏳ Ticket kapatılıyor...", ephemeral=True)

        # Transcript oluştur
        transcript = ""
        async for message in channel.history(limit=None, oldest_first=True):
            transcript += f"[{message.created_at.strftime('%H:%M')}] {message.author}: {message.content}\n"

        file = discord.File(io.StringIO(transcript), filename=f"{channel.name}-transcript.txt")

        if log_channel:
            await log_channel.send(
                f"📁 Ticket kapatıldı: {channel.name}",
                file=file
            )

        await asyncio.sleep(2)
        await channel.delete()


# ================= PANEL KOMUTU =================
@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):
    embed = discord.Embed(
        title="🎫 Destek Sistemi",
        description="Aşağıdan kategori seçerek ticket oluşturabilirsiniz.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())


@bot.event
async def on_ready():
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    print(f"{bot.user} aktif!")

bot.run(TOKEN)
