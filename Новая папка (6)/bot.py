import discord
from discord.ext import commands
from datetime import timedelta

# --- НАСТРОЙКИ ---
TOKEN = "ВСТАВЬ_СЮДА_НОВЫЙ_ТОКЕН"
LOG_CHANNEL_ID = 1480193205684273203
OWNER_ROLE_NAME = "*" 
MUTE_DURATION = timedelta(days=1)
BANNED_WORDS = ["logger", "loger", "l0gger", "l0ger", "логгер", "логер", "dm me for", "dm free", "dm for", "scammer script", "https", "discord.gg"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

def has_owner_role():
    async def predicate(ctx: commands.Context):
        role = discord.utils.get(ctx.author.roles, name=OWNER_ROLE_NAME)
        if role is None: raise commands.CheckFailure("No Owner Role")
        return True
    return commands.check(predicate)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure): pass
    elif isinstance(error, commands.CommandNotFound): pass
    else: print(f"Error: {error}")

def contains_banned_word(text: str) -> bool:
    return any(word in text.lower() for word in BANNED_WORDS)

async def punish_member(message: discord.Message):
    member = message.author
    if not isinstance(member, discord.Member) or member.id == message.guild.owner_id: return
    channel_name = message.channel.name
    try: await message.delete()
    except: pass
    try: await member.timeout(MUTE_DURATION, reason="Forbidden word")
    except: return
    try:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🔇 User muted", color=discord.Color.red())
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="User", value=f"{member.mention} ({member.name})", inline=False)
            embed.add_field(name="Channel", value=f"#{channel_name}", inline=False)
            embed.add_field(name="Message", value=f"```{message.content}```", inline=False)
            embed.add_field(name="Duration", value="1 day", inline=False)
            await log_channel.send(embed=embed)
    except: pass
    try:
        dm_embed = discord.Embed(title="🔇 Muted", description="🧧 You have been punished by 1d. You can appeal to @anobizv1 🧧", color=discord.Color.red())
        await member.send(embed=dm_embed)
    except: pass

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} is online!")

@bot.event
async def on_message(message: discord.Message):
    if not message.author.bot and contains_banned_word(message.content): await punish_member(message)
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if not after.author.bot and contains_banned_word(after.content): await punish_member(after)

@bot.command(name="help")
@has_owner_role()
async def help_cmd(ctx):
    embed = discord.Embed(title="🤖 Bot Command List", description="Commands for role '*'", color=discord.Color.green())
    embed.add_field(name="🛡️ Moderation", value=".ban @user\n.kick @user\n.unmute @user\n.clear [amount]\n.rename @user [name]", inline=True)
    embed.add_field(name="⚙️ Utilities", value=".member\n.activ\n.proverka @user\n.send @user [text]\n.partner [text]", inline=True)
    embed.add_field(name="🚫 Anti-Logger", value=".addword [word]\n.removeword [word]\n.wordlist", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="partner")
@has_owner_role()
async def partner(ctx, *, message_text: str):
    await ctx.message.delete()
    await ctx.send(message_text)

@bot.command(name="proverka")
@has_owner_role()
async def proverka(ctx, member: discord.Member):
    guild = ctx.guild
    overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), member: discord.PermissionOverwrite(read_messages=True, send_messages=True), ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
    channel = await guild.create_text_channel(name=f"verification-{member.name}", overwrites=overwrites)
    await ctx.send(f"✅ Created: {channel.mention}")

@bot.command(name="activ")
@has_owner_role()
async def activ(ctx):
    await ctx.message.delete()
    msg = await ctx.send("activ?\n@everyone")
    await msg.add_reaction("✅")

@bot.command(name="clear")
@has_owner_role()
async def clear(ctx, amount: int):
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"✅ Deleted {len(deleted)} messages.", delete_after=5)

@bot.command(name="send")
@has_owner_role()
async def send_to_user(ctx, member: discord.Member, *, message_text: str):
    try: 
        await member.send(message_text)
        await ctx.send(f"✅ Message sent to **{member.display_name}**.")
    except: await ctx.send("❌ Failed to send.")

@bot.command(name="ban")
@has_owner_role()
async def ban(ctx, member: discord.Member, *, reason: str = "No reason"):
    await member.ban(reason=reason); await ctx.send(f"🔨 {member} banned.")

@bot.command(name="kick")
@has_owner_role()
async def kick(ctx, member: discord.Member, *, reason: str = "No reason"):
    await member.kick(reason=reason); await ctx.send(f"👢 {member} kicked.")

@bot.command(name="rename")
@has_owner_role()
async def rename(ctx, member: discord.Member, *, new_name: str):
    await member.edit(nick=new_name); await ctx.send(f"✏️ {member.display_name} renamed.")

@bot.command(name="member")
@has_owner_role()
async def member_count(ctx):
    await ctx.send(f"📊 Members: {ctx.guild.member_count}")

@bot.command(name="unmute")
@has_owner_role()
async def unmute(ctx, member: discord.Member):
    await member.timeout(None); await ctx.send(f"✅ {member.display_name} unmuted.")

@bot.command(name="addword")
@has_owner_role()
async def add_word(ctx, *, word: str):
    BANNED_WORDS.append(word.lower()); await ctx.send(f"✅ Added: {word}")

@bot.command(name="removeword")
@has_owner_role()
async def remove_word(ctx, *, word: str):
    BANNED_WORDS.remove(word.lower()); await ctx.send(f"✅ Removed: {word}")

@bot.command(name="wordlist")
@has_owner_role()
async def word_list(ctx):
    await ctx.send(f"🚫 Banned: {', '.join(BANNED_WORDS)}")

bot.run("MTQ4OTM0NTQ5MTE3ODM1NjkzOQ.GN6U45.tsDBCNGsvSLmvcBGK1cTdYyZK6IMnXz0t6Mk5A")