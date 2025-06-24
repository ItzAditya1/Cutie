
import discord
from discord.ext import commands
from discord.utils import get
import datetime
import random  


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    activity = discord.Activity(type=discord.ActivityType.watching, name="SPY ESPORTS 💖")
    await bot.change_presence(status=discord.Status.dnd, activity=activity)

# Command categories
categories = {
    "Moderation": {
        "emoji": "💀",
        "commands": ["ban","unban", "kick", "mute", "unmute", "clear""lock", "unlock", "hide", "unhide","createchannel","deletechannel"]
    },
    "Utility": {
        "emoji": "🛡️",
        "commands": ["avatar", "banner", "botinfo", "ping", "member_count", "nick", "react", "serverav", "serverinfo", "userinfo",  "setupticket"]
    },
    "Role": {
        "emoji": "⚡",
        "commands": ["createrole", "deleterole", "role", "removerole" , "roleallbot", "roleallhuman"]
    }
    }
    
class HelpDropdownselect:
    def __init__(self, author):
        self.author = author
        options = [
            discord.SelectOption(label=cat, emoji=data["emoji"], description=f"{cat} Commands")
            for cat, data in categories.items()
        ]
        super().__init__(placeholder="Choose Command Category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message("❌ Only the command author can use this menu.", ephemeral=True)

        category = self.values[0]
        data = categories[category]
        commands_list = ", ".join(f"`{cmd}`" for cmd in data["commands"])

        embed = discord.Embed(
            title=f"{category} Commands {data['emoji']}",
            description=commands_list,
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Requested by {self.author.name}", icon_url=self.author.display_avatar)
        await interaction.response.edit_message(embed=embed, view=self.view)

# HELP
@bot.command()
async def help(ctx):
    total = sum(len(data["commands"]) for data in categories.values())
    usable = total  # You can dynamically filter based on permissions if needed

    embed = discord.Embed(
        title="Cutie Help Menu",
        description=f"• Prefix - `!`\n• Total Commands = `{total}` | Usable = `{usable}`\n"
                    f"__**Categories**__\n" +
                    "\n".join(f"{data['emoji']} **{name}**" for name, data in categories.items()),
        color=discord.Color.brand_red()
    )

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1386275890815832164/1386656046474592287/cutie.jpg")
    embed.set_footer(text=f"Requested By {ctx.author.name}", icon_url=ctx.author.display_avatar)

    embed.add_field(
        name="💀 Moderation Commands",
        value="`ban`,`unban`, `kick`, `mute`, `unmute`, `clear`,`lock`, `unlock`, `hide`, `unhide`,`createchannel`,`deletechannel`",
        inline=False
    )

    embed.add_field(
        name="🛡️ Utility Commands",
        value="`avatar`, `banner`, `botinfo`,`ping`, `member_count`, `nick`, `react`, `serverav`, `serverinfo`, `userinfo`,  `setupticket`",
        inline=False
    )

    embed.add_field(
        name="⚡ Role Commands",
        value="`createrole`, `deleterole`, `role`, `removerole`, `roleallbot`, `roleallhuman`",
        inline=False
    )

    await ctx.send(embed=embed,)


# Embed style helper
def create_embed(title, description, color=discord.Color.blurple()):
    return discord.Embed(title=title, description=description, color=color)

# 1. Clear Messages
@bot.command(aliases=["purge"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = None):
    if amount is None or amount <= 0:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!clear <number of messages>```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Deletes the specified number of messages from the channel.", inline=False)
        await ctx.send(embed=embed)
        return

    try:
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to delete the command itself too
        embed = discord.Embed(
            description=f"🧹 Successfully deleted `{len(deleted) - 1}` messages.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, delete_after=5)
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 2. Delete Channel
@bot.command()
@commands.has_permissions(manage_channels=True)
async def delete_channel(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel  # Default to current channel if none provided

    try:
        await channel.delete(reason=f"Deleted by {ctx.author}")
        embed = discord.Embed(
            description=f"🗑️ Channel `{channel.name}` has been **deleted** successfully.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)  # Send confirmation before deletion
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to delete this channel.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 3. Create Channel
@bot.command()
@commands.has_permissions(manage_channels=True)
async def create_channel(ctx, channel_name: str = None, channel_type: str = "text"):
    if not channel_name:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!create_channel <name> [type]```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Creates a new text or voice channel.", inline=False)
        await ctx.send(embed=embed)
        return

    # Determine channel type
    types = {"text": discord.ChannelType.text, "voice": discord.ChannelType.voice}
    chosen_type = types.get(channel_type.lower())
    if not chosen_type:
        await ctx.send("❌ Invalid type! Use `text` or `voice`.")
        return

    try:
        new_channel = await ctx.guild.create_text_channel(channel_name) if chosen_type == discord.ChannelType.text else await ctx.guild.create_voice_channel(channel_name)
        embed = discord.Embed(
            description=f"✅ Successfully created {chosen_type.name} channel: {new_channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to create channels.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 4. Mute Member
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if not member:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!mute <@user> [reason]```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Mutes a member by removing their speaking permission.", inline=False)
        await ctx.send(embed=embed)
        return

    # Create "Muted" role if it doesn't exist
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted", reason="Mute role created by bot")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)

    if muted_role in member.roles:
        await ctx.send("❌ That user is already muted.")
        return

    try:
        await member.add_roles(muted_role, reason=reason)
        embed = discord.Embed(
            description=f"🔇 Successfully muted {member.mention}\n📝 Reason: `{reason}`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to mute this user.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 5. Unmute Member
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member = None):
    if not member:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!unmute <@user>```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Unmutes a member by removing the Muted role.", inline=False)
        await ctx.send(embed=embed)
        return

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role or muted_role not in member.roles:
        await ctx.send("❌ That user is not muted.")
        return

    try:
        await member.remove_roles(muted_role, reason=f"Unmuted by {ctx.author}")
        embed = discord.Embed(
            description=f"🔊 Successfully unmuted {member.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unmute this user.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 6. Kick
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if not member:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!kick <@user> [reason]```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Kicks a user from the server.", inline=False)
        await ctx.send(embed=embed)
        return

    if member == ctx.author:
        await ctx.send("❌ You can't kick yourself.")
        return
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("❌ You can't kick someone with a higher or equal role.")
        return
    if not ctx.guild.me.top_role > member.top_role:
        await ctx.send("❌ I can't kick this member due to role hierarchy.")
        return

    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            description=f"✅ Successfully kicked {member.mention}\n📝 Reason: `{reason}`",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to kick this user.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 7. Ban
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if not member:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!ban <@user> [reason]```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Bans a user from the server.", inline=False)
        await ctx.send(embed=embed)
        return

    if member == ctx.author:
        await ctx.send("❌ You cannot ban yourself.")
        return
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("❌ You can't ban someone with a higher or equal role.")
        return
    if not ctx.guild.me.top_role > member.top_role:
        await ctx.send("❌ I can't ban this member due to role hierarchy.")
        return

    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            description=f"✅ Successfully banned {member.mention}\n📝 Reason: `{reason}`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this user.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 8. Unban
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: str = None):
    if not user:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!unban <username#1234>```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Unbans a previously banned user.", inline=False)
        await ctx.send(embed=embed)
        return

    try:
        name, discriminator = user.split("#")
    except ValueError:
        return await ctx.send("❌ Please use the correct format: `username#1234`")

    bans = await ctx.guild.bans()
    for ban_entry in bans:
        banned_user = ban_entry.user
        if banned_user.name == name and banned_user.discriminator == discriminator:
            await ctx.guild.unban(banned_user)
            embed = discord.Embed(
                description=f"✅ Successfully unbanned `{user}`",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            return

    await ctx.send(f"❌ User `{user}` not found in the ban list.")


# 9. Hide Channel
@bot.command()
@commands.has_permissions(manage_channels=True)
async def hide(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)

    if overwrite.view_channel is False:
        await ctx.send("🙈 This channel is already hidden.")
        return

    try:
        overwrite.view_channel = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
            description=f"🙈 {channel.mention} has been **hidden** from @everyone.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 10. Unhide Channel
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unhide(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)

    if overwrite.view_channel is None or overwrite.view_channel is True:
        await ctx.send("👀 This channel is already visible.")
        return

    try:
        overwrite.view_channel = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
            description=f"👀 {channel.mention} has been **made visible** to @everyone.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 11. Lock Channel
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)

    if overwrite.send_messages is False:
        await ctx.send("🔒 This channel is already locked.")
        return

    try:
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
            description=f"🔒 {channel.mention} has been **locked**.\nMembers can no longer send messages.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 12. Unlock Channel
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)

    if overwrite.send_messages is None or overwrite.send_messages is True:
        await ctx.send("🔓 This channel is already unlocked.")
        return

    try:
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
            description=f"🔓 {channel.mention} has been **unlocked**.\nMembers can now send messages.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 13. Create Role
@bot.command()
@commands.has_permissions(manage_roles=True)
async def createrole(ctx, *, role_name: str = None):
    if not role_name:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!createrole <role name>```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Creates a new role in the server.", inline=False)
        await ctx.send(embed=embed)
        return

    try:
        new_role = await ctx.guild.create_role(name=role_name, reason=f"Created by {ctx.author}")
        embed = discord.Embed(
            description=f"✅ Successfully created role: {new_role.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to create roles.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 14. Delete Role
@bot.command(aliases=["dr","delrole","deleterole"])
@commands.has_permissions(manage_roles=True)
async def delete_role(ctx, *, role: discord.Role = None):
    if not role:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!dr,delrol,deleterole <@role>```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Deletes a role from the server.", inline=False)
        await ctx.send(embed=embed)
        return

    try:
        role_name = role.name
        await role.delete(reason=f"Deleted by {ctx.author}")
        embed = discord.Embed(
            description=f"🗑️ Role `{role_name}` has been **deleted**.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to delete that role.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 15. Add Role to User
@bot.command(aliases=["r",])
@commands.has_permissions(manage_roles=True)
async def role(ctx, role: discord.Role = None, *members: discord.Member):
    if not role or not members:
        # Show help embed if usage is wrong
        help_embed = discord.Embed(
            title="Usage",
            description="```bash\n!r,role <@role> <@user1> [@user2 ...]```",
            color=discord.Color.blurple()
        )
        help_embed.add_field(name="Help", value="Assigns a Role to Specified Users", inline=False)
        await ctx.send(embed=help_embed)
        return

    # Attempt to add role to each mentioned member
    success = []
    for member in members:
        try:
            await member.add_roles(role)
            success.append(member.mention)
        except discord.Forbidden:
            await ctx.send(f"❌ Missing permissions to give role to {member.mention}")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {str(e)}")

    if success:
        success_embed = discord.Embed(
            description=f"✅ Successfully added {role.mention} role to {', '.join(success)}",
            color=discord.Color.green()
        )
        await ctx.send(embed=success_embed)


# 16. Remove Role from User
@bot.command(aliases=["rr","rrole"])
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, role: discord.Role = None, *members: discord.Member):
    if not role or not members:
        # Help embed
        help_embed = discord.Embed(
            title="Usage",
            description="```bash\n!rr,rrole,removerole <@role> <@user1> [@user2 ...]```",
            color=discord.Color.blurple()
        )
        help_embed.add_field(name="Help", value="Removes a Role from Specified Users", inline=False)
        await ctx.send(embed=help_embed)
        return

    # Try to remove role from each user
    success = []
    for member in members:
        try:
            await member.remove_roles(role)
            success.append(member.mention)
        except discord.Forbidden:
            await ctx.send(f"❌ Can't remove role from {member.mention} due to permission error.")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {str(e)}")

    if success:
        success_embed = discord.Embed(
            description=f"✅ Successfully removed {role.mention} role from {', '.join(success)}",
            color=discord.Color.green()
        )
        await ctx.send(embed=success_embed)


# 17. Role All Bots
@bot.command(aliases=["rab"])
@commands.has_permissions(manage_roles=True)
async def roleallbot(ctx, role: discord.Role = None):
    if role is None:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!rab,roleallbot <@role>```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Gives the role to all bots in the server.", inline=False)
        await ctx.send(embed=embed)
        return

    success = 0
    for member in ctx.guild.members:
        if member.bot and role not in member.roles:
            try:
                await member.add_roles(role, reason=f"Mass role assignment by {ctx.author}")
                success += 1
            except:
                continue

    embed = discord.Embed(
        description=f"🤖 Added {role.mention} to **{success}** bot(s).",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


# 18. Role All Humans
@bot.command(aliases=["rah"])
@commands.has_permissions(manage_roles=True)
async def roleallhuman(ctx, role: discord.Role = None):
    if role is None:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!rah,roleallhuman <@role>```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Gives the role to all human (non-bot) members in the server.", inline=False)
        await ctx.send(embed=embed)
        return

    success = 0
    for member in ctx.guild.members:
        if not member.bot and role not in member.roles:
            try:
                await member.add_roles(role, reason=f"Mass role assignment by {ctx.author}")
                success += 1
            except:
                continue

    embed = discord.Embed(
        description=f"✅ Added {role.mention} to **{success}** human members.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


# 19. Avatar
@bot.command(aliases=["av"])
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author  # Use the author if no member is mentioned
    avatar_url = member.display_avatar.url

    embed = discord.Embed(
        title=f"{member.display_name}'s Avatar",
        description=f"[Click to view full size]({avatar_url})",
        color=discord.Color.blurple()
    )
    embed.set_image(url=avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)


# 20. Banner
@bot.command(aliases=["bn"])
async def banner(ctx, member: discord.Member = None):
    member = member or ctx.author
    user = await bot.fetch_user(member.id)  # Required to get banner

    if user.banner is None:
        embed = discord.Embed(
            description=f"❌ {member.mention} does not have a profile banner.",
            color=discord.Color.red()
        )
    else:
        banner_url = user.banner.url
        embed = discord.Embed(
            title=f"{member.display_name}'s Banner",
            description=f"[Click to view full size]({banner_url})",
            color=discord.Color.blurple()
        )
        embed.set_image(url=banner_url)

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


# 21. Bot Info
import platform
import time

start_time = time.time()  # Place this at the top of your bot file

@bot.command()
async def botinfo(ctx):
    uptime = time.time() - start_time
    hours, remainder = divmod(int(uptime), 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(
        title="🤖 Bot Info",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
    embed.add_field(name="📛 Name", value=ctx.bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=f"`{ctx.bot.user.id}`", inline=True)
    embed.add_field(name="👑 Developer", value="Aditya#0001", inline=True)  # Customize this
    embed.add_field(name="📶 Latency", value=f"{round(ctx.bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🕒 Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=True)
    embed.add_field(name="📚 Library", value=f"discord.py `{discord.__version__}`", inline=True)
    embed.add_field(name="🌐 Servers", value=len(ctx.bot.guilds), inline=True)

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


# 22. Ping
@bot.command()
async def ping(ctx):
    bot_latency = round(bot.latency * 1000)
    db_latency = random.randint(1, 5)

    # Latency status logic
    if bot_latency < 100:
        status = "🟢 Excellent Latency"
    elif bot_latency < 200:
        status = "🟡 Good Latency"
    else:
        status = "🔴 Poor Latency"

    embed = discord.Embed(
        title="SecureX",
        color=discord.Color.green()
    )

    # ✅ This line creates the profile + username display at the top left
    embed.set_author(name=str(ctx.author.display_name), icon_url=ctx.author.display_avatar.url)

    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/YOUR_BOT_ID/YOUR_ICON.png")  # Replace with bot/server icon

    embed.add_field(name="📶 Bot Latency", value=f"```{bot_latency}ms```", inline=True)
    embed.add_field(name="💾 Database Latency", value=f"```{db_latency}ms```", inline=True)
    embed.add_field(name="📡 Status", value=f"{status}", inline=False)

    await ctx.send(embed=embed)

# 23. Member Count
@bot.command(aliases=["mc","membercount"])
async def member_count(ctx):
    guild = ctx.guild
    total_members = guild.member_count
    humans = len([m for m in guild.members if not m.bot])
    bots = len([m for m in guild.members if m.bot])

    embed = discord.Embed(
        title=f" {guild.name}- Member Statistics",
        color=discord.Color.blue()
    )

    # 👤 Author icon and title bar
    embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else ctx.author.display_avatar.url)

    # 👥 Stats
    embed.add_field(name="👥 Total Members", value=f"```{total_members}```", inline=True)
    embed.add_field(name="🧍 Humans", value=f"```{humans}```", inline=True)
    embed.add_field(name="🤖 Bots", value=f"```{bots}```", inline=True)

    # Footer
    embed.set_footer(text=f"Requested by {ctx.author} • Today at {ctx.message.created_at.strftime('%H:%M')}")
    
    await ctx.send(embed=embed)


# 24. Nick
@bot.command(aliases=["nk"])
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member = None, *, nickname: str = None):
    if not member or nickname is None:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!nick,nk <@user> <new nickname>```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Changes the nickname of a specified member.", inline=False)
        await ctx.send(embed=embed)
        return

    try:
        old_nick = member.display_name
        await member.edit(nick=nickname, reason=f"Changed by {ctx.author}")
        embed = discord.Embed(
            description=f"✏️ Nickname for {member.mention} changed from `{old_nick}` to `{nickname}`",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("AUKAT ME RHO")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 25. React
@bot.command()
@commands.has_permissions(manage_messages=True)
async def react(ctx, emoji: str = None, message_id: int = None):
    if not emoji:
        embed = discord.Embed(
            title="Usage",
            description="```bash\n!react <emoji> [message_id]```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Help", value="Reacts to a message with the given emoji. If no ID is provided, it reacts to your last message.", inline=False)
        await ctx.send(embed=embed)
        return

    try:
        if message_id:
            message = await ctx.channel.fetch_message(message_id)
        else:
            async for msg in ctx.channel.history(limit=10):
                if msg.author == ctx.author:
                    message = msg
                    break

        await message.add_reaction(emoji)
        embed = discord.Embed(
            description=f"✅ Reacted to [this message]({message.jump_url}) with {emoji}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except discord.NotFound:
        await ctx.send("❌ Could not find the message.")
    except discord.HTTPException:
        await ctx.send("❌ Invalid emoji or too many reactions.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# 26. Server Avatar
@bot.command(aliases=["serverav", "serveravatar","sav"])
async def server_av(ctx):
    guild = ctx.guild
    if guild.icon:
        embed = discord.Embed(
            title=f"{guild.name}'s Server Icon",
            description=f"[Click to view full size]({guild.icon.url})",
            color=discord.Color.blurple()
        )
        embed.set_image(url=guild.icon.url)
    else:
        embed = discord.Embed(
            description="❌ This server has no icon set.",
            color=discord.Color.red()
        )

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


# 27. Server Info
@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild

    embed = discord.Embed(
        title=f"Server Info - {guild.name}",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=guild.icon.url if guild.icon else ctx.author.display_avatar.url)

    embed.add_field(name="📛 Name", value=guild.name, inline=True)
    embed.add_field(name="🆔 ID", value=f"`{guild.id}`", inline=True)
    embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)

    embed.add_field(name="📅 Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
    embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
    embed.add_field(name="🔗 Boosts", value=f"{guild.premium_subscription_count} (Tier {guild.premium_tier})", inline=True)

    embed.add_field(name="💬 Text Channels", value=len(guild.text_channels), inline=True)
    embed.add_field(name="🔊 Voice Channels", value=len(guild.voice_channels), inline=True)
    embed.add_field(name="🔧 Roles", value=len(guild.roles), inline=True)

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

# 28. User Info
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
    roles_list = ", ".join(roles) if roles else "No roles"

    embed = discord.Embed(
        color=discord.Color.red()
    )

    # ✅ Set author name and icon
    embed.set_author(
        name=f"User information for {member.display_name} !!",
        icon_url=member.display_avatar.url
    )

    # Thumbnail and details
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="ID", value=str(member.id), inline=True)
    embed.add_field(name="Guild Joined", value=member.joined_at.strftime("%a, %d %b %Y %H:%M:%S GMT"), inline=False)
    embed.add_field(name="Discord Registered", value=member.created_at.strftime("%a, %d %b %Y %H:%M:%S GMT"), inline=False)
    embed.add_field(name=f"Roles [{len(roles)+1}]", value=roles_list + ", @everyone", inline=False)
    embed.add_field(name="Avatar–URL", value=member.display_avatar.url, inline=False)

    embed.set_footer(text=f"Requested by {ctx.author} • Today at {ctx.message.created_at.strftime('%H:%M')}")
    await ctx.send(embed=embed)

# 29. Setup Ticket
@bot.command()
async def setup_ticket(ctx):
    embed = discord.Embed(title="🎫 Need Help?", description="React to open a ticket!", color=0x3498db)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎟️")

    def check(reaction, user):
        return str(reaction.emoji) == "🎟️" and reaction.message.id == msg.id

    @bot.event
    async def on_reaction_add(reaction, user):
        if reaction.emoji == "🎟️" and not user.bot:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await ctx.guild.create_text_channel(f"ticket-{user.name}", overwrites=overwrites)
            await channel.send(f"🎫 Hello {user.mention}, how can we help you?")

# Giveaways
import asyncio
import random
from discord.ext import commands
import discord

@bot.command(aliases=["gstart", "giveaway"])
@commands.has_permissions(manage_guild=True)
async def giveaways(ctx, duration: str = None, winners: int = None, *, prize: str = None):
    if not duration or not winners or not prize:
        embed = discord.Embed(
            title="🎉 Giveaway Usage",
            description="```bash\n.giveaways <duration> <winners> <prize>```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Example", value=".giveaways 1m 1 Nitro", inline=False)
        await ctx.send(embed=embed)
        return

    # Convert duration (e.g. 1m, 2h) to seconds
    time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    try:
        unit = duration[-1]
        if unit not in time_units:
            raise ValueError()
        time_seconds = int(duration[:-1]) * time_units[unit]
    except:
        return await ctx.send("❌ Invalid duration format. Use s/m/h/d (e.g. 10m for 10 minutes)")

    # Giveaway embed
    embed = discord.Embed(
        title="🎉 Giveaway",
        description=f"**Prize:** {prize}\n\nReact with 🎉 to enter!\nHosted by: {ctx.author.mention}\nEnds in: `{duration}`",
        color=discord.Color.gold()
    )
    embed.set_footer(text="Giveaway ends soon. Best of luck!")
    giveaway_message = await ctx.send(embed=embed)
    await giveaway_message.add_reaction("🎉")

    await asyncio.sleep(time_seconds)

    # Fetch updated message
    new_msg = await ctx.channel.fetch_message(giveaway_message.id)
    users = await new_msg.reactions[0].users().flatten()
    users = [user for user in users if not user.bot]

    if len(users) < winners:
        await ctx.send("❌ Not enough participants to choose winners.")
        return

    winners_list = random.sample(users, winners)
    winner_mentions = ", ".join(winner.mention for winner in winners_list)

    result_embed = discord.Embed(
        title="🎉 Giveaway Ended",
        description=f"**Prize:** {prize}\n🏆 Winner(s): {winner_mentions}",
        color=discord.Color.green()
    )
    result_embed.set_footer(text="Thanks for participating!")
    await ctx.send(embed=result_embed)


# Replace with your bot token
bot.run("MTIwNjA3NDM3MTAxMDA3MjU5Ng.G3P2uM.dn1tgYAEVB5EXC6JgsgaYY9xQ94gFGyeOLYdoc")
