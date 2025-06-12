import discord
from discord import app_commands
from datetime import timedelta
import random as rand
import asyncio
from keep_alive import keep_alive
keep_alive()


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
gameList = {}
class OnGoingGame:
    def __init__(self, Player1: discord.Member, Player2: discord.Member, live_bullets: int, bet: str):
        self.live_or_not = False
        self.bullets_left = 6
        self.live_bullets = live_bullets
        self.messagePlayer = Player1
        self.opposingPlayer = Player2
        self.bet = bet
        self.turn = False
    def __str__(self):
        return str(self.messagePlayer) + " challenged " + str(self.opposingPlayer) + " with " + str(self.bullets_left) + " left"
    def roll_bullet(self):
        if self.bullets_left < self.live_bullets:
            raise Exception("Bullets lower then one")
        random_number = rand.randint(1, self.bullets_left)
        if random_number <= self.live_bullets:
            self.live_or_not = True
            return self.live_or_not
        self.bullets_left -= 1
        self.turn = not self.turn
        return self.live_or_not
    def ToPlayer(self, reverse = False):
        if self.turn:
            if not reverse:
                return self.opposingPlayer
            return self.messagePlayer
        else:
            if not reverse:
                return self.messagePlayer
            return self.opposingPlayer
async def finishGame(messageID, punishedPlayer):
    print(punishedPlayer.roles)
    if gameList[messageID].bet != "sad (No punishment)":
        for i in punishedPlayer.roles:
            try:
                await punishedPlayer.remove_roles(i)
            except Exception as E:
                print(str(i) + " couldn't be removed cuz: " + str(E))
    match gameList[messageID].bet:
        case "timed out":
            try: await punishedPlayer.timeout(timedelta(days = 1), reason = "Lost in Russian Roulette, Loser.")
            except:
                pass
        case "banned":
            try: await punishedPlayer.ban(reason = "Lost in Russian Roulette, Loser.")
            except:
                pass
        case "kicked":
            try: await punishedPlayer.kick(reason="Lost in Russian Roulette, Loser.")
            except:
                pass
        case "sad (No punishment)":
            pass
    gameList.pop(messageID)
class opponentButtons(discord.ui.View):
    @discord.ui.button(label="Yourself", style=discord.ButtonStyle.danger, emoji='🔫')
    async def shootself_button_callback(self, inter, button=discord.Button):
        if gameList[inter.message.id].roll_bullet():
            loseEmbed = discord.Embed(title="💥 Live!",
                                        description=str(gameList[inter.message.id].ToPlayer()) + " will now be " + gameList[inter.message.id].bet,
                                        color=discord.Colour.dark_red())
            punishedPlayer = gameList[inter.message.id].ToPlayer()
            await finishGame(inter.message.id, await inter.guild.fetch_member(punishedPlayer.id))
            await inter.message.edit(embed=loseEmbed, view=None)
            return
        blankEmbed = discord.Embed(title="Blank.",
                                   description=str(gameList[inter.message.id].ToPlayer(reverse = True)) + " is spared.")
        await inter.message.edit(embed=blankEmbed, view=None)
        await asyncio.sleep(2)
        nextturnEmbed = discord.Embed(title="It's " + str(gameList[inter.message.id].ToPlayer()) + " turn.",
                                   description="Choose who you want to shoot.")
        print(inter.message.id)
        await inter.message.edit(embed=nextturnEmbed, view=gameButtons())
class gameButtons(discord.ui.View):
    @discord.ui.button(label="Yourself", style=discord.ButtonStyle.danger, emoji='🔫')
    async def shootself_button_callback(self, inter, button=discord.Button):
        if inter.user == gameList[inter.message.id].ToPlayer():
            if gameList[inter.message.id].roll_bullet():
               loseEmbed = discord.Embed(title="💥 Live!",
                                         description=str(gameList[inter.message.id].ToPlayer()) + " lost!\n" + str(gameList[inter.message.id].ToPlayer(reverse = True)) + " wins!\n" + str(gameList[inter.message.id].ToPlayer()) + " will now be " + gameList[inter.message.id].bet,
                                         color=discord.Colour.dark_red())
               punishedPlayer = gameList[inter.message.id].ToPlayer() 
               await finishGame(inter.message.id, await inter.guild.fetch_member(punishedPlayer.id))
               await inter.message.edit(embed=loseEmbed, view=None)
               return
            blankEmbed = discord.Embed(title="Blank.",
                                       description=str(gameList[inter.message.id].ToPlayer(reverse = True)) + " is spared.")
            await inter.message.edit(embed=blankEmbed, view=None)
            await asyncio.sleep(2)
            nextturnEmbed = discord.Embed(title="It's " + str(gameList[inter.message.id].ToPlayer()) + " turn.",
                                       description="Choose who you want to shoot.")
            print(inter.message.id)
            await inter.message.edit(embed=nextturnEmbed, view=gameButtons())
        else:
            errorEmbed = discord.Embed(title = "Error! ❌", description = "You are not in this game/It's not your turn!", color = discord.Colour.red())
            await inter.response.send_message(embed = errorEmbed, ephemeral = True)


    @discord.ui.button(label="Opponent", style=discord.ButtonStyle.danger, emoji='🧑')
    async def shootopponent_button_callback(self, inter, button=discord.Button):
        if gameList[inter.message.id].ToPlayer() == inter.user:
            if gameList[inter.message.id].roll_bullet():
                loseEmbed = discord.Embed(title="💥 Live!",
                                            description=str(gameList[inter.message.id].ToPlayer(reverse = True)) + " lost!\n" + str(gameList[inter.message.id].ToPlayer()) + " wins!\n" + str(gameList[inter.message.id].ToPlayer(reverse = True)) + " will now be " + gameList[inter.message.id].bet,
                                            color=discord.Colour.dark_red())
                punishedPlayer = gameList[inter.message.id].ToPlayer(reverse=True)
                await finishGame(inter.message.id, await inter.guild.fetch_member(punishedPlayer.id))
                await inter.message.edit(embed=loseEmbed, view=None)
                return
            gameList[inter.message.id].turn = not gameList[inter.message.id].turn
            blankEmbed = discord.Embed(title="Blank.",
                                       description=str(gameList[inter.message.id].ToPlayer(reverse = True)) + " is spared.")
            await inter.message.edit(embed=blankEmbed, view=None)
            await asyncio.sleep(2)
            nextturnEmbed = discord.Embed(title="It's " + str(gameList[inter.message.id].ToPlayer()) + " turn.",
                                       description="You have to shoot yourself.")
            print(inter.message.id)
            await inter.message.edit(embed=nextturnEmbed, view=opponentButtons())
        else:
            errorEmbed = discord.Embed(title="Error! ❌", description="You are not in this game/It's not your turn!",
                                       color=discord.Colour.red())
            await inter.response.send_message(embed=errorEmbed, ephemeral=True)
class discButtons(discord.ui.View):
    @discord.ui.button(label = "Deny", style = discord.ButtonStyle.danger, emoji = '✖️')
    async def deny_button_callback(self, inter, button = discord.Button):
        if gameList[inter.message.id].opposingPlayer == inter.user:
            denyEmbed2 = discord.Embed(title="Cancelled",
                                       description="Bet timed out or user denied.")
            await inter.message.edit(embed=denyEmbed2, view = None)
        else:
            errorEmbed = discord.Embed(title="Error! ❌", description="You are not being bet on!",
                                       color=discord.Colour.red())
            await inter.response.send_message(embed = errorEmbed, ephemeral = True)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji='✅')
    async def accept_button_callback(self, inter, button=discord.Button):
        if gameList[inter.message.id].opposingPlayer == inter.user:
            print(gameList)
            acceptEmbed = discord.Embed(title="It's " + str(gameList[inter.message.id].ToPlayer()) + " turn.",
                                   description="Choose who you want to shoot.")
            print(inter.message.id)
            await inter.response.edit_message(embed=acceptEmbed, view=gameButtons())
        else:
            errorEmbed = discord.Embed(title="Error! ❌", description="You are not being bet on!",
                                       color=discord.Colour.red())
            await inter.response.send_message(embed = errorEmbed, ephemeral = True)
@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")
@tree.command(
    name = "manual",
    description = "Learn how to play the game",
)
async def instruction(inter):
    InstructEmbed = discord.Embed(title = "Instruction", description = """ • There is a gun by default with 5 blanks and 1 live, this may be configured when you start a game
    
 • Each turn, one player gets the gun

 • The player may either shoot themselves or shoot the opponent

 • If the player shoots themselves and the bullet is a blank, the turn passes to the other player

 • If the player shoots the opponent and it's a blank, the player has to shoot themselves

 • The first person to get shot with a live bullet loses.
""", color = 800000)
    await inter.response.send_message(embed = InstructEmbed, ephemeral=True)
@tree.command(
    name = "bet",
    description = "begin a game of russian roulette"
)
@app_commands.describe(bets = "Bet stuff", member = "Member ur betting")
@app_commands.choices(bets = [
    app_commands.Choice(name = "Timeout", value = "timed out"),
    app_commands.Choice(name = "Ban", value = "banned"),
    app_commands.Choice(name = "Kick", value = "kicked"),
    app_commands.Choice(name = "None", value = "sad (No punishment)")])
async def begin(inter, member: discord.Member, live_bullets: int, bets: app_commands.Choice[str]):
    if live_bullets > 6 or live_bullets <= 0:
        errorEmbed = discord.Embed(title="Error! ❌", description="Invalid Live Bullet Amount!",
                                   color=discord.Colour.red())
        await inter.response.send_message(embed=errorEmbed, ephemeral=True)
        return
    if member == inter.user:
        errorEmbed = discord.Embed(title="Error! ❌", description="Cannot bet on yourself!",
                                   color=discord.Colour.red())
        await inter.response.send_message(embed=errorEmbed, ephemeral=True)
        return
    betEmbed = discord.Embed(title = str(inter.user) + " is challenging " + str(member), description = "Bet is being " + str(bets.value) + " with " + str(live_bullets) + " live bullets.\n For reference, this is around a " + str(int((live_bullets/6)*100)) + "% chance of a live bullet\non the first turn." )
    await inter.response.send_message(content = member.mention,embed=betEmbed, view = discButtons())
    messageResponse = await inter.original_response()
    gameList[messageResponse.id] = OnGoingGame(inter.user, member, live_bullets, str(bets.value))

client.run("stop tryna find my token goofy")