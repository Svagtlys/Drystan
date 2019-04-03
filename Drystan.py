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
    This command will accept the name of a shared google sheet following the DRPG character sheet template, and will be able to parse the data on "Helper Sheet 1" of it. Currently only returns the data found on that sheet.
    '''
    savedvars = gc.open(inputsheet).worksheet("Helper Sheet 1") #accepts the name for a google sheet and finds the saved variables worksheet
    
    await ctx.send(savedvars.get_all_records())


@bot.command()
async def roll(ctx, *, content:str):
    '''
    Accepts the one or more args that are given as strings, and returns a fully completed and formatted roll embed
    Regex:                                           | Examples:
    Roll - ^[0-9]+d[0-9]+                            | 1d20 ; 50d30
    Operation - [(\+)(\-)(\*)(/)(\%)(\^)][\s]?[0-9]+ | +5 ; - 100 ; /3 ; ^4
    Vantage - \\s([ad])(van)                         | avan ; dvan
    Explosion - \\s?!{1,2}[0-9]*                     | ! ; !6 ; !!13
    Title - \\s(&t\s?")([^"]+)(")                    | &t "I'm attacking!"
    Description - \\s(&d\s?")([^"]+)(")              | &d "Depiction of me stabbing his eye out: ~|-- O"
    '''
    
    giventitle = ""
    givendesc = ""
    errorList = []
    numdice = 0
    numsides = 0
    operations = []
    vantage = 0 #0 - None; 1 - Advantage; 2 - Disadvantage
    explosion = ""
    
    #use re.compile(regexthing, re.I).search(content) to get the first instance (ignoring case) returned as a match case   https://docs.python.org/3/library/re.html#match-objects

    temp = find_embed_info(content)
    content = temp[0]
    giventitle = temp[1]
    givendesc = temp[2]
    errorList.extend(temp[3])

    temp = find_roll_info(content)
    content = temp[0]
    numsides = temp[1]
    numdice = temp[2]
    errorList.extend(temp[3])
    impossible = temp[4]
    
    temp = find_operation_info(content)
    content = temp[0]
    operations = temp[1]

    temp = find_vantage_info(content)
    content = temp[0]
    vantage = temp[1]

    temp = find_explosion_info(content)
    content = temp[0]
    explosion = temp[1]

    #VARS TO USE FOR REST OF FUNCTION
    # giventitle / givendesc
    # numsides / numdice
    # errorList / impossible
    # operations / vantage / explosion
    rolls = []                          #list of rolls for editing
    formattedrolls = []                 #list of formatted rolls to be displayed in the "Rolled" field
    total = 0                           #int displayed in the "Total"

    if impossible is True and re.search("^[0-9]+",content,re.I) is None:
        total = "Impossible"
    else:
        if numsides == 0 and numdice == 0:
            matchcase = re.search("^[0-9]+",content,re.I)
            if matchcase:
                rolls = [int(matchcase.group(0))]
                formattedrolls = [int(matchcase.group(0))]
        else:
            #run the roll
            temp = run_roll(numdice, numsides, vantage, explosion, operations)
            rolls = temp[0]
            formattedrolls = temp[1]
            errorList.extend(temp[2])

            #format the roll
            temp = format_roll(rolls, formattedrolls, numsides)
            rolls = temp[0]
            formattedrolls = temp[1]
            
        #apply operations
        temp = run_operations(rolls, operations)
        rolls = temp[0]
        errorList.extend(temp[1])
        total = temp[2]
        

    if giventitle == "":
        giventitle = "Roll"
    if givendesc == "":
        givendesc = "The dice rattle against the table!"
    
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
        embed.add_field(name = "Explosiveness", value = explosion, inline = True)
        if len(listToString(", ", formattedrolls)) < 1024 - len("Rolled " + str(numdice) + "d" + str(numsides)):
            embed.add_field(name = "Rolled " + str(numdice) + "d" + str(numsides), value = listToString(", ", formattedrolls), inline = False)
        else:
            embed.add_field(name = "Rolled " + str(numdice) + "d" + str(numsides), value = "Exceeds displayable length", inline = False)
        embed.add_field(name = "Operators", value = listToString(", ", operations), inline = False)
        embed.add_field(name = "Total", value = str(total), inline = False)
        embed.set_footer(text = "Errors: " + listToString("\n", errorList))
    await ctx.send(None, embed = embed)


@bot.command()
async def rolltable(ctx, inputsheet):
    '''
    Rolls given a table with a sheet of "Main". See Table for Drystan for formatting.  Must be shared with sheeteditor@drystan.iam.gserviceaccount.com
    '''
    #result = ""

    sheet = gc.open(inputsheet)
    currtablevars = sheet.worksheet("Main").get_all_records()

    #read A1 to determine dice type
    #roll = 0

    await ctx.send(currtablevars)


@bot.command(pass_context=True) 
async def savetable(ctx, inputsheet):
    '''
    Doesn't save the table yet, because I've decided SQL would be better for storing, but I haven't yet learned it.
    '''
    
    author = ctx.message.author
    name = ctx.message.content
    link = ctx.message.content

    #tablesheet = gc.open("Drystan's Secret Sheet").worksheet("Saved Tables")
    await ctx.send(author.mention + ", I've saved your table named " + name + " which can be found at " + link)


def listToString(separator, mylist):
    result = ""
    for i in range(len(mylist)):
        result += str(mylist[i])
        if i < len(mylist)-1:
            if mylist[i] != "**|**" and mylist[i+1] != "**|**":
                result += str(separator)
            else:
                result += "  "
    if result == "":
        return "None"
    else:
        return result

def toInt(nonint):
    if nonint is None:
        return 0
    return int(re.compile(r"[0-9]+", re.I).search(str(nonint)).group(0))


#find embed info
def find_embed_info(content):
    regextitle = r'\s(&t\s?")([^"]+)(")'
    regexdesc = r'\s(&d\s?")([^"]+)(")'
    
    giventitle = ""
    givendesc = ""
    errorList = []

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

    return [content, giventitle, givendesc, errorList]

def find_roll_info(content):
    regexroll = r"^[0-9]+d[0-9]+"
    numsides = 0
    numdice = 0
    errorList = []
    impossible = False

    matchcase = re.compile(regexroll, re.I).search(content)
    while(matchcase): #A valid roll was found - find d, slice on either side, set as num dice and num sides
        numdice = int(content[matchcase.start():matchcase.start()+matchcase.group(0).find("d")])
        numsides = int(content[matchcase.start()+matchcase.group(0).find("d")+1:matchcase.end()])
        content = content[:matchcase.start()] + content[matchcase.end():]
        matchcase = re.compile(regexroll, re.I).search(content)

    if numdice == 0:
        errorList.append("You can't have zero dice")
        impossible = True
    if numdice < 0:
        errorList.append("You can't have negative dice")
        impossible = True
    if numsides == 0:
        errorList.append("You can't have zero sides on your dice")
        impossible = True
    if numsides < 0:
        errorList.append("You can't have negative sides on your dice")
        impossible = True
    if numsides*numdice > 100000:
        errorList.append("That's a very large roll you're asking me to do for free, and I'm not doing it!")
        impossible = True
    
    return [content, numsides, numdice, errorList, impossible]


def find_operation_info(content):
    regexoperation = r"[\s]?[(\+)(\-)(\*)(/)(\%)(\^)][\s]?[0-9]+"
    operations = []

    matchcase = re.compile(regexoperation, re.I).search(content)
    while(matchcase): #A valid operation was found - add to operation list to be used later
        operations.append(matchcase.group(0))
        content = content[:matchcase.start()] + content[matchcase.end():]
        matchcase = re.compile(regexoperation, re.I).search(content)

    return [content, operations]


def find_vantage_info(content):
    regexvantage = r"\s([ad]van)"
    vantage = 0
    
    matchcase = re.search("\s([ad])(van)",content,re.I)
    #print(str(matchcase) + " && " + str(matchcase.groups()))
    if matchcase: #Advantage or disadvantage was found in the content
        if matchcase.group(1).lower() == "a":
            vantage = 1
        elif matchcase.group(1).lower() == "d":
            vantage = 2
        content = content[:matchcase.start()] + content[matchcase.end():]

    return [content, vantage]


def find_explosion_info(content):
    regexexplosion = r"!{1,2}[0-9]*"
    explosion = ""
    
    matchcase = re.search(regexexplosion, content, re.I)
    if matchcase: #A valid explosion was found - add to explosion to be used later
        explosion = (matchcase.group(0))
        content = content[:matchcase.start()] + content[matchcase.end():]

    return [content, explosion]


# roll_dice function 
def run_roll(numdice, numsides, vantage, explosion, operations):
    rolls = []
    formattedrolls = []
    errorList = []

    #roll beginning bit
    for i in range(numdice):
        temp = randint(1,numsides)
        rolls.append(temp)
        formattedrolls.append(temp)

    #apply advantage to rolls
    temp = run_vantage(rolls, formattedrolls, vantage, numdice, numsides)
    rolls = temp[0]
    formattedrolls = temp[1]
                    
    #apply explosions to rolls post-advantage
    temp = run_explosion(rolls, formattedrolls, explosion, numdice, numsides)
    rolls = temp[0]
    formattedrolls = temp[1]
    errorList.extend(temp[2])

    #return everything
    return [rolls, formattedrolls, errorList]
    

def run_vantage(rolls, formattedrolls, vantage, numdice, numsides):
    #add second layer of dice rolls
    if vantage != 0:
        for i in range(numdice):
            temp = randint(1,numsides)
            rolls.append(temp)
            formattedrolls.append(temp)
    #format the crits, then simultaneously remove from rolls/crossout in formattedrolls for avan/dvan
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

    return [rolls, formattedrolls]


def run_explosion(rolls, formattedrolls, explosion, numdice, numsides):
    errorList = []
    if explosion != "":
        #see if exploding on num other than max/crit
        explodeon = re.search(r"[0-9]+", explosion)
        if explodeon is None:
            operand = numsides
        else:
            operand = int(explodeon.group(0))

        if operand > numsides: #Make sure the explosion is valid
            errorList.append("You can't explode on a number greater than the highest possible roll")
        #The actual explosion stuffs!
        elif "!!" in explosion:
            iterations = 0
            newrolls = []
            for i in range(len(rolls)):
                if rolls[i] == operand:
                    newrolls.append(randint(1,numsides))
            while operand in newrolls and iterations < 20:
                rolls.extend(newrolls)
                formattedrolls.append("|")
                formattedrolls.extend(newrolls)
                i = 0
                while i < len(newrolls):
                    if newrolls[i] == operand:
                        newrolls[i] = randint(1,numsides)
                        i += 1
                    else:
                        newrolls.pop(i)
                iterations += 1
            rolls.extend(newrolls)
            formattedrolls.append("|")
            formattedrolls.extend(newrolls)
            if iterations == 20:
                errorList.append("Too many expounded explosions")
        elif "!" in explosion:
            formattedrolls.append("|")
            for i in range(len(rolls)):
                if rolls[i] == operand:
                    rando = randint(1,numsides)
                    rolls.append(rando)
                    formattedrolls.append(rando)

    return [rolls, formattedrolls, errorList]
            

def run_operations(rolls, operations):
    errorList = []
    total = 0
    #add rolls together
    for i in rolls:
        total += i
    
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

    return [rolls, errorList, total]
            

def format_roll(rolls, formattedrolls, numsides):
    rolli = 0 #Because the | dividing exploded rolls is messing it up
    for i in range(len(formattedrolls)):
        if formattedrolls[i] == "|":
            formattedrolls[i] = "**|**"
            rolli -= 1
        elif toInt(formattedrolls[i]) == numsides:
            formattedrolls[i] = "__**" + str(formattedrolls[i]) + "**__"
        if rolli >= 0 and rolli < len(rolls):
            if rolls[rolli] == float('inf') or rolls[rolli] == float('-inf'):
                rolls[rolli] = 0
        rolli += 1
    
    return [rolls, formattedrolls]


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

## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL
## SUPER SECRET TOKEN AND ALL

bot.run('') #where 'inside miniquotes' is bot token