# Imports
import random as r
import time as t
import csv
import numpy as np
import pandas as pd
import asyncio as a
import discord
from discord.ext import commands
from discord import Interaction

# Intents
intents = discord.Intents.all()
intents.message_content = True
intents.members = True

# bot init (tookin at bottom)
bot = commands.Bot(command_prefix="!", intents=intents)


# actions on bot start
@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")
    print(f"Bot ID: {bot.user.id}")
    print("---------------------------")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="you")
    )
    await bot.tree.sync()


# actions on message
# checks if user is server member
@bot.event
async def on_message(message):
    # Ignore messages from the bot
    if message.author == bot.user or message.author.bot:
        return

    await bot.process_commands(message)


# commands
# shutdown
@bot.tree.command(name="shutdown", description="Shuts down the bot")
async def shutdown(interaction: discord.Interaction):
    await interaction.response("Shutting down...")
    await bot.close()


# user info
@bot.command(aliases=["uinfo", "whois"], description="Get info about a user")
async def userinfo(ctx, member: discord.Member = None):
    # Generating dataframe
    df = pd.read_csv("scores.csv")
    df.columns = ["name", "score"]
    df = df.sort_values(by="score", ascending=False, ignore_index=True)
    # confirms if member is specified
    if member is None:
        member = ctx.author
    # gets member info
    roles = [role for role in member.roles]
    embed = discord.Embed(
        title="User Info",
        description=f"Here is the info we retrieved about {member.mention}",
        color=discord.Color.blue(),
        timestamp=ctx.message.created_at,
    )
    embed.set_thumbnail(url=member.avatar)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(
        name="Name", value=f"USER:{member.name}\nALIAS:{member.display_name}"
    )
    embed.add_field(name="Status", value=member.status)
    embed.add_field(
        name="Created at",
        value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
    )
    embed.add_field(
        name="Joined at", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
    )
    embed.add_field(
        name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles])
    )
    embed.add_field(name="Top role", value=member.top_role.mention)
    embed.add_field(name="Message count", value="0")
    embed.add_field(name="Autism level", value="uh oh broken")
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
    await ctx.send(embed=embed)


# test request
@bot.command()
async def test(ctx):
    # initial embed for rainbow colours
    colours = [
        0x32A852,
        0x3296A8,
        0xB700FF,
        0x9232A8,
        0xA8326F,
        0xF25207,
        0x3EFA00,
        0xFA0000,
    ]
    embed = discord.Embed(
        title="Autism Test",
        description="Dare you enter?",
        color=r.choice(colours),
        timestamp=ctx.message.created_at,
    )
    # return embed
    embed.add_field(
        name="Test",
        value="https://www.clinical-partners.co.uk/for-adults/autism-and-aspergers/adult-autism-test",
    )
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
    msg = await ctx.send(embed=embed)

    # loop for rainbow colours
    for x in range(1000):
        embed2 = discord.Embed(
            title="Autism Test",
            description="Dare you enter?",
            color=r.choice(colours),
            timestamp=ctx.message.created_at,
        )
        embed2.add_field(
            name="Test",
            value="https://www.clinical-partners.co.uk/for-adults/autism-and-aspergers/adult-autism-test",
        )
        await a.sleep(0.5)
        await msg.edit(embed=embed2)

    await ctx.send(
        "Heres the test https://www.clinical-partners.co.uk/for-adults/autism-and-aspergers/adult-autism-test"
    )


# add member
@bot.command(aliases=["add", "update"])
async def add_member(ctx, member: discord.Member = None, score: int = 0):
    # resolves to author if no member is specified
    if member is None:
        member = ctx.author
    # generating dataframe
    df = pd.read_csv("scores.csv")
    df.columns = ["name", "score"]
    # checks if member is in dataframe
    if member.name not in df["name"].values:
        # adds member to dataframe by creating new DF and concatenating
        new_row = pd.DataFrame({"name": member.name, "score": score}, index=[0])
        df = pd.concat([df, new_row], ignore_index=True)
        # sorts and saves dataframe to csv
        df.sort_values(by="score", ascending=False, ignore_index=True)
        df.to_csv("scores.csv", index=False)
        # prints and sends message
        print(f"Added member {member.name} with score {score}")
        await ctx.send(f"Added {member.name} with score {score}")

    elif member.name in df["name"].values:
        # finds member in dataframe and changes score
        df.loc[df["name"] == member.name, "score"] = score
        # sorts and saves dataframe to csv
        df.sort_values(by="score", ascending=False, ignore_index=True)
        df.to_csv("scores.csv", index=False)
        # prints and sends message
        print(f"Updated {member.name} with score {score}")
        await ctx.send(f"Updated {member.name} with score {score}")


# remove member
@bot.command(aliases=["remove"])
async def remove_member(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    # generating dataframe
    df = pd.read_csv("scores.csv")
    df.columns = ["name", "score"]
    # finds member in dataframe
    member_row = df.loc[df["name"] == member.name]
    sorted_member_row = member_row.sort_values(by="score", ascending=False)
    target_row = sorted_member_row.iloc[0]
    # removes row with member name
    df = df.drop(target_row.name, axis=0)
    # saves dataframe to csv
    df.to_csv("scores.csv", index=False)
    # prints and sends message
    print(f"Removed member {member.name}")
    await ctx.send(f"Removed member {member.name}")


# leaderboard
@bot.command(aliases=["ranks", "scores"])
async def leaderboard(ctx):
    # Generating dataframe
    df = pd.read_csv("scores.csv")
    df.columns = ["name", "score"]
    df = df.sort_values(by="score", ascending=False, ignore_index=True)
    print(df)
    # initial embed for rainbow colours
    colours = [
        0x32A852,
        0x3296A8,
        0xB700FF,
        0x9232A8,
        0xA8326F,
        0xF25207,
        0x3EFA00,
        0xFA0000,
    ]
    embed = discord.Embed(
        title="Autismo 3000",
        description="All alone :(",
        color=r.choice(colours),
        timestamp=ctx.message.created_at,
    )
    # return embed
    # if no members on leaderboard
    if len(df) == 0:
        print("No members")
        embed.add_field(name="Scores", value="No members")
        await ctx.send(embed=embed)
    # if members on leaderboard
    if len(df) != 0:
        embed.add_field(name="Scores", value=df.to_string(index=False))
        msg = await ctx.send(embed=embed)
        # loop for rainbow colours
        for x in range(1000):
            embed2 = discord.Embed(
                title="Autismo 3000",
                description=f"Winner: {df.iloc[0]['name']}",
                color=r.choice(colours),
                timestamp=ctx.message.created_at,
            )
            embed2.add_field(name="Scores", value=df.to_string(index=False))
            await a.sleep(0.5)
            await msg.edit(embed=embed2)


# bot tookin
bot.run("MTA4NjMyMzkyOTE4ODE1NTQ3Mw.GQzdA8._gspe6YkTnMVnTjie9nPtfLEDcvAJ9Eu8Z1F1E")
