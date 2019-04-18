#region IMPORTS
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from math import ceil
from random import randint
import re
import discord
from discord.ext import commands
from discord.errors import HTTPException
#endregion
#region INITIATION
prefix = ">"
bot = commands.Bot(command_prefix=prefix)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('Drystan-fda22d2bcc9d.json', scope)

gc = gspread.authorize(credentials)

tempfile = open('private-tables.txt','r')
secrettable1 = tempfile.readline().strip()
secrettable2 = tempfile.readline().strip()
tempfile.close()
tempfile = open('bot-token.txt','r')
token = tempfile.readline()
tempfile.close()
#endregion

#region BASIC COMMANDS
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
#endregion
#region SAVE/LIST COMMANDS
@bot.command(pass_context = True)
async def savechar(ctx):
    '''
    >savechar charactername linktocharacter : Saves the character to a private googlesheet, must be shared with sheeteditor@drystan.iam.gserviceaccount.com
    '''
    await ctx.send(save_sheet(2, ctx))


@bot.command(pass_context=True)
async def savetable(ctx):
    '''
    >savetable tablename linktotable : Saves the table to a private googlesheet, must be shared with sheeteditor@drystan.iam.gserviceaccount.com
    '''
    
    await ctx.send(save_sheet(1, ctx))

@bot.command(pass_context = True)
async def listchars(ctx):
    '''
    >listchars (key) : List all characters saved by you. Type key after the command to view the keys as well.
    '''

    await ctx.send("\n".join(list_saved_sheets(2, ctx)))

@bot.command(pass_context = True)
async def listtables(ctx):
    '''
    >listtables (key) : List all tables saved by you. Type key after the command to view the keys as well.
    '''

    await ctx.send("\n".join(list_saved_sheets(1, ctx)))

#endregion
#region ROLL COMMANDS
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
            temp = run_operations(rolls, operations)
            rolls = temp[0]
            errorList.extend(temp[1])
            total = temp[2]
        else:
            #run the roll
            temp = run_roll(numdice, numsides, vantage, explosion, operations)
            rolls = temp[0]
            formattedrolls = temp[1]
            errorList.extend(temp[2])
            total = temp[3]
        
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
        embed.add_field(name = "Explosiveness", value = explosion if explosion else "None", inline = True)
        if len(listToString(", ", formattedrolls)) < 1024 - len("Rolled " + str(numdice) + "d" + str(numsides)):
            embed.add_field(name = "Rolled " + str(numdice) + "d" + str(numsides), value = listToString(", ", formattedrolls), inline = False)
        else:
            embed.add_field(name = "Rolled " + str(numdice) + "d" + str(numsides), value = "Exceeds displayable length", inline = False)
        embed.add_field(name = "Operators", value = listToString(", ", operations) if operations else "None", inline = False)
        embed.add_field(name = "Total", value = str(total), inline = False)
        embed.set_footer(text = "Errors: " + listToString("\n", errorList))
    await ctx.send(None, embed = embed)


@bot.command(pass_content=True)
async def rollchar(ctx):
    '''
    >rollchar linkhere option

    Pass read enable sharing link or name of saved character, and what score you want to roll
    Rolls given a character with a sheet named "Helper Sheet". See "Character for Drystan" for formatting.  Must be shared with sheeteditor@drystan.iam.gserviceaccount.com
    '''
    result = ""
    match = re.match("(\S+)\s(\S+)", ctx.message.content[10:], re.I)
    if match is None:
        await ctx.send("You need to provide two arguments")
        return
    inputsheet = match.group(1).strip()
    value = match.group(2).strip()
    sheet = None

    if re.match("https://drive.google.com/open\?id=\S+/", inputsheet, re.I) or re.match("https://docs.google.com/spreadsheets/d/\S+/edit\?usp=sharing", inputsheet, re.I):
        sheet = gc.open_by_key(proper_find_id(inputsheet))
    else:
        key = open_saved_sheet(2, ctx.message.author.id, inputsheet)
        if key is None:
            await ctx.send("You haven't saved a character named " + inputsheet)
            return
        sheet = gc.open_by_key(key)
    helpersheet = sheet.get_worksheet(len(sheet.worksheets())-1).get_all_values()

    if value == "str":
        value = "Strength Modifier"
    elif value == "dex":
        value = "Dexterity Modifier"
    elif value == "con":
        value = "Constitution Modifier"
    elif value == "int":
        value = "Intelligence Modifier"
    elif value == "wis":
        value = "Wisdom Modifier"
    elif value == "cha":
        value = "Charsima Modifier"
    else:
        await ctx.send("That's not a valid score to roll on!")
        return

    valueinfo = get_value(helpersheet, value) #value, formatted
    operations = [bonus_formatter(valueinfo[0])]
    temp = run_roll(1, 20, None, None, operations) #rolls, formattedrolls, errorlist, total

    try:
        embed = discord.Embed(title = "**" + str(sheet.title) + "**", description = "*You rolled " + str(temp[1]) + " " + listToString(", ", operations) + " (" + str(valueinfo[1]) + " bonus) = " + str(temp[3]) + "*\u0020", color=0x89eaf8)
    except HTTPException:
        await ctx.send("Your title and description are too long!  Shorten one or both.")
    
    await ctx.send(None, embed = embed)


@bot.command(pass_context=True)
async def rolltable(ctx):
    '''
    Pass read enable sharing link or name of saved table
    Rolls given a table with a sheet named "Main". See "Table for Drystan" for formatting.  Must be shared with sheeteditor@drystan.iam.gserviceaccount.com
    '''
    result = ""
    inputsheet = ctx.message.content[11:]
    sheet = None

    if re.match("https://drive.google.com/open\?id=\S+/", inputsheet, re.I) or re.match("https://docs.google.com/spreadsheets/d/\S+/edit\?usp=sharing", inputsheet, re.I):
        sheet = gc.open_by_key(proper_find_id(inputsheet))
    else:
        sheet = gc.open_by_key(open_saved_sheet(1, ctx.message.author.id, inputsheet))
    currtable = sheet.worksheet("Main")
    info = currtable.get_all_values() #list of lists [row][col]
    if len(info[0]) < 2:
        await ctx.send("You must have at least two columns: one for the rolling and one for the name.")
    foundrow = roll_on_table(info)

    name1 = info[foundrow][1]
    desc1 = ""
    name2 = ""
    desc2 = ""
    if len(info[foundrow]) <= 4:
        desc1 = info[foundrow][2]
        if info[foundrow][3] == "TRUE":
            currtable = sheet.worksheet(name1)
            info = currtable.get_all_values() #list of lists [row][col]
            foundrow = roll_on_table(info)
            name2 = info[foundrow][1]
            if len(info[foundrow]) > 2:
                desc2 = info[foundrow][2]

    try:
        embed = discord.Embed(title = "**" + name1 + "**", description = "*" + desc1 + "*" if desc1 else "", color=0x89eaf8)
    except HTTPException:
        await ctx.send("Your title and description are too long!  Shorten one or both.")

    if embed and name2:
        try:
            embed.add_field(name = name2, value = desc2 if desc2 else "\u200b", inline = True)
        except HTTPException:
            await ctx.send("Your secondary title and description are too long!  Shorten one or both.")
    
    await ctx.send(None, embed = embed)
#endregion
#region CHARACTER SHEET INTERACTION COMMANDS
@bot.command(pass_context=True)
async def showchar(ctx):
    '''
    >showchar character sheetpart    -      Input saved character key, or link to valid character sheet, and the part of the sheet you want to view
    Basic - Displays gender, deity, alignment, and experience
    Build - Displays race and subrace, as well as all classes and archetypes, and their associated level and hit die
    Abilities - Displays all ability scores and modifiers, as well as skill proficiencies and bonuses (Can also type Strength, Dexterity, Constitution, Intelligence, Wisdom or Charisma to view just one ability's table)
    Battle - Displays health, death saves, and AC, as well as remaining and maximum hit die
    Gear - Displays armor and shield, with bonus to AC and weight
    Complete - Displays all of the above

    Note: All of the above display your character's name, total level, and first class
    '''
    match = re.match("(\S+)\s(\S+)", ctx.message.content[9:].strip())
    if match is None:
        await ctx.send("You need to input two arguments")
        return
    inputsheet = match.group(1)
    sheetpart = match.group(2).lower()
    sheet = None

    if re.match("https://drive.google.com/open\?id=\S+/", inputsheet, re.I) or re.match("https://docs.google.com/spreadsheets/d/\S+/edit\?usp=sharing", inputsheet, re.I):
        sheet = gc.open_by_key(proper_find_id(inputsheet))
    else:
        key = open_saved_sheet(2, ctx.message.author.id, inputsheet)
        if key is None:
            await ctx.send("You haven't saved a character named " + inputsheet)
            return
        sheet = gc.open_by_key(key)
    helpersheet = sheet.worksheet("Helper Sheet").get_all_values()

    try:
        embed = discord.Embed(title = "**" + get_value(helpersheet, "Name")[0] + "**", description = "----------------------------------------------------------------------------------------", color=0x89eaf8)
    except HTTPException:
        await ctx.send("Your character's name is too long!  Shorten it to view in Discord.")
    if embed:
        blocks = block_builder(helpersheet, sheetpart)
        try:
            if sheetpart != "complete" and sheetpart != "abilities":
                embed.add_field(name = sheetpart.lower().capitalize(), value = (blocks[0])[1:])
            else:
                for i in blocks:
                    check = int(i[0])
                    embed.add_field(name = "Basic" if check == 1 else "" + "Build" if check == 2 else "" + "Abilities" if check == 3 else "" + "Battle" if check == 4 else "" + "Gear" if check == 5 else "Generic Name", value = i[1:])
        except IndexError:
            await ctx.send("That isn't a valid part of the character sheet.")
            return
    await ctx.send(None, embed = embed)
    
@bot.command(pass_context=True)
async def editchar(ctx):
    '''
    >editchar character     -   Input saved character key, or link to valid character sheet
    '''
    inputsheet = ctx.message.content[9:].strip()
    sheet = None

    if re.match("https://drive.google.com/open\?id=\S+/", inputsheet, re.I) or re.match("https://docs.google.com/spreadsheets/d/\S+/edit\?usp=sharing", inputsheet, re.I):
        sheet = gc.open_by_key(proper_find_id(inputsheet))
    else:
        key = open_saved_sheet(2, ctx.message.author.id, inputsheet)
        if key is None:
            await ctx.send("You haven't saved a character named " + inputsheet)
            return
        sheet = gc.open_by_key(key)
    helpersheet = sheet.worksheet("Helper Sheet").get_all_values()

    try:
        embed = discord.Embed(title = "**" + get_value(helpersheet, "Name")[0] + "**", description = "*Level " + get_value(helpersheet, "Level")[0] + " " + get_value(helpersheet, "Class 1")[0] + "*", color=0x89eaf8)
    except HTTPException:
        await ctx.send("Your character's name is too long!  Shorten it to view in Discord.")
    if embed:
        pass
    await ctx.send(None, embed = embed)
#endregion

#region HELPER FUNCTIONS / NON COMMANDS

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
    matchcase = re.compile(r"[0-9]+", re.I).search(str(nonint))
    if matchcase is None:
        return 0
    return int(matchcase.group(0))


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


def run_roll(numdice, numsides, vantage, explosion, operations):
    rolls = []
    formattedrolls = []
    errorList = []
    total = 0
    operand = 0

    #roll beginning bit
    for i in range(numdice):
        temp = randint(1,numsides)
        rolls.append(temp)
        formattedrolls.append(temp)

    #apply advantage to rolls
    if vantage != None:
        temp = run_vantage(rolls, formattedrolls, vantage, numdice, numsides)
        rolls = temp[0]
        formattedrolls = temp[1]
                    
    #apply explosions to rolls post-advantage
    if explosion != None:
        temp = run_explosion(rolls, formattedrolls, explosion, numdice, numsides)
        rolls = temp[0]
        formattedrolls = temp[1]
        errorList.extend(temp[2])
        operand = temp[3]


    #format the roll
    temp = format_roll(rolls, formattedrolls, numsides, operand)
    rolls = temp[0]
    formattedrolls = temp[1]

    #apply the operations
    if operations != None:
        temp = run_operations(rolls, operations)
        errorList.extend(temp[0])
        total = temp[1]

    #return everything
    return [rolls, formattedrolls, errorList, total]
    
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
    operand = 0
    if explosion != "":
        #see if exploding on num other than max/crit
        explodeon = re.search("[0-9]+", explosion)
        if explodeon is None:
            operand = numsides
        else:
            operand = int(explodeon.group(0))
        if operand > numsides: #Make sure the explosion is valid
            errorList.append("You can't explode on a number greater than the highest possible roll")
        #The actual explosion stuffs!
        elif "!!" in explosion and operand in rolls:
            iterations = 0
            newrolls = []
            for i in range(numdice):
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
        elif "!" in explosion and operand in rolls:
            formattedrolls.append("|")
            for i in range(numdice):
                if rolls[i] == operand:
                    rando = randint(1,numsides)
                    rolls.append(rando)
                    formattedrolls.append(rando)

    return [rolls, formattedrolls, errorList, operand]
            
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

    return [errorList, total]
            

def format_roll(rolls, formattedrolls, numsides, isexploding):
    rolli = 0 #Because the | dividing exploded rolls is messing it up
    for i in range(len(formattedrolls)):
        if formattedrolls[i] == "|":
            formattedrolls[i] = "**|**"
            rolli -= 1
        elif toInt(formattedrolls[i]) == numsides:
            formattedrolls[i] = "**" + str(formattedrolls[i]) + "**"
        elif toInt(formattedrolls[i]) == 1:
            formattedrolls[i] = "*" + str(formattedrolls[i]) + "*"
        if isexploding != 0 and toInt(formattedrolls[i]) == isexploding:
            formattedrolls[i] = "__" + str(formattedrolls[i]) + "__"
        if rolli >= 0 and rolli < len(rolls):
            if rolls[rolli] == float('inf') or rolls[rolli] == float('-inf'):
                rolls[rolli] = 0
        rolli += 1
    
    return [rolls, formattedrolls]


def roll_on_table(info):
    matchcase = re.search("^([0-9]+)(d)([0-9]+)", info[0][0], re.I)
    numdice = int(matchcase.group(1))
    dicetype = int(matchcase.group(3))
    roll = 0
    for i in range(numdice):
        roll += randint(1, dicetype)
    maxrow = len(info)-1
    minrow = 1
    foundrow = minrow + int((maxrow-minrow)/2)
    while(minrow <= maxrow):
        cellvalue = info[foundrow][0]
        if "-" in cellvalue:
            foundrange = range(int(re.search('^([0-9]+)', cellvalue).group(1)), int(re.search('(?:-)([0-9]+)', cellvalue).group(1)))
            if roll in foundrange:
                break
            elif roll > max(foundrange):
                minrow = foundrow+1
            else: #roll < min(foundrange)
                maxrow = foundrow-1
        else:
            foundrange = int(re.search('^([0-9]+)', cellvalue).group(1))
            if roll == foundrange:
                break
            elif roll > foundrange:
                minrow = foundrow+1
            else: #roll < foundrange
                maxrow = foundrow-1
        foundrow = minrow + int((maxrow-minrow)/2)
    return foundrow

def open_saved_sheet(type, authorid, title): #1 - table, 2 - char
    if type == 1:
        savedtables = gc.open_by_key(secrettable1).sheet1
    elif type == 2:
        savedtables = gc.open_by_key(secrettable2).sheet1
    foundrow = 0
    author = str(authorid)
    for i in range(1,savedtables.row_count+1): #down the first column
        if savedtables.cell(i, 1).value == author:#Column A is authors
            foundrow = i
            break
    if foundrow == 0: #Author has no tables (not in system)
        return None
    row = savedtables.row_values(foundrow)
    for i in range(1, len(row), 2): #across the row/counting columns
        if row[i] == title:
            return row[i+1]
    return None

def proper_find_id(url):

    foundid = re.match("(https://drive.google.com/open\?id=|https://docs.google.com/spreadsheets/d/)(\S+)(/\?|/edit\?usp=sharing)?", url, re.I).group(2)
    
    return foundid

def save_sheet(secretsheet, ctx): #secretsheet : 1 - tables, 2 - characters; ctx
    '''
    >savetable tablename linktotable : Saves the table to a private googlesheet, must be shared with sheeteditor@drystan.iam.gserviceaccount.com
    '''
    authorid = str(ctx.message.author.id)
    message = re.search("(>savetable |>savechar )(\S+)\s(\S+)", ctx.message.content, re.I) #excluding command
    name = message.group(2) #first word after command is name of table
    link = message.group(3) #second "word" after command is the link to the table
    saveditems = None
    item = None

    if re.match("https://drive.google.com/open\?id=\S+/?", link, re.I) or re.match("https://docs.google.com/spreadsheets/d/\S+/edit\?usp=sharing", link, re.I):
        key = proper_find_id(link)
        #search column A for author, otherwise add line and append
        if secretsheet == 1:
            saveditems = gc.open_by_key(secrettable1).sheet1
            item = "table"
        elif secretsheet == 2:
            saveditems = gc.open_by_key(secrettable2).sheet1
            item = "character"
        
        col_values = saveditems.col_values(1) #all values in column A
        for r in range(1, len(col_values)): #excluding first row (header)
            if col_values[r] == authorid:
                row_values = saveditems.row_values(r+1) #all values in row i
                for c in range(1, len(row_values), 2): #excluding author id and links
                    if row_values[c] == name:   #UPDATE PRESENT TABLE
                        saveditems.update_cell(r+1, c+2, key)
                        return "I've updated your " + item + " named **" + name + "** to point to the GSheet with an id of *" + key + "*."
                saveditems.add_cols(2) #ADD NEW COLUMNS AND ADD TABLE
                saveditems.update_cell(r+1, len(row_values)+1, name)
                saveditems.update_cell(r+1, len(row_values)+2, key)
                return "I've saved your " + item + " named **" + name + "** which has an id of *" + key + "*."
        #ADD AUTHOR AND TABLE IN NEW ROW
        saveditems.append_row([authorid, name, key])
        return "I've saved your " + item + " named **" + name + "** which has an id of *" + key + "*."

        return "I was unable to save your " + item + "."
    return "That isn't a valid link."

def list_saved_sheets(secretsheet, ctx):
    authorid = str(ctx.message.author.id)
    message = re.search("(>listtables|>listchars)( key)?", ctx.message.content, re.I) #excluding command

    saveditems = None
    item = None

    founditems = []


    #search column A for author, otherwise add line and append
    if secretsheet == 1:
        saveditems = gc.open_by_key(secrettable1).sheet1
        item = "table"
    elif secretsheet == 2:
        saveditems = gc.open_by_key(secrettable2).sheet1
        item = "character"
    
    col_values = saveditems.col_values(1) #all values in column A
    for r in range(1, len(col_values)): #excluding first row (header)
        if col_values[r] == authorid:
            row_values = saveditems.row_values(r+1) #all values in row i
            for c in range(1, len(row_values), 2): #excluding author id and links
                founditems.append("**" + row_values[c] + "**")
                # if showkeys:
                #     founditems[len(founditems)-1] += " at key *" + row_values[c+1] + "*"
    if len(founditems) == 0:
        return "I was unable to find any " + item + "s saved by you."
    else:
        return founditems

def get_value(sheet, item):
    '''
    Pass helpersheet get all values list of lists and name of item
    '''
    helpersheetdict = {
        #region General info
        'Name': [sheet[1][0], sheet[0][0]],
        'Deity': [sheet[1][1], sheet[0][1]],
        'Gender': [sheet[3][0], sheet[2][0]],
        'Alignment':   [sheet[3][1], sheet[2][1]],
        'Experience':   [sheet[5][0], sheet[4][0]],
        'Level':   [sheet[5][1], sheet[4][1]],
        #endregion
        #region Race & Class info
        'Race'          :   [sheet[1][2], sheet[0][2]],
        'Subrace'       :   [sheet[3][2], sheet[2][2]],
        'Class 1'       :   [sheet[1][3], sheet[0][3]],
        'Archetype 1'   :   [sheet[3][3], sheet[2][3]],
        'Level 1'       :   [sheet[5][3], sheet[4][3]],
        'Hit Die 1'     :   [sheet[7][3], sheet[6][3]],
        'Class 2'       :   [sheet[1][4], sheet[0][4]],
        'Archetype 2'   :   [sheet[3][4], sheet[2][4]],
        'Level 2'       :   [sheet[5][4], sheet[4][4]],
        'Hit Die 2'     :   [sheet[7][4], sheet[6][4]],
        'Class 3'       :   [sheet[1][5], sheet[0][5]],
        'Archetype 3'   :   [sheet[3][5], sheet[2][5]],
        'Level 3'       :   [sheet[5][5], sheet[4][5]],
        'Hit Die 3'     :   [sheet[7][5], sheet[6][5]],
        #endregion
        #region Abilities
        #region Strength
        'Strength Score'        :   [sheet[1][6], sheet[0][6]],
        'Strength Modifier'     :   [sheet[1][7], sheet[0][7]],
        'Strength Saving Prof'  :   [sheet[3][6], sheet[2][6]],
        'Strength Saving Bonus' :   [sheet[3][7], sheet[2][7]],
        'Athletics Prof'        :   [sheet[5][6], sheet[4][6]],
        'Athletics Bonus'       :   [sheet[5][7], sheet[4][7]],
        #endregion
        #region Dexterity
        'Dexterity Score'       :   [sheet[1][8], sheet[0][8]],
        'Dexterity Modifier'    :   [sheet[1][9], sheet[0][9]],
        'Dexterity Saving Prof' :   [sheet[3][8], sheet[2][8]],
        'Dexterity Saving Bonus':   [sheet[3][9], sheet[2][9]],
        'Acrobatics Prof'       :   [sheet[5][8], sheet[4][8]],
        'Acrobatics Bonus'      :   [sheet[5][9], sheet[4][9]],
        'Sleight of Hand Prof'  :   [sheet[7][8], sheet[6][8]],
        'Sleight of Hand Bonus' :   [sheet[7][9], sheet[6][9]],
        'Stealth Prof'          :   [sheet[9][8], sheet[8][8]],
        'Stealth Bonus'         :   [sheet[9][9], sheet[8][9]],
        #endregion
        #region Constitution
        'Constitution Score'       :   [sheet[1][10], sheet[0][10]],
        'Constitution Modifier'    :   [sheet[1][11], sheet[0][11]],
        'Constitution Saving Prof' :   [sheet[3][10], sheet[2][10]],
        'Constitution Saving Bonus':   [sheet[3][11], sheet[2][11]],
        #endregion
        #region Intelligence
        'Intelligence Score'       :   [sheet[1][12], sheet[0][12]],
        'Intelligence Modifier'    :   [sheet[1][13], sheet[0][13]],
        'Intelligence Saving Prof' :   [sheet[3][12], sheet[2][12]],
        'Intelligence Saving Bonus':   [sheet[3][13], sheet[2][13]],
        'Arcana Prof'              :   [sheet[5][12], sheet[4][12]],
        'Arcana Bonus'             :   [sheet[5][13], sheet[4][13]],
        'History Prof'             :   [sheet[7][12], sheet[6][12]],
        'History Bonus'            :   [sheet[7][13], sheet[6][13]],
        'Investigation Prof'       :   [sheet[9][12], sheet[8][12]],
        'Investigation Bonus'      :   [sheet[9][13], sheet[8][13]],
        'Nature Prof'              :   [sheet[11][12], sheet[10][12]],
        'Nature Bonus'             :   [sheet[11][13], sheet[10][13]],
        'Religion Prof'            :   [sheet[13][12], sheet[12][12]],
        'Religion Bonus'           :   [sheet[13][13], sheet[12][13]],
        #endregion
        #region Wisdom
        'Wisdom Score'         :   [sheet[1][14], sheet[0][14]],
        'Wisdom Modifier'      :   [sheet[1][15], sheet[0][15]],
        'Wisdom Saving Prof'   :   [sheet[3][14], sheet[2][14]],
        'Wisdom Saving Bonus'  :   [sheet[3][15], sheet[2][15]],
        'Animal Handling Prof' :   [sheet[5][14], sheet[4][14]],
        'Animal Handling Bonus':   [sheet[5][15], sheet[4][15]],
        'Insight Prof'         :   [sheet[7][14], sheet[6][14]],
        'Insight Bonus'        :   [sheet[7][15], sheet[6][15]],
        'Medicine Prof'        :   [sheet[9][14], sheet[8][14]],
        'Medicine Bonus'       :   [sheet[9][15], sheet[8][15]],
        'Perception Prof'      :   [sheet[11][14], sheet[10][14]],
        'Perception Bonus'     :   [sheet[11][15], sheet[10][15]],
        'Survival Prof'        :   [sheet[13][14], sheet[12][14]],
        'Survival Bonus'       :   [sheet[13][15], sheet[12][15]],
        #endregion
        #region Charisma
        'Charisma Score'         :   [sheet[1][16], sheet[0][16]],
        'Charisma Modifier'      :   [sheet[1][17], sheet[0][17]],
        'Charisma Saving Prof'   :   [sheet[3][16], sheet[2][16]],
        'Charisma Saving Bonus'  :   [sheet[3][17], sheet[2][17]],
        'Deception Prof' :   [sheet[5][16], sheet[4][16]],
        'Deception Bonus':   [sheet[5][17], sheet[4][17]],
        'Intimidation Prof'         :   [sheet[7][16], sheet[6][16]],
        'Intimidation Bonus'        :   [sheet[7][17], sheet[6][17]],
        'Performance Prof'        :   [sheet[9][16], sheet[8][16]],
        'Performance Bonus'       :   [sheet[9][17], sheet[8][17]],
        'Persuasion Prof'      :   [sheet[11][16], sheet[10][16]],
        'Persuasion Bonus'     :   [sheet[11][17], sheet[10][17]],
        #endregion
        #region Overall
        'Proficiency'       :   [sheet[5][2], sheet[4][2]],
        'Passive Perception':   [sheet[7][0], sheet[6][0]],
        'Passive Insight'   :   [sheet[7][1], sheet[6][1]],
        'Initiative'        :   [sheet[7][2], sheet[6][2]],
        'Jack of All Trades':   [sheet[9][5], sheet[8][5]],
        #endregion
        #endregion
        #region Battle Stats
        #region Speeds
        'Walking Speed'     :   [sheet[9][0], sheet[8][0]],
        'Swimming Speed'    :   [sheet[9][1], sheet[8][1]],
        'Flying Speed'      :   [sheet[9][2], sheet[8][2]],
        'Climbing Speed'    :   [sheet[9][3], sheet[8][3]],
        'Burrowing Speed'   :   [sheet[9][4], sheet[8][4]],
        #endregion
        #region Health, AC, Deathsaves
        'Current Health'            :   [sheet[11][0], sheet[10][0]],
        'Maximum Health'            :   [sheet[11][1], sheet[10][1]],
        'Temporary Health'          :   [sheet[11][2], sheet[10][2]],
        'Successful Death Saves'    :   [sheet[11][3], sheet[10][3]],
        'Failed Death Saves'        :   [sheet[11][4], sheet[10][4]],
        'Armor Class'               :   [sheet[13][4], sheet[12][4]],
        'Armor Class with Shield'   :   [sheet[13][5], sheet[12][5]],
        #endregion
        #region Hit Die
        'Remaining D6'  :   [sheet[13][0], sheet[12][0]],
        'Remaining D8'  :   [sheet[13][1], sheet[12][0]],
        'Remaining D10' :   [sheet[13][2], sheet[12][0]],
        'Remaining D12' :   [sheet[13][3], sheet[12][0]],
        'Maximum D6'    :   [sheet[15][0], sheet[14][0]],
        'Maximum D8'    :   [sheet[15][1], sheet[14][0]],
        'Maximum D10'   :   [sheet[15][2], sheet[14][0]],
        'Maximum D12'   :   [sheet[15][3], sheet[14][0]],
        #endregion
        #endregion
        #region Gear
        'Armor Name'        :   [sheet[15][6], sheet[14][6]],
        'Armor AC Bonus'    :   [sheet[15][7], sheet[14][7]],
        'Armor Weight'      :   [sheet[15][8], sheet[14][8]],
        'Shield Name'       :   [sheet[15][9], sheet[14][9]],
        'Shield AC Bonus'   :   [sheet[15][10], sheet[14][10]],
        'Shield Weight'     :   [sheet[15][11], sheet[14][11]],
        #endregion
    }

    result = helpersheetdict.get(item, ["Invalid input", "Invalid input"])
    if result[0] == "":
        result[0] = "None"
    if result[1] == "":
        result[1] = "None"
    return result

def correct_spacing(string, numspaces):
    if len(string) < numspaces:
        for i in range(numspaces - len(string)):
            string += " "
    elif len(string) > numspaces:
        string = string[:numspaces]
    return string

def block_builder(charsheet, blockname):

    result = []
    #  " + correct_spacing(get_value(charsheet, )[0], ) + "
    if blockname == "basic" or blockname == "complete":
        result.append("1```+-Basic Info--------------------------+\n"
                    + "| Gender:      " + correct_spacing(get_value(charsheet, "Gender")[0], 21) + "  |\n"
                    + "| Deity:       " + correct_spacing(get_value(charsheet, "Deity")[0], 21) + "  |\n"
                    + "| Alignment:   " + correct_spacing(get_value(charsheet, "Alignment")[0], 21) + "  |\n"
                    + "| Experience:  " + correct_spacing(get_value(charsheet, "Experience")[0], 11) + "  Lvl " + correct_spacing(get_value(charsheet, "Level")[0], 4) + "  |\n"
                    + "+-------------------------------------+```")
    if blockname == "battle" or blockname == "complete":
        shield = " "
        ac = get_value(charsheet, "Armor Class")[0]
        shieldac = get_value(charsheet, "Armor Class with Shield")[0]
        if ac.isdigit() and shieldac.isdigit() and int(ac) < int(shieldac):
            shield = "X"
        success = correct_spacing("".join(["X" for i in range(int(get_value(charsheet, "Successful Death Saves")[0]))]), 3)
        failure = correct_spacing("".join(["X" for i in range(int(get_value(charsheet, "Failed Death Saves")[0]))]), 3)
        result.append("4```+-Hit Points--------------------------+\n"
                    + "| Current:     " + correct_spacing(get_value(charsheet, "Current Health")[0], 4) + "    AC:       " + correct_spacing(ac, 2) + "   |\n"
                    + "| Temporary:   " + correct_spacing(get_value(charsheet, "Temporary Health")[0], 4) + "    Shield?:  [" + shield + "]  | \n"
                    + "| Maximum:     " + correct_spacing(get_value(charsheet, "Maximum Health")[0], 4) + "    Total AC: " + correct_spacing(shieldac, 2) + "   |\n"
                    + "+-Hit Dice----------------------------+\n"
                    + "|            D6    D8    D10    D12   |\n"
                    + "| Current:   " + correct_spacing(get_value(charsheet, "Remaining D6")[0], 3) + "   " + correct_spacing(get_value(charsheet, "Remaining D8")[0], 3) + "   " + correct_spacing(get_value(charsheet, "Remaining D10")[0], 3) + "    " + correct_spacing(get_value(charsheet, "Remaining D12")[0], 3) + "   |\n"
                    + "| Maximum:   " + correct_spacing(get_value(charsheet, "Maximum D6")[0], 3) + "   " + correct_spacing(get_value(charsheet, "Maximum D8")[0], 3) + "   " + correct_spacing(get_value(charsheet, "Maximum D10")[0], 3) + "    " + correct_spacing(get_value(charsheet, "Maximum D12")[0], 3) + "   |\n"
                    + "+-Death Saves-------------------------+\n"
                    + "| Successes               [" + success[0] + "] [" + success[1] + "] [" + success[2] + "] |\n"
                    + "| Failures                [" + failure[0] + "] [" + failure[1] + "] [" + failure[2] + "] |\n"
                    + "+-------------------------------------+```")
    if blockname == "build" or blockname == "complete":
        result.append("2```+-Race & Class------------------------+\n"
                    + "| Race:     " + correct_spacing(get_value(charsheet, "Race")[0], 24) + "  |\n"
                    + "| Subrace:  " + correct_spacing(get_value(charsheet, "Subrace")[0], 24) + "  |\n"
                    + "+ - - - - - - - - - - - - - - - - - - +\n"
                    + "| " + correct_spacing(get_value(charsheet, "Class 1")[0], 11) + " " + correct_spacing(get_value(charsheet, "Class 2")[0], 11) + " " + correct_spacing(get_value(charsheet, "Class 3")[0], 11) + " |\n"
                    + "| " + correct_spacing(get_value(charsheet, "Archetype 1")[0], 11) + " " + correct_spacing(get_value(charsheet, "Archetype 2")[0], 11) + " "  + correct_spacing(get_value(charsheet, "Archetype 3")[0], 11) + " |\n"
                    + "| Lvl " + correct_spacing(get_value(charsheet, "Level 1")[0], 7) + " Lvl " + correct_spacing(get_value(charsheet, "Level 2")[0], 7) + " Lvl " + correct_spacing(get_value(charsheet, "Level 3")[0], 7) + " |\n"
                    + "| " + correct_spacing(get_value(charsheet, "Hit Die 1")[0], 11) + " " + correct_spacing(get_value(charsheet, "Hit Die 2")[0], 11) +  " " + correct_spacing(get_value(charsheet, "Hit Die 3")[0], 11) + " |\n"
                    + "+-------------------------------------+```")
    #region ABILITIES
    if blockname == "strength" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Strength--------| " + correct_spacing(get_value(charsheet, "Strength Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value(charsheet, "Strength Modifier")[0]), 2) + " |--+\n"
                       + "| Saving Throw     [" + correct_spacing(get_value(charsheet, "Strength Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Strength Saving Bonus")[0]), 3) + "]   |\n"
                       + "| Athletics        [" + correct_spacing(get_value(charsheet, "Athletics Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Athletics Bonus")[0]), 3) + "]   |\n"
                       + "+-------------------------------------+```")
    if blockname == "dexterity" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Dexterity-------| " + correct_spacing(get_value(charsheet, "Dexterity Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value(charsheet, "Dexterity Modifier")[0]), 2) + " |--+\n"
                    + "| Saving Throw     [" + correct_spacing(get_value(charsheet, "Dexterity Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Dexterity Saving Bonus")[0]), 3) + "]   |\n"
                    + "| Acrobatics       [" + correct_spacing(get_value(charsheet, "Acrobatics Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Acrobatics Bonus")[0]), 3) + "]   |\n"
                    + "| Sleight of Hand  [" + correct_spacing(get_value(charsheet, "Sleight of Hand Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Sleight of Hand Bonus")[0]), 3) + "]   |\n"
                    + "| Acrobatics       [" + correct_spacing(get_value(charsheet, "Stealth Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Stealth Bonus")[0]), 3) + "]   |\n"
                    + "+-------------------------------------+```")
    if blockname == "constitution" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Constitution----| " + correct_spacing(get_value(charsheet, "Constitution Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value(charsheet, "Constitution Modifer")[0]), 2) + " |--+\n"
                    + "| Saving Throw     [" + correct_spacing(get_value(charsheet, "Constitution Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Constitution Saving Bonus")[0]), 3) + "]   |\n"
                    + "+-------------------------------------+```")
    if blockname == "intelligence" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Intelligence----| " + correct_spacing(get_value(charsheet, "Intelligence Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value(charsheet, "Intelligence Modifier")[0]), 2) + " |--+\n"
                    + "| Saving Throw     [" + correct_spacing(get_value(charsheet, "Intelligence Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Intelligence Saving Bonus")[0]), 3) + "]   |\n"
                    + "| Arcana           [" + correct_spacing(get_value(charsheet, "Arcana Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Arcana Bonus")[0]), 3) + "]   |\n"
                    + "| History          [" + correct_spacing(get_value(charsheet, "History Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "History Bonus")[0]), 3) + "]   |\n"
                    + "| Investigation    [" + correct_spacing(get_value(charsheet, "Investigation Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Investigation Bonus")[0]), 3) + "]   |\n"
                    + "| Nature           [" + correct_spacing(get_value(charsheet, "Nature Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Nature Bonus")[0]), 3) + "]   |\n"
                    + "| Reiligion        [" + correct_spacing(get_value(charsheet, "Religion Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Religion Bonus")[0]), 3) + "]   |\n"
                    + "+-------------------------------------+```")
    if blockname == "wisdom" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Wisdom----------| " + correct_spacing(get_value(charsheet, "Wisdom Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value(charsheet, "Wisdom Modifier")[0]), 2) + " |--+\n"
                    + "| Saving Throw     [" + correct_spacing(get_value(charsheet, "Wisdom Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Wisdom Saving Bonus")[0]), 3) + "]   |\n"
                    + "| Animal Handling  [" + correct_spacing(get_value(charsheet, "Animal Handling Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Animal Handling Bonus")[0]), 3) + "]   |\n"
                    + "| Insight          [" + correct_spacing(get_value(charsheet, "Insight Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Insight Bonus")[0]), 3) + "]   |\n"
                    + "| Medicine         [" + correct_spacing(get_value(charsheet, "Medicine Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Medicine Bonus")[0]), 3) + "]   |\n"
                    + "| Perception       [" + correct_spacing(get_value(charsheet, "Perception Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Perception Bonus")[0]), 3) + "]   |\n"
                    + "| Survival         [" + correct_spacing(get_value(charsheet, "Survival Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Survival Bonus")[0]), 3) + "]   |\n"
                    + "+-------------------------------------+```")
    if blockname == "charisma" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Charisma--------| " + correct_spacing(get_value(charsheet, "Charisma Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value(charsheet, "Charisma Modifier")[0]), 2) + " |--+\n"
                    + "| Saving Throw     [" + correct_spacing(get_value(charsheet, "Charisma Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Charisma Saving Bonus")[0]), 3) + "]   |\n"
                    + "| Deception        [" + correct_spacing(get_value(charsheet, "Deception Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Deception Bonus")[0]), 3) + "]   |\n"
                    + "| Intimidation     [" + correct_spacing(get_value(charsheet, "Intimidation Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Intimidation Bonus")[0]), 3) + "]   |\n"
                    + "| Performance      [" + correct_spacing(get_value(charsheet, "Performance Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Performance Bonus")[0]), 3) + "]   |\n"
                    + "| Persuasion       [" + correct_spacing(get_value(charsheet, "Persuasion Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value(charsheet, "Persuasion Bonus")[0]), 3) + "]   |\n"
                    + "+-------------------------------------+```")
    #endregion
    if blockname == "gear" or blockname == "complete":
        armorbonus = get_value(charsheet, "Armor AC Bonus")[0]
        armorbonus = bonus_formatter(armorbonus)
        shieldbonus = get_value(charsheet, "Shield AC Bonus")[0]
        shieldbonus = bonus_formatter(shieldbonus)
        result.append("5```+-Battle Gear-------------------------+\n"
                    + "| Armor:    " + correct_spacing(get_value(charsheet, "Armor Name")[0], 25) + " |\n"
                    + "| AC Bonus: " + correct_spacing(armorbonus,3) + "      Weight: " + correct_spacing(get_value(charsheet, "Armor Weight")[0], 2) + " lbs   |\n"
                    + "+ - - - - - - - - - - - - - - - - - - +\n"
                    + "| Shield:   " + correct_spacing(get_value(charsheet, "Shield Name")[0], 25) + " |\n"
                    + "| AC Bonus: " + correct_spacing(shieldbonus, 3) + "      Weight: " + correct_spacing(get_value(charsheet, "Shield Weight")[0], 2) + " lbs   |\n"
                    + "+-------------------------------------+```")
    return result

def bonus_formatter(rawnum):
    if rawnum.isdigit():
        if int(rawnum) > 0:
            rawnum = "+" + rawnum
        elif int(rawnum) < 0:
            rawnum = "-" + rawnum
    return rawnum


#endregion

bot.run(token)