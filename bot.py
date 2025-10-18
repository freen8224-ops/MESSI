import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button

TOKEN = "YOUR_BOT_TOKEN"  # ⬅️ Replace with your bot token

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash commands synced!")

bot = MyBot()

# ======================
# 🧰 Auto Create Verified Role
# ======================
async def get_or_create_verified_role(guild: discord.Guild) -> discord.Role:
    role = discord.utils.get(guild.roles, name="Verified")
    if not role:
        role = await guild.create_role(name="Verified", reason="Auto-created for verification system")
        try:
            await role.edit(position=len(guild.roles) - 1)
        except:
            pass
    return role

# ======================
# 🔐 Verification System
# ======================
class VerifyButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success)
    async def verify(self, interaction: discord.Interaction, button: Button):
        member = interaction.user
        guild = interaction.guild
        role = await get_or_create_verified_role(guild)

        if role in member.roles:
            await interaction.response.send_message("✅ You're already verified!", ephemeral=True)
            return

        await member.add_roles(role)
        await interaction.response.send_message(
            f"🎉 Welcome {member.mention}! You are now verified.",
            ephemeral=True
        )

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    bot.add_view(VerifyButton())

@bot.tree.command(name="setupverify", description="Create the verification panel.")
@app_commands.checks.has_permissions(administrator=True)
async def setupverify(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔐 Server Verification",
        description="Click the button below to verify yourself and access the server.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, view=VerifyButton())

# ======================
# 🛡️ Moderation Commands
# ======================
@bot.tree.command(name="kick", description="Kick a member.")
@app_commands.describe(member="The member to kick", reason="Reason for kicking")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member} kicked. Reason: {reason}")

@bot.tree.command(name="ban", description="Ban a member.")
@app_commands.describe(member="The member to ban", reason="Reason for banning")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {member} banned. Reason: {reason}")

@bot.tree.command(name="unban", description="Unban a member.")
@app_commands.describe(user_tag="username#0000")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_tag: str):
    banned_users = await interaction.guild.bans()
    name, discriminator = user_tag.split("#")
    for ban_entry in banned_users:
        if (ban_entry.user.name, ban_entry.user.discriminator) == (name, discriminator):
            await interaction.guild.unban(ban_entry.user)
            await interaction.response.send_message(f"✅ Unbanned {ban_entry.user}")
            return
    await interaction.response.send_message("❌ User not found.")

@bot.tree.command(name="mute", description="Timeout (mute) a member.")
@app_commands.describe(member="Member to mute", minutes="Duration in minutes", reason="Reason")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason"):
    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🔇 {member} muted for {minutes} minutes.")

@bot.tree.command(name="unmute", description="Remove timeout from a member.")
@app_commands.describe(member="Member to unmute")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(f"🔊 {member} unmuted.")

@bot.tree.command(name="clear", description="Clear messages.")
@app_commands.describe(amount="Number of messages to delete")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Deleted {amount} messages.", ephemeral=True)

# ======================
# 🆘 Help Command
# ======================
@bot.tree.command(name="help", description="Show all bot commands.")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🆘 Help Menu",
        description="Here are all the commands you can use with this bot:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🔐 Verification",
        value="/setupverify → Create the verification panel",
        inline=False
    )
    embed.add_field(
        name="🛡️ Moderation",
        value=(
            "/kick <member>\n"
            "/ban <member>\n"
            "/unban <user#0000>\n"
            "/mute <member> <minutes>\n"
            "/unmute <member>\n"
            "/clear <amount>"
        ),
        inline=False
    )
    embed.set_footer(text="Bot works on multiple servers automatically. Made with ❤️ using discord.py")
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run(TOKEN)
