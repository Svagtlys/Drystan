import gspread
from oauth2client.service_account import ServiceAccountCredentials

from math import ceil
from random import randint
import re
import discord
from discord.ext import commands
from discord.errors import HTTPException


prefix = ">"
bot = commands.Bot(command_prefix=prefix)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('Drystan-fda22d2bcc9d.json', scope)

gc = gspread.authorize(credentials)

@bot.event
async def on_ready():
    print("My name is Drystan, and I'll be your mechanics handler today!")


@bot.command()
async def ping(ctx):
    '''
    This command shows the ping of the bot to your server
    '''
    # Get the latency of the bot
    latency = bot.latency  # Included in the Discord.py library
    # Send it to the user
    await ctx.send(latency)


@bot.command()
async def sheet(ctx, inputsheet): #will be expanded later for the purposes of character importation
    '''
    This command will accept the link to a google sheet following the DRPG character sheet template, and will be able to parse the data on it
    '''
    savedvars = gc.open(inputsheet).worksheet("Helper Sheet") #accepts the name for a google sheet and finds the saved variables worksheet
    
    await ctx.send(savedvars.get_all_records())


@bot.command()
async def roll(ctx, *, content:str):
    '''
    Accepts the one or more args that are given as strings, and returns a fully completed and formatted roll embed
    Regex:                                           | Examples:
    Roll - ^[0-9]+d[0-9]+                            | 1d20 ; 50d30
    Operation - [(\+)(\-)(\*)(/)(\%)(\^)][\s]?[0-9]+ | +5 ; - 100 ; /3 ; ^4
    Vantage - \\s([ad])(van)                          | avan ; dvan
    Title - \\s(&t\s?")([^"]+)(")                     | &t "I'm attacking!"
    Description - \\s(&d\s?")([^"]+)(")               | &d "Depiction of me stabbing his eye out: ~|-- O"
    '''
    
    numdice = 0
    numsides = 0
    operations = []
    explosions = []
    vantage = 0 #0 - None; 1 - Advantage; 2 - Disadvantage

    giventitle = ""
    givendesc = ""
    
    regexroll = r"^[0-9]+d[0-9]+"
    regexoperation = r"[\s]?[(\+)(\-)(\*)(/)(\%)(\^)][\s]?[0-9]+"
    regexexplosion = r"\s?!{1,2}[0-9]*"
    regexvantage = r"\s([ad])(van)"
    regextitle = r'\s(&t\s?")([^"]+)(")'
    regexdesc = r'\s(&d\s?")([^"]+)(")'
    flags = re.I
    #use re.compile(regexthing, flags).search(content) to get the first instance returned as a match case   https://docs.python.org/3/library/re.html#match-objects

    matchcase = re.compile(regextitle, re.I).search(content)
    while(matchcase): #Title for embed
        if giventitle:
            errorList.append("You really shouldn't give me two titles")
        giventitle += str(matchcase.group(2))
        content = content[:matchcase.start()] + content[matchcase.end():]
        matchcase = re.compile(regextitle, re.I).search(content)

    matchcase = re.compile(regexdesc, re.I).search(content)
    while(matchcase): #Description for embed
        if givendesc:
            errorList.append("You really shouldn't give me two descriptions")
        givendesc += str(matchcase.group(2))
        content = content[:matchcase.start()] + content[matchcase.end():]
        matchcase = re.compile(regexdesc, re.I).search(content)
    
    matchcase = re.compile(regexroll, flags).search(content)
    while(matchcase): #A valid roll was found - find d, slice on either side, set as num dice and num sides
        numdice = int(content[matchcase.start():matchcase.start()+matchcase.group(0).find("d")])
        numsides = int(content[matchcase.start()+matchcase.group(0).find("d")+1:matchcase.end()])
        content = content[:matchcase.start()] + content[matchcase.end():]
        matchcase = re.compile(regexroll, flags).search(content)
    
    matchcase = re.compile(regexoperation, flags).search(content)
    while(matchcase): #A valid operation was found - add to operation list to be used later
        operations.append(matchcase.group(0))
        content = content[:matchcase.start()] + content[matchcase.end():]
        matchcase = re.compile(regexoperation, flags).search(content)

    matchcase = re.compile(regexexplosion, flags).search(content)
    while(matchcase): #A valid operation was found - add to operation list to be used later
        explosions.append(matchcase.group(0))
        content = content[:matchcase.start()] + content[matchcase.end():]
        matchcase = re.compile(regexexplosion, flags).search(content)
    
    matchcase = re.compile(regexvantage, flags).search(content)
    while(matchcase): #Advantage or disadvantage was found in the content
        first = matchcase.group(1)
        if first == "a":
            vantage = 1
        elif first == "d":
            vantage = 2
        content = content[:matchcase.start()] + content[matchcase.end():]
        matchcase = re.compile(regexoperation, flags).search(content)
        
        
    rolls = [] #list of rolls for editing
    formattedrolls = [] #list of formatted rolls to be displayed in the "Rolled" field
    total = 0 #int displayed in the "Total"
    errorList = []

    if numdice == 0:
        errorList.append("You can't have zero dice")
        total = "Impossible"
    if numdice < 0:
        errorList.append("You can't have negative dice")
        total = "Impossible"
    if numsides == 0:
        errorList.append("You can't have zero sides on your dice")
        total = "Impossible"
    if numsides < 0:
        errorList.append("You can't have negative sides on your dice")
        total = "Impossible"
    if numsides*numdice > 100000:
        errorList.append("That's a very large roll you're asking me to do for free, and I'm not doing it")
        total = "Impossible"
    else:
        if vantage == 0: #no vantage/normal rolling
            for i in range(numdice): #roll based on numdice and numsides, add formatted strings to totalrolled and ints to totalofcall
                rolls.append(randint(1,numsides))
                formattedrolls = rolls.copy()
        else: #some vantage (as yet undetermined)
            for i in range(numdice*2):
                rolls.append(randint(1,numsides))
        
            #format the crits, then simultaneously remove from rolls/crossout in formattedrolls for avan/dvan
            formattedrolls = rolls.copy()

            if vantage == 1: #advantage
                for i in range(numdice):
                    minind = rolls.index(min(rolls))
                    formattedrolls[minind] = "~~" + str(formattedrolls[minind]) + "~~"
                    rolls[minind] = float('inf')
                    
            elif vantage == 2: #disadvantage
                for i in range(numdice):
                    maxind = rolls.index(max(rolls))
                    formattedrolls[maxind] = "~~" + str(formattedrolls[maxind]) + "~~"
                    rolls[maxind] = float('-inf')
                    

        #apply explosions to rolls post advantage
        for i in explosions:
            explosion = re.search(r"!{1,2}", i).group(0)
            if re.search(r"[0-9]*", i).group(0) == "":
                operand = numsides
            else:
                operand = re.search(r"[0-9]*", i).group(0)
            if operand > numsides: #Make sure the explosion is valid
                errorList.append("You can't explode on a number greater than the highest possible roll")
                if explosion == "!":
                    formattedrolls.append("|")
                    for i in range(len(rolls)):
                        if rolls[i] == operand:
                            rando = randint(1,numsides)
                            rolls.append(rando)
                            formattedrolls.append(rando)
                elif explosion == "!!":
                    newrolls = []
                    for i in range(len(rolls)):
                        if rolls[i] == operand:
                            newrolls.append(randint(1,numsides))
                    while operand in newrolls:
                        rolls.extend(newrolls)
                        formattedrolls.append("|")
                        formattedrolls.extend(newrolls)
                        i = 0
                        while i < len(newrolls)-1:
                            if newrolls[i] == operand:
                                newrolls[i] = randint(1,numsides)
                                i += 1
                            else:
                                newrolls.pop(i)
                    rolls.extend(newrolls)
                    formattedrolls.append("|")
                    formattedrolls.extend(newrolls)
                    

        #format completed rolls
        for i in range(len(formattedrolls)):
            if toInt(formattedrolls[i]) == numsides:
                formattedrolls[i] = "__**" + str(formattedrolls[i]) + "**__"
            if rolls[i] == float('inf') or rolls[i] == float('-inf'):
                    rolls[i] = 0
        #add rolls together
        for i in rolls:
            total += i

        if total == float('inf') or total == float('-inf'):
            print(listToString(", ", rolls))
        
        #apply operations to total
        for i in operations: 
            operator = re.search(r"[(\+)(\-)(\*)(/)(\%)(\^)]", i).group(0)
            operand = int(re.search(r"[0-9]+", i).group(0))
            if operator == "+":
                total += operand
            elif operator == "-":
                total -= operand
            elif operator == "*":
                total *= operand
            elif operator == "/":
                if operand == 0: #Make sure the divisor isn't 0
                    errorList.append("You can't divide by zero")
                    continue
                else:
                    total /= operand
            elif operator == "%":
                if operand == 0: #Make sure the divisor isn't 0
                    errorList.append("You can't modulo by zero")
                    continue
                else:
                    total %= operand
            elif operator == "^":
                total **= operand


    if giventitle == "":
        giventitle = "Roll"
    if givendesc == "":
        givendesc = "How beautiful it is!"
    
    vantagename = ""
    if vantage == 1:
        vantagename = "Advantage"
    elif vantage == 2:
        vantagename = "Disadvantage"
    else:
        vantagename = "None"
        
    try:
        embed = discord.Embed(title = "**" + giventitle + "**", description = "*" + givendesc + "*", color=0x89eaf8)
    except HTTPException:
        await ctx.send("Your title and description are too long!  Shorten one or both.")

    if embed:
        embed.add_field(name = "Vantage", value = vantagename, inline = True)
        embed.add_field(name = "Explosiveness", value = "None", inline = True)
        if len(listToString(", ", formattedrolls)) < 1024 - len("Rolled " + str(numdice) + "d" + str(numsides)):
            embed.add_field(name = "Rolled " + str(numdice) + "d" + str(numsides), value = listToString(", ", formattedrolls), inline = False)
        else:
            embed.add_field(name = "Rolled " + str(numdice) + "d" + str(numsides), value = "Exceeds displayable length", inline = False)
        embed.add_field(name = "Operators", value = listToString(", ", operations), inline = False)
        embed.add_field(name = "Total", value = str(total), inline = False)
        embed.set_footer(text = "Errors: " + listToString("\n", errorList))
    await ctx.send(None, embed = embed)


@bot.command(pass_context=True) 
async def savetable(ctx):

    matchcase = re.compile(regexvantage, flags).search(content)
    
    author = ctx.message.author
    name = ctx.message.content
    link = ctx.message.content

    tablesheet = gc.open().worksheet()
    await ctx.send(author.mention + ", I've saved your table named " + name + " which can be found at " + link)


def listToString(separator, mylist):
    result = ""
    for i in range(len(mylist)):
        result += str(mylist[i])
        if i < len(mylist)-1:
           result += str(separator)
    if result == "":
        return "None"
    else:
        return result

def toInt(nonint):
    return int(re.compile(r"[0-9]+", re.I).search(str(nonint)).group(0))


bot.run('') #where 'inside miniquotes' is bot token

##@bot.command()
##async def sum(ctx, *nums):
##    '''
##    This command adds two or more numbers together
##    '''
##    try:
##        result = 0
##
##        for index in range(len(nums)):
##            result += int(nums[index])
##            
##    except ValueError:
##        await ctx.send("That's an invalid argument!")
##        print("sumall ValueError")
##        
##    else:
##        await ctx.send(result)
