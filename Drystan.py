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
secrettable3 = tempfile.readline().strip()
tempfile.close()
tempfile = open('bot-token.txt','r')
token = tempfile.readline()
tempfile.close()

helpersheetdict = {}

greenquestions = [
                "What is the name of your character?", "What does your character worship?", "What is your character's gender?", "What is your character's alignment?", "How much experience has your character earned?",
                "What is your character's race?", "What is your character's subrace?", "What is your first class?", "What is your first class's archetype?", "What is your first class's level?", "What is the hit die your first class uses?", "What is your second class?", "What is your second class's archetype?", "What is your second class's level?", "What is the hit die your second class uses?", "What is your third class?", "What is your third class's archetype?", "What is your third class's level?", "What is the hit die your third class uses?",
                "What is your character's strength score?", "What is your character's proficiency for their strength saving throw?", "What is your character's proficiency in ahtletics?",
                "What is your character's dexterity score?", "What is your character's proficiency in proficiency in their dexterity saving throw?", "What is your character's proficiency in acrobatics?", "What is your character's proficiency in sleight of hand?", "What is your character's proficiency in stealth?",
                "What is your character's constitution score?", "What is your character's proficiency in their constitution saving throw?",
                "What is your character's intelligence score?", "What is your character's proficiency in their intelligence saving throw?", "What is your character's proficiency in arcana?", "What is your character's proficiency in history?", "What is your character's proficiency in investigation?", "What is your character's proficiency in nature?", "What is your character's proficiency in religion?",
                "What is your character's wisdom score?", "What is your character's proficiency in their wisdom saving throw?", "What is your character's proficiency in animal handling?", "What is your character's proficiency in insight?", "What is your character's proficiency in medicine?", "What is your character's proficiency in perception?", "What is your character's proficiency in survival?",
                "What is your character's charisma score?", "What is your character's proficiency in their charisma saving throw?", "What is your character's proficiency in deception?", "What is your character's proficiency in intimidation?", "What is your character's proficiency in performance?", "What is your character's proficiency in persuasion?",
                "Is your character a Jack of All Trades?",
                "What is your character's walking speed?", "What is your character's swimming speed?", "What is your character's flying speed?", "What is your character's climbing speed?", "What is your character's burrowing speed?",
                "What is your character's current health?", "What is your character's maximum health?", "What is your character's temporary health?", "How many successful death saves has your character made?", "How many failed death saves has your character made?",
                "How many unused D6 does your character have?", "How many unused D8 does your character have?", "How many unused D10 does your character have?", "How many unused D12 does your character have?",
                "What armor is your character wearing?", "What bonus does the armor provide to your character's AC?", "How much does the armor weigh?", "What shield is your character holding?", "What bonus does the shield provide to your character's AC?", "How much does the shield weigh?"]
greenkeys = [
            'Name', 'Deity', 'Gender', 'Alignment', 'Experience',
            'Race', 'Subrace', 'Class 1', 'Archetype 1', 'Level 1', 'Hit Die 1', 'Class 2', 'Archetype 2', 'Level 2', 'Hit Die 2', 'Class 3', 'Archetype 3', 'Level 3', 'Hit Die 3',
            'Strength Score', 'Strength Saving Prof', 'Athletics Prof',
            'Dexterity Score', 'Dexterity Saving Prof', 'Acrobatics Prof', 'Sleight of Hand Prof', 'Stealth Prof',
            'Constitution Score', 'Constitution Saving Prof',
            'Intelligence Score', 'Intelligence Saving Prof', 'Arcana Prof', 'History Prof', 'Investigation Prof', 'Nature Prof', 'Religion Prof',
            'Wisdom Score', 'Wisdom Saving Prof', 'Animal Handling Prof', 'Insight Prof', 'Medicine Prof', 'Perception Prof', 'Survival Prof',
            'Charisma Score', 'Charisma Saving Prof', 'Deception Prof', 'Intimidation Prof', 'Performance Prof', 'Persuasion Prof',
            'Jack of All Trades',
            'Walking Speed', 'Swimming Speed', 'Flying Speed', 'Climbing Speed', 'Burrowing Speed',
            'Current Health', 'Maximum Health', 'Temporary Health', 'Successful Death Saves', 'Failed Death Saves',
            'Remaining D6', 'Remaining D8', 'Remaining D10', 'Remaining D12',
            'Armor Name', 'Armor AC Bonus', 'Armor Weight', 'Shield Name', 'Shield AC Bonus', 'Shield Weight']
cellvaluedict = {
        #region general info
        'name'      :   [2, 1],
        'deity'     :   [2, 2],
        'gender'    :   [4, 1],
        'alignment' :   [4, 2],
        'experience':   [6, 1],
        'level'     :   [6, 2],
        #endregion
        #region race & class info
        'race'          :   [2, 3],
        'subrace'       :   [4, 3],
        'class 1'       :   [2, 4],
        'archetype 1'   :   [4, 4],
        'level 1'       :   [6, 4],
        'hit die 1'     :   [8, 4],
        'class 2'       :   [2, 5],
        'archetype 2'   :   [4, 5],
        'level 2'       :   [6, 5],
        'hit die 2'     :   [8, 5],
        'class 3'       :   [2, 6],
        'archetype 3'   :   [4, 6],
        'level 3'       :   [6, 6],
        'hit die 3'     :   [8, 6],
        #endregion
        #region abilities
        #region strength
        'strength score'        :   [2, 7],
        'strength bonus'     :   [2, 8],
        'strength saving prof'  :   [4, 7],
        'strength saving bonus' :   [4, 8],
        'athletics prof'        :   [6, 7],
        'athletics bonus'       :   [6, 8],
        #endregion
        #region dexterity
        'dexterity score'       :   [2, 9],
        'dexterity bonus'    :   [2, 10],
        'dexterity saving prof' :   [4, 9],
        'dexterity saving bonus':   [4, 10],
        'acrobatics prof'       :   [6, 9],
        'acrobatics bonus'      :   [6, 10],
        'sleight of hand prof'  :   [8, 9],
        'sleight of hand bonus' :   [8, 10],
        'stealth prof'          :   [10, 9],
        'stealth bonus'         :   [10, 10],
        #endregion
        #region constitution
        'constitution score'       :   [2, 11],
        'constitution bonus'    :   [2, 12],
        'constitution saving prof' :   [4, 11],
        'constitution saving bonus':   [4, 12],
        #endregion
        #region intelligence
        'intelligence score'       :   [2, 13],
        'intelligence bonus'    :   [2, 14],
        'intelligence saving prof' :   [4, 13],
        'intelligence saving bonus':   [4, 14],
        'arcana prof'              :   [6, 13],
        'arcana bonus'             :   [6, 14],
        'history prof'             :   [8, 13],
        'history bonus'            :   [8, 14],
        'investigation prof'       :   [10, 13],
        'investigation bonus'      :   [10, 14],
        'nature prof'              :   [12, 13],
        'nature bonus'             :   [12, 14],
        'religion prof'            :   [14, 13],
        'religion bonus'           :   [14, 14],
        #endregion
        #region wisdom
        'wisdom score'         :   [2, 15],
        'wisdom bonus'      :   [2, 16],
        'wisdom saving prof'   :   [4, 15],
        'wisdom saving bonus'  :   [4, 16],
        'animal handling prof' :   [6, 15],
        'animal handling bonus':   [6, 16],
        'insight prof'         :   [8, 15],
        'insight bonus'        :   [8, 16],
        'medicine prof'        :   [10, 15],
        'medicine bonus'       :   [10, 16],
        'perception prof'      :   [12, 15],
        'perception bonus'     :   [12, 16],
        'survival prof'        :   [14, 15],
        'survival bonus'       :   [14, 16],
        #endregion
        #region charisma
        'charisma score'        :   [2, 17],
        'charisma bonus'     :   [2, 18],
        'charisma saving prof'  :   [4, 17],
        'charisma saving bonus' :   [4, 18],
        'deception prof'        :   [6, 17],
        'deception bonus'       :   [6, 18],
        'intimidation prof'     :   [8, 17],
        'intimidation bonus'    :   [8, 18],
        'performance prof'      :   [10, 17],
        'performance bonus'     :   [10, 18],
        'persuasion prof'       :   [12, 17],
        'persuasion bonus'      :   [12, 18],
        #endregion
        #region overall skip increment here
        'proficiency'       :   [6, 3],
        'passive perception':   [8, 1],
        'passive insight'   :   [8, 2],
        'initiative'        :   [8, 3],
        'jack of all trades':   [10, 6],
        #endregion
        #endregion
        #region battle stats increment from here
        #region speeds
        'walking speed'     :   [10, 1],
        'swimming speed'    :   [10, 2],
        'flying speed'      :   [10, 3],
        'climbing speed'    :   [10, 4],
        'burrowing speed'   :   [10, 5],
        #endregion
        #region health, ac, deathsaves
        'current health'            :   [12, 1],
        'maximum health'            :   [12, 2],
        'temporary health'          :   [12, 3],
        'successful death saves'    :   [12, 4],
        'failed death saves'        :   [12, 5],
        'armor class'               :   [14, 5],
        'armor class with shield'   :   [14, 6],
        #endregion
        #region hit die
        'remaining d6'  :   [14, 1],
        'remaining d8'  :   [14, 2],
        'remaining d10' :   [14, 3],
        'remaining d12' :   [14, 4],
        'maximum d6'    :   [16, 1],
        'maximum d8'    :   [16, 2],
        'maximum d10'   :   [16, 3],
        'maximum d12'   :   [16, 4],
        #endregion
        #endregion
        #region gear
        'armor name'        :   [16, 7],
        'armor ac bonus'    :   [16, 8],
        'armor weight'      :   [16, 9],
        'shield name'       :   [16, 10],
        'shield ac bonus'   :   [16, 11],
        'shield weight'     :   [16, 12],
        #endregion
    }

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
    try:
        result = save_sheet(1, ctx)
    except AttributeError:
        result = "You forgot either the name of the table or the link to the table"
    await ctx.send(result)

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
    Takes in a formatted roll (examples below) and returns a complex output (containing the rolls, what you did to it, any errors that occured, and the final total)
    The first thing after ">roll " must be either a Roll, or a number (if you want the bot to do simple math for you). After that, everything else can be in any order.
    Regex:                                          | Examples:
    Roll - #d#                                      | 1d20  or  50d30
    Operation - +#, -#, /#, *#, ^#                  | +5  or  - 100  or  /3  or  *8  or  ^4
    Vantage - avan, dvan                            | avan  or  dvan
    Explosion - !, !!, !#, !!#                      | !  or  !6  or  !!13   (no number defaults to on crit)
    Title -  &t "Title here"                        | &t "I'm attacking!"
    Description - &d "Description here"             | &d "Depiction of me stabbing his eye out: ~|-- O"
    To hit and damage roll - <#, <=#, =#, >=#, >#   | 1d20 <5 1d4+2  or  1d20+5 >=15 1d10+2
    Seperate multiple rolls - rollhere ; rollhere   | 1d20+10 ; 1d20+1 ; 1d10+8
    Simple ouput - &s                               | &s   (This is the same as typing ">r rollstuffhere")
    '''
    
    embeds = do_all_rolls(content, False)
    for each in embeds:
        if each[0] == True:
            await ctx.send(None, embed = each[1])
        else:
            await ctx.send(each[1])


@bot.command()
async def r(ctx, *, content:str):
    '''
    Takes in a formatted roll (examples below) and returns a simplified output (total only)
    Basic Input:                                     | Examples:
    Roll - #d#                                       | 1d20  or  50d30
    Operation - +#, -#, /#, *#, ^#                   | +5  or  - 100  or  /3  or  *8  or  ^4
    Vantage - avan, dvan                             | avan  or  dvan
    Explosion - !, !!, !#, !!3                       | !  or  !6  or  !!13 (no number defaults to on crit)
    To hit and damage roll - <#, <=#, =#, >=#, >#    | 1d20 <5 1d4+2  or  1d20+5 >=15 1d10+2
    Seperate multiple rolls - rollhere ; rollhere    | 1d20+10 ; 1d20+1 or 5 + 10 ; 1d10+8
    '''
    
    texts = do_all_rolls(content, True)
    for each in texts:
        await ctx.send(each[1])


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
    value = match.group(2).strip().lower()
    sheet = None

    if re.match("https://drive.google.com/open\?id=\S+/", inputsheet, re.I) or re.match("https://docs.google.com/spreadsheets/d/\S+/edit\?usp=sharing", inputsheet, re.I):
        sheet = gc.open_by_key(proper_find_id(inputsheet))
    else:
        key = open_saved_sheet(2, ctx.message.author.id, inputsheet)
        if key is None:
            await ctx.send("You haven't saved a character named " + inputsheet)
            return
        sheet = gc.open_by_key(key)
    helpersheet = sheet.worksheet("Helper Sheet")
    set_helperdict(helpersheet.get_all_values())
    
    if value[-5:] != 'bonus':
        value += " bonus"

    valueinfo = get_value(value) #value, formatted
    if valueinfo[0] == "Invalid Input":
        await ctx.send("That's not a valid bonus to use!")
        return
    operations = [bonus_formatter(valueinfo[0])]
    temp = run_roll(1, 20, None, None, operations) #rolls, formattedrolls, errorlist, total

    try:
        embed = discord.Embed(title = "**" + str(sheet.title) + "**", description = "*You rolled " + str(temp[1][0]) + " " + listToString(", ", operations) + " (" + str(valueinfo[1]) + " bonus) = " + str(temp[3]) + "*\u0020", color=0x89eaf8)
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
    Abilities - Displays all ability scores and bonuses, as well as skill proficiencies and bonuses (Can also type Strength, Dexterity, Constitution, Intelligence, Wisdom or Charisma to view just one ability's table)
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

    set_helperdict(helpersheet)

    try:
        embed = discord.Embed(title = "**" + get_value("Name")[0] + "**", description = "----------------------------------------------------------------------------------------", color=0x89eaf8)
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
    myauth = ctx.message.author
    mychannel = ctx.message.channel

    if re.match("https://drive.google.com/open\?id=\S+/", inputsheet, re.I) or re.match("https://docs.google.com/spreadsheets/d/\S+/edit\?usp=sharing", inputsheet, re.I):
        sheet = gc.open_by_key(proper_find_id(inputsheet))
    else:
        key = open_saved_sheet(2, ctx.message.author.id, inputsheet)
        if key is None:
            await ctx.send("You haven't saved a character named " + inputsheet)
            return
        sheet = gc.open_by_key(key)
    helpersheet = sheet.worksheet("Helper Sheet")

    set_helperdict(helpersheet.get_all_values())

    await ctx.send("What would you like to edit?")
    def check(m):
        return m.author == myauth and m.channel == mychannel
    mykey = (await bot.wait_for('message', check = check)).content
    myvalue = get_value(mykey)
    if myvalue[0] == 'Invalid Input':
        await ctx.send(mykey + " is not a valid part of the sheet")
        return
    await ctx.send("The current value is " + myvalue[0])

    await ctx.send("What would you like the new " + myvalue[1] + " to be?")
    newvalue = await bot.wait_for('message', check = check)

    result = change_value(helpersheet, mykey, newvalue)

    await ctx.send("Your character's " + myvalue[1] + " is now " + newvalue.content)


@bot.command(pass_context=True)
async def createchar(ctx):
    '''
    >createchar character - Input saved character key, or link to valid character sheet
    Creates a character from scratch - Asks for all inputtable values (green)
    '''
    inputsheet = ctx.message.content[11:].strip()
    sheet = None

    if re.match("https://drive.google.com/open\?id=\S+/", inputsheet, re.I) or re.match("https://docs.google.com/spreadsheets/d/\S+/edit\?usp=sharing", inputsheet, re.I):
        sheet = gc.open_by_key(proper_find_id(inputsheet))
    else:
        key = open_saved_sheet(2, ctx.message.author.id, inputsheet)
        if key is None:
            await ctx.send("You haven't saved a character named " + inputsheet)
            return
        sheet = gc.open_by_key(key)
    helpersheet = sheet.worksheet("Helper Sheet")
    myauth = ctx.message.author
    mychannel = ctx.message.channel
    await ctx.send("To skip answering, send a message containing only \"(S)\". To quit, send a message containing only \"(X)\". For questions about proficiency, answer with \"Exp\" for expertise, \"Prof\" for proficient, and \"(S)\" for none.")
    def check(m):
        return m.author == myauth and m.channel == mychannel
    for i in range(len(greenkeys)):
        await ctx.send(greenquestions[i])
        msg = await bot.wait_for('message', check = check)
        result = change_value(helpersheet, greenkeys[i], msg)
        if result == False:
            break


    await ctx.send("Your character has been created.")

#endregion
#region COMBAT TRACKER
@bot.command()
async def combat(ctx):

    finalembed = None
    channel = ctx.message.channel
    author = ctx.message.author

    fullcontent = ctx.message.content[7:].strip() #dont lower here cause might have things to repeat back
    firstarg = fullcontent[:fullcontent.find(" ")].lower() if fullcontent.find(" ") != -1 else fullcontent
    restargs = fullcontent[fullcontent.find(" "):] if fullcontent.find(" ") != -1 else None
    finalembed = [False, "Nothing was accomplished"]

    print(firstarg)
    print(restargs)

    #firstargs: start, end, add, remove, nextturn, lastturn, gototurn
    if firstarg == "start":
        print("start")
        finalembed = start_combat(channel, author, ctx.message.mentions[0] if len(ctx.message.mentions) == 1 else False)

    if firstarg == "end":
        print("end")
        finalembed = end_combat(channel, author)

    if firstarg == "powers":
        print("powers")
        finalembed = list_powers(channel, author)
    
    if firstarg == "add":
        print("add(players)")
        finalembed = await add_players(channel, author, ctx)

    if finalembed[0] == False:
        await ctx.send(finalembed[1]) 
        return
    else:
        await ctx.send(None, finalembed[1])
        return
#endregion


#region HELPER FUNCTIONS / NON COMMANDS
#region general
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

def bonus_formatter(rawnum):
    if rawnum.isdigit():
        if int(rawnum) >= 0:
            rawnum = "+" + rawnum
        elif int(rawnum) < 0:
            rawnum = "-" + rawnum
    return rawnum

def go_int(stringtoint, baseint):
    if stringtoint.isdigit():
        return int(stringtoint)
    else:
        return baseint

def correct_spacing(string, numspaces):
    if len(string) < numspaces:
        for i in range(numspaces - len(string)):
            string += " "
    elif len(string) > numspaces:
        string = string[:numspaces]
    return string

def is_outside_quotes(fullstring, charindex):
    numright = re.findall('"', fullstring[charindex:])
    if len(numright) % 2 == 0:
        return True
    else:
        return False

#endregion
#region roll/r helpers
def do_all_rolls(fullcontent, simple):
    myrolls = find_all_rolls(fullcontent)
    finishedrolls = []
    for each in myrolls:
        finishedrolls.extend(do_full_roll(each, simple))
    embeds = []
    for each in finishedrolls:
        embeds.append(create_roll_embed(each))
    return embeds

def do_full_roll(content, simple): #this one takes in between semicolon stuff, returns one or two embeds (depending on if there's dependent rolls)
    dependized = find_dependent_info(content) #indepcontent, depnum, deptype, depcontent
    if dependized[1] != None:
        allembeds = [do_one_roll(dependized[0], simple)]
        total = allembeds[0][8]
        if ">" in dependized[1] and total > dependized[2]:
            allembeds.append(do_one_roll(dependized[3], simple))
        if "=" in dependized[1] and total == dependized[2]:
            allembeds.append(do_one_roll(dependized[3], simple))
        if "<" in dependized[1] and total < dependized[2]:
            allembeds.append(do_one_roll(dependized[3], simple))
        return allembeds
    else:
        return [do_one_roll(content, simple)]
#                                                                                      0     1         2           3            4           5         6          7         8        9        10
def do_one_roll(content, simple): #this one takes in one in/dependized roll, returns title, desc, vantagename, explosion, formattedrolls, numdice, numsides, operations, total, errorlist, simple
    #region
    giventitle = ""
    givendesc = ""
    errorList = []
    numdice = 0
    numsides = 0
    operations = []
    vantage = 0 #0 - None; 1 - Advantage; 2 - Disadvantage
    explosion = ""

    if simple == False:
        temp = find_embed_info(content)
        content = temp[0]
        giventitle = temp[1]
        givendesc = temp[2]
        errorList.extend(temp[3])
        simple = temp[4]

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


    rolls = []                          #list of rolls for editing
    formattedrolls = []                 #list of formatted rolls to be displayed in the "Rolled" field
    total = 0                           #int displayed in the "Total"
    #endregion
    if impossible is True and re.search("^[0-9]+",content,re.I) is None:
        total = "Impossible"
    else:
        if numsides == 0 and numdice == 0:
            matchcase = re.search("^[0-9]+",content,re.I)
            if matchcase:
                rolls = [int(matchcase.group(0))]
                formattedrolls = [int(matchcase.group(0))]
            temp = run_operations(rolls, operations)
            errorList.extend(temp[0])
            total = temp[1]
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
    return [giventitle, givendesc, vantagename, explosion, formattedrolls, numdice, numsides, operations, total, errorList, simple]

def create_roll_embed(onerollcontentlist):
    if onerollcontentlist[10] == True:
        return [False, "You rolled " + listToString(",", onerollcontentlist[4]) + " and your total is " + str(onerollcontentlist[8])]
    else:
        try:
            embed = discord.Embed(title = "**" + onerollcontentlist[0] + "**", description = "*" + onerollcontentlist[1] + "*", color=0x89eaf8)
        except HTTPException:
            return [False, "Your title and description are too long!  Shorten one or both."]

        if embed:
            embed.add_field(name = "Vantage", value = onerollcontentlist[2], inline = True)
            embed.add_field(name = "Explosiveness", value = onerollcontentlist[3] if onerollcontentlist[3] else "None", inline = True)
            if len(listToString(", ", onerollcontentlist[4])) < 1024 - len("Rolled " + str(onerollcontentlist[5]) + "d" + str(onerollcontentlist[6])):
                embed.add_field(name = "Rolled " + str(onerollcontentlist[5]) + "d" + str(onerollcontentlist[6]), value = listToString(", ", onerollcontentlist[4]), inline = False)
            else:
                embed.add_field(name = "Rolled " + str(onerollcontentlist[5]) + "d" + str(onerollcontentlist[6]), value = "Exceeds displayable length", inline = False)
            embed.add_field(name = "Operators", value = listToString(", ",onerollcontentlist[7]) if onerollcontentlist[7] else "None", inline = False)
            embed.add_field(name = "Total", value = str(onerollcontentlist[8]), inline = False)
            embed.set_footer(text = "Errors: " + listToString("\n", onerollcontentlist[9]))
        return [True, embed]

#find dependent info - leftroll ># rightroll - if >= / <= / = # is achieved in left roll, right roll will be run
def find_embed_info(content):
    regextitle = r'\s(&t\s?")([^"]+)(")'
    regexdesc = r'\s(&d\s?")([^"]+)(")'
    
    giventitle = ""
    givendesc = ""
    errorList = []
    simple = False

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

    matchcase = re.search("&s", content, re.I)
    if matchcase:
        simple = True
        content = content[:matchcase.start()] + content[matchcase.end():]

    return [content, giventitle, givendesc, errorList, simple]

def find_all_rolls(content):
    rolls = []
    match = re.search(';', content)
    while match:
        if is_outside_quotes(content, match.start()):
            rolls.append(content[:match.start()])
            content = content[match.end():]
            match = re.search(';', content)
        else:
            match = re.search(';', content[match.end():])

    if len(content) > 0:
        rolls.append(content)

    return rolls

def find_dependent_info(content):
    dependenttype = None
    dependentnum = None
    dependentcontent = None
    
    matchcase = re.search('(?P<dependenttype><|<=|=|>=|>)\s?(?P<dependentnum>[0-9]+)', content, re.I)
    if matchcase: #A valid explosion was found - add to explosion to be used later
        dependenttype = (matchcase.group("dependenttype"))
        dependentnum = int((matchcase.group("dependentnum")))
        dependentcontent = content[matchcase.end():]
        content = content[:matchcase.start()]

    return [content, dependenttype, dependentnum, dependentcontent]

def find_roll_info(content):
    regexroll = r"^[0-9]+[dD][0-9]+"
    numsides = 0
    numdice = 0
    errorList = []
    impossible = False
    content = content.strip()
    matchcase = re.compile(regexroll, re.I).search(content)
    if(matchcase): #A valid roll was found - find d, slice on either side, set as num dice and num sides
        numdice = int(content[matchcase.start():matchcase.start()+matchcase.group(0).lower().find("d")])
        numsides = int(content[matchcase.start()+matchcase.group(0).lower().find("d")+1:matchcase.end()])
        content = content[:matchcase.start()] + content[matchcase.end():]

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
#endregion
#region sheet
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
    foundid = url
    try:
        foundid = re.match("(https://drive.google.com/open\?id=|https://docs.google.com/spreadsheets/d/)([^/]+)(/\?|/edit\?usp=sharing)?", url, re.I).group(2)
    except Exception:
        pass
    return foundid

def save_sheet(secretsheet, ctx): #secretsheet : 1 - tables, 2 - characters; ctx
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

def set_helperdict(sheet):

    global helpersheetdict

    helpersheetdict = {
        #region general info
        'name': [sheet[1][0], sheet[0][0]],
        'deity': [sheet[1][1], sheet[0][1]],
        'gender': [sheet[3][0], sheet[2][0]],
        'alignment':   [sheet[3][1], sheet[2][1]],
        'experience':   [sheet[5][0], sheet[4][0]],
        'level':   [sheet[5][1], sheet[4][1]],
        #endregion
        #region race & class info
        'race'          :   [sheet[1][2], sheet[0][2]],
        'subrace'       :   [sheet[3][2], sheet[2][2]],
        'class 1'       :   [sheet[1][3], sheet[0][3]],
        'archetype 1'   :   [sheet[3][3], sheet[2][3]],
        'level 1'       :   [sheet[5][3], sheet[4][3]],
        'hit die 1'     :   [sheet[7][3], sheet[6][3]],
        'class 2'       :   [sheet[1][4], sheet[0][4]],
        'archetype 2'   :   [sheet[3][4], sheet[2][4]],
        'level 2'       :   [sheet[5][4], sheet[4][4]],
        'hit die 2'     :   [sheet[7][4], sheet[6][4]],
        'class 3'       :   [sheet[1][5], sheet[0][5]],
        'archetype 3'   :   [sheet[3][5], sheet[2][5]],
        'level 3'       :   [sheet[5][5], sheet[4][5]],
        'hit die 3'     :   [sheet[7][5], sheet[6][5]],
        #endregion
        #region abilities
        #region strength
        'strength score'        :   [sheet[1][6], sheet[0][6]],
        'strength bonus'     :   [sheet[1][7], sheet[0][7]],
        'strength saving prof'  :   [sheet[3][6], sheet[2][6]],
        'strength saving bonus' :   [sheet[3][7], sheet[2][7]],
        'athletics prof'        :   [sheet[5][6], sheet[4][6]],
        'athletics bonus'       :   [sheet[5][7], sheet[4][7]],
        #endregion
        #region dexterity
        'dexterity score'       :   [sheet[1][8], sheet[0][8]],
        'dexterity bonus'    :   [sheet[1][9], sheet[0][9]],
        'dexterity saving prof' :   [sheet[3][8], sheet[2][8]],
        'dexterity saving bonus':   [sheet[3][9], sheet[2][9]],
        'acrobatics prof'       :   [sheet[5][8], sheet[4][8]],
        'acrobatics bonus'      :   [sheet[5][9], sheet[4][9]],
        'sleight of hand prof'  :   [sheet[7][8], sheet[6][8]],
        'sleight of hand bonus' :   [sheet[7][9], sheet[6][9]],
        'stealth prof'          :   [sheet[9][8], sheet[8][8]],
        'stealth bonus'         :   [sheet[9][9], sheet[8][9]],
        #endregion
        #region constitution
        'constitution score'       :   [sheet[1][10], sheet[0][10]],
        'constitution bonus'    :   [sheet[1][11], sheet[0][11]],
        'constitution saving prof' :   [sheet[3][10], sheet[2][10]],
        'constitution saving bonus':   [sheet[3][11], sheet[2][11]],
        #endregion
        #region intelligence
        'intelligence score'       :   [sheet[1][12], sheet[0][12]],
        'intelligence bonus'    :   [sheet[1][13], sheet[0][13]],
        'intelligence saving prof' :   [sheet[3][12], sheet[2][12]],
        'intelligence saving bonus':   [sheet[3][13], sheet[2][13]],
        'arcana prof'              :   [sheet[5][12], sheet[4][12]],
        'arcana bonus'             :   [sheet[5][13], sheet[4][13]],
        'history prof'             :   [sheet[7][12], sheet[6][12]],
        'history bonus'            :   [sheet[7][13], sheet[6][13]],
        'investigation prof'       :   [sheet[9][12], sheet[8][12]],
        'investigation bonus'      :   [sheet[9][13], sheet[8][13]],
        'nature prof'              :   [sheet[11][12], sheet[10][12]],
        'nature bonus'             :   [sheet[11][13], sheet[10][13]],
        'religion prof'            :   [sheet[13][12], sheet[12][12]],
        'religion bonus'           :   [sheet[13][13], sheet[12][13]],
        #endregion
        #region wisdom
        'wisdom score'         :   [sheet[1][14], sheet[0][14]],
        'wisdom bonus'      :   [sheet[1][15], sheet[0][15]],
        'wisdom saving prof'   :   [sheet[3][14], sheet[2][14]],
        'wisdom saving bonus'  :   [sheet[3][15], sheet[2][15]],
        'animal handling prof' :   [sheet[5][14], sheet[4][14]],
        'animal handling bonus':   [sheet[5][15], sheet[4][15]],
        'insight prof'         :   [sheet[7][14], sheet[6][14]],
        'insight bonus'        :   [sheet[7][15], sheet[6][15]],
        'medicine prof'        :   [sheet[9][14], sheet[8][14]],
        'medicine bonus'       :   [sheet[9][15], sheet[8][15]],
        'perception prof'      :   [sheet[11][14], sheet[10][14]],
        'perception bonus'     :   [sheet[11][15], sheet[10][15]],
        'survival prof'        :   [sheet[13][14], sheet[12][14]],
        'survival bonus'       :   [sheet[13][15], sheet[12][15]],
        #endregion
        #region charisma
        'charisma score'         :   [sheet[1][16], sheet[0][16]],
        'charisma bonus'      :   [sheet[1][17], sheet[0][17]],
        'charisma saving prof'   :   [sheet[3][16], sheet[2][16]],
        'charisma saving bonus'  :   [sheet[3][17], sheet[2][17]],
        'deception prof' :   [sheet[5][16], sheet[4][16]],
        'deception bonus':   [sheet[5][17], sheet[4][17]],
        'intimidation prof'         :   [sheet[7][16], sheet[6][16]],
        'intimidation bonus'        :   [sheet[7][17], sheet[6][17]],
        'performance prof'        :   [sheet[9][16], sheet[8][16]],
        'performance bonus'       :   [sheet[9][17], sheet[8][17]],
        'persuasion prof'      :   [sheet[11][16], sheet[10][16]],
        'persuasion bonus'     :   [sheet[11][17], sheet[10][17]],
        #endregion
        #region overall
        'proficiency'       :   [sheet[5][2], sheet[4][2]],
        'passive perception':   [sheet[7][0], sheet[6][0]],
        'passive insight'   :   [sheet[7][1], sheet[6][1]],
        'initiative'        :   [sheet[7][2], sheet[6][2]],
        'jack of all trades':   [sheet[9][5], sheet[8][5]],
        #endregion
        #endregion
        #region battle stats
        #region speeds
        'walking speed'     :   [sheet[9][0], sheet[8][0]],
        'swimming speed'    :   [sheet[9][1], sheet[8][1]],
        'flying speed'      :   [sheet[9][2], sheet[8][2]],
        'climbing speed'    :   [sheet[9][3], sheet[8][3]],
        'burrowing speed'   :   [sheet[9][4], sheet[8][4]],
        #endregion
        #region health, ac, deathsaves
        'current health'            :   [sheet[11][0], sheet[10][0]],
        'maximum health'            :   [sheet[11][1], sheet[10][1]],
        'temporary health'          :   [sheet[11][2], sheet[10][2]],
        'successful death saves'    :   [sheet[11][3], sheet[10][3]],
        'failed death saves'        :   [sheet[11][4], sheet[10][4]],
        'armor class'               :   [sheet[13][4], sheet[12][4]],
        'armor class with shield'   :   [sheet[13][5], sheet[12][5]],
        #endregion
        #region hit die
        'remaining d6'  :   [sheet[13][0], sheet[12][0]],
        'remaining d8'  :   [sheet[13][1], sheet[12][1]],
        'remaining d10' :   [sheet[13][2], sheet[12][2]],
        'remaining d12' :   [sheet[13][3], sheet[12][3]],
        'maximum d6'    :   [sheet[15][0], sheet[14][0]],
        'maximum d8'    :   [sheet[15][1], sheet[14][1]],
        'maximum d10'   :   [sheet[15][2], sheet[14][2]],
        'maximum d12'   :   [sheet[15][3], sheet[14][3]],
        #endregion
        #endregion
        #region gear
        'armor name'        :   [sheet[15][6], sheet[14][6]],
        'armor ac bonus'    :   [sheet[15][7], sheet[14][7]],
        'armor weight'      :   [sheet[15][8], sheet[14][8]],
        'shield name'       :   [sheet[15][9], sheet[14][9]],
        'shield ac bonus'   :   [sheet[15][10], sheet[14][10]],
        'shield weight'     :   [sheet[15][11], sheet[14][11]],
        #endregion
    }

def get_value(item):
    '''
    Pass helpersheet get all values list of lists and name of item
    '''

    result = helpersheetdict.get(item.lower(), ["Invalid Input", "Invalid Input"])
    if result[0] == "":
        result[0] = "None"
    if result[1] == "":
        result[1] = "None"
    return result

def change_value(helpersheet, key, msg):
    msg = msg.content
    if msg == '(S)': #skip
        return True
    elif msg == '(X)': #Exit
        return False
    else:
        rowcol = cellvaluedict.get(key.lower())
        helpersheet.update_cell(rowcol[0], rowcol[1], msg)
        return True
#endregion
#region combat
def start_combat(channel, cm, acm):
    savedcombats = gc.open_by_key(secrettable3).sheet1

    col_values = savedcombats.col_values(1) #all values in column A
    for r in range(1, len(col_values)): #excluding first row (header)
        if col_values[r] == str(channel.id): #CHANNEL HAS COMBAT ACTIVE ALREADY, MAKE NOTE SAYING NUH UH
            return [False, "You already have a combat active in this channel."]
    #CREATE NEW COMBAT FOR REALSIES
    savedcombats.append_row([str(channel.id), str(cm.id), str(acm.id) if acm is not False else None])
    return [False, "You are now Combat Master" + "".join([" and " + acm.mention + " is the Assistant CM"  if acm is not False else ""]) + "! Type `>combat powers` to see your powers."]

def end_combat(channel, author):
    savedcombats = gc.open_by_key(secrettable3).sheet1
    cm = is_author_cm(channel, author)
    if cm == 1:
        col_values = savedcombats.col_values(1) #all values in column A
        for r in range(1, len(col_values)): #excluding first row (header)
            if col_values[r] == str(channel.id): #CHANNEL HAS COMBAT ACTIVE
                savedcombats.delete_row(r+1)
                return [False, "I have ended combat in your channel!"]
        #CNO ACTIVE COMBAT
    elif cm == 0:
        return [False, "There is no combat active in this channel"]
    elif cm == -1 or cm == .5:
        return [False, "You are not the Combat Master, and therefore do not have access to this command."]

def list_powers(channel, author):
    cm = is_author_cm(channel, author)
    if cm == 1: #is cm to active combat
        return [False, '''```You are the Combat Master, and these are commands you may run:
        >combat end                   |   This ends the combat in the channel.
        >combat add @user(s)          |   This prompts the mentioned user(s) to provide the name of a saved character, or the edit link to a valid character sheet.
        >combat addnpc key (#)        |   This intakes a valid npc sheet or the saved key to an npc sheet, and adds (#) copy of the npc to the combat.
        >combat remove charname       |   This removes the character in combat with the given name.
        ```''']
    elif cm == .5:
        return [False, '''```You are the Assistant Combat Master, and these are the commands you may run:
        >combat nextinit
        >combat preinit
        >combat gotoinit        
        >combat map
        ```''']
    elif cm == 0: #no active combat
        return [False, '''```There are three positions a user may hold: Combat Master, Assistant CM, and Player.
        The Combat Master has full access to all commands.
        The Assistant Combat Master has access to all commands, except end, add, and remove.
        The Player has partial and limited command access - a limit of one attack and one AoO per round, unless CM/ACM provides extra.
        ```''']
    elif cm == -1:
        return [False, '''```You are a Player, and these are the commands you may run:
        >combat attack charname attack   |   You may run this command once on your turn, unless the CM/ACM provides an extra run. The charname must be you or another character in the combat, and the attack must be the key for an attack you have saved, or an attack you just created.
        ```''']

async def add_players(channel, author, ctx):
    cm = is_author_cm(channel, author)
    if cm == 1:
        users = [each.display_name for each in ctx.message.mentions]
        charkeys = []
        characters = []
        
        for each in ctx.message.mentions:
            await ctx.send(each.mention + " What character would you like to add? (Saved character key)")
            def check(m):
                return m.author == each and m.channel == channel
            charkey = proper_find_id((await bot.wait_for('message', check = check)).content)
            try:
                set_helperdict(gc.open_by_key(open_saved_sheet(2, each.id, charkey)).worksheet("Helper Sheet").get_all_values())
                characters.append(get_value("Name")[0])
                charkeys.append(charkey)
            except gspread.exceptions.APIError:
                characters.append(None)
                charkeys.append(None)

        playerdict = dict(zip(users, characters))
        return [False, "All mentioned users have added characters or declined to join combat.\n" + "\n".join(["*" + user + "* joined with __" + str(playerdict[user]) + "__" if playerdict[user] != None else "*" + user + "* didn't join combat." for user in playerdict ])]
    elif cm == .5 or cm == -1:
        return [False, "You are not the Combat Master, and therefore do not have access to this command."]

def add_npcs(channel, author, key):
    pass


def is_author_cm(channel, author): #1 = cm, 0 = no combat, -1 = not cm
    savedcombats = gc.open_by_key(secrettable3).sheet1
    col_values = savedcombats.col_values(1) #all values in column A
    for r in range(1, len(col_values)): #excluding first row (header)
        if col_values[r] == str(channel.id): #active combat
            if savedcombats.cell(r+1, 2).value == str(author.id): #author is cm
                return 1
            if savedcombats.cell(r+1, 3).value == str(author.id):
                return .5
            return -1
    return 0
#endregion
#region other
def block_builder(charsheet, blockname):

    result = []
    #  " + correct_spacing(get_value()[0], ) + "
    set_helperdict(charsheet)
    if blockname == "basic" or blockname == "complete":
        result.append("1```+-Basic Info--------------------------+\n"
                    + "| Gender:      " + correct_spacing(get_value("Gender")[0], 21) + "  |\n"
                    + "| Deity:       " + correct_spacing(get_value("Deity")[0], 21) + "  |\n"
                    + "| Alignment:   " + correct_spacing(get_value("Alignment")[0], 21) + "  |\n"
                    + "| Experience:  " + correct_spacing(get_value("Experience")[0], 11) + "  Lvl " + correct_spacing(get_value("Level")[0], 4) + "  |\n"
                    + "+-------------------------------------+```")
    if blockname == "battle" or blockname == "complete":
        shield = " "
        ac = get_value("Armor Class")[0]
        shieldac = get_value("Armor Class with Shield")[0]
        if ac.isdigit() and shieldac.isdigit() and int(ac) < int(shieldac):
            shield = "X"
        success = correct_spacing("".join(["X" for i in range(go_int(get_value("Successful Death Saves")[0], 0))]), 3)
        failure = correct_spacing("".join(["X" for i in range(go_int(get_value("Failed Death Saves")[0], 0))]), 3)
        result.append("4```+-Hit Points--------------------------+\n"
                    + "| Current:     " + correct_spacing(get_value("Current Health")[0], 4) + "    AC:       " + correct_spacing(ac, 2) + "   |\n"
                    + "| Temporary:   " + correct_spacing(get_value("Temporary Health")[0], 4) + "    Shield?:  [" + shield + "]  | \n"
                    + "| Maximum:     " + correct_spacing(get_value("Maximum Health")[0], 4) + "    Total AC: " + correct_spacing(shieldac, 2) + "   |\n"
                    + "+-Hit Dice----------------------------+\n"
                    + "|            D6    D8    D10    D12   |\n"
                    + "| Current:   " + correct_spacing(get_value("Remaining D6")[0], 3) + "   " + correct_spacing(get_value("Remaining D8")[0], 3) + "   " + correct_spacing(get_value("Remaining D10")[0], 3) + "    " + correct_spacing(get_value("Remaining D12")[0], 3) + "   |\n"
                    + "| Maximum:   " + correct_spacing(get_value("Maximum D6")[0], 3) + "   " + correct_spacing(get_value("Maximum D8")[0], 3) + "   " + correct_spacing(get_value("Maximum D10")[0], 3) + "    " + correct_spacing(get_value("Maximum D12")[0], 3) + "   |\n"
                    + "+-Death Saves-------------------------+\n"
                    + "| Successes               [" + success[0] + "] [" + success[1] + "] [" + success[2] + "] |\n"
                    + "| Failures                [" + failure[0] + "] [" + failure[1] + "] [" + failure[2] + "] |\n"
                    + "+-------------------------------------+```")
    if blockname == "build" or blockname == "complete":
        result.append("2```+-Race & Class------------------------+\n"
                    + "| Race:     " + correct_spacing(get_value("Race")[0], 24) + "  |\n"
                    + "| Subrace:  " + correct_spacing(get_value("Subrace")[0], 24) + "  |\n"
                    + "+ - - - - - - - - - - - - - - - - - - +\n"
                    + "| " + correct_spacing(get_value("Class 1")[0], 11) + " " + correct_spacing(get_value("Class 2")[0], 11) + " " + correct_spacing(get_value("Class 3")[0], 11) + " |\n"
                    + "| " + correct_spacing(get_value("Archetype 1")[0], 11) + " " + correct_spacing(get_value("Archetype 2")[0], 11) + " "  + correct_spacing(get_value("Archetype 3")[0], 11) + " |\n"
                    + "| Lvl " + correct_spacing(get_value("Level 1")[0], 7) + " Lvl " + correct_spacing(get_value("Level 2")[0], 7) + " Lvl " + correct_spacing(get_value("Level 3")[0], 7) + " |\n"
                    + "| " + correct_spacing(get_value("Hit Die 1")[0], 11) + " " + correct_spacing(get_value("Hit Die 2")[0], 11) +  " " + correct_spacing(get_value("Hit Die 3")[0], 11) + " |\n"
                    + "+-------------------------------------+```")
    #region ABILITIES
    if blockname == "strength" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Strength--------| " + correct_spacing(get_value("Strength Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value("Strength bonus")[0]), 2) + " |--+\n"
                       + "| Saving Throw     [" + correct_spacing(get_value("Strength Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Strength Saving Bonus")[0]), 3) + "]   |\n"
                       + "| Athletics        [" + correct_spacing(get_value("Athletics Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Athletics Bonus")[0]), 3) + "]   |\n"
                       + "+-------------------------------------+```")
    if blockname == "dexterity" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Dexterity-------| " + correct_spacing(get_value("Dexterity Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value("Dexterity bonus")[0]), 2) + " |--+\n"
                    + "| Saving Throw     [" + correct_spacing(get_value("Dexterity Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Dexterity Saving Bonus")[0]), 3) + "]   |\n"
                    + "| Acrobatics       [" + correct_spacing(get_value("Acrobatics Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Acrobatics Bonus")[0]), 3) + "]   |\n"
                    + "| Sleight of Hand  [" + correct_spacing(get_value("Sleight of Hand Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Sleight of Hand Bonus")[0]), 3) + "]   |\n"
                    + "| Acrobatics       [" + correct_spacing(get_value("Stealth Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Stealth Bonus")[0]), 3) + "]   |\n"
                    + "+-------------------------------------+```")
    if blockname == "constitution" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Constitution----| " + correct_spacing(get_value("Constitution Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value("Constitution Modifer")[0]), 2) + " |--+\n"
                    + "| Saving Throw     [" + correct_spacing(get_value("Constitution Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Constitution Saving Bonus")[0]), 3) + "]   |\n"
                    + "+-------------------------------------+```")
    if blockname == "intelligence" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Intelligence----| " + correct_spacing(get_value("Intelligence Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value("Intelligence bonus")[0]), 2) + " |--+\n"
                    + "| Saving Throw     [" + correct_spacing(get_value("Intelligence Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Intelligence Saving Bonus")[0]), 3) + "]   |\n"
                    + "| Arcana           [" + correct_spacing(get_value("Arcana Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Arcana Bonus")[0]), 3) + "]   |\n"
                    + "| History          [" + correct_spacing(get_value("History Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("History Bonus")[0]), 3) + "]   |\n"
                    + "| Investigation    [" + correct_spacing(get_value("Investigation Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Investigation Bonus")[0]), 3) + "]   |\n"
                    + "| Nature           [" + correct_spacing(get_value("Nature Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Nature Bonus")[0]), 3) + "]   |\n"
                    + "| Reiligion        [" + correct_spacing(get_value("Religion Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Religion Bonus")[0]), 3) + "]   |\n"
                    + "+-------------------------------------+```")
    if blockname == "wisdom" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Wisdom----------| " + correct_spacing(get_value("Wisdom Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value("Wisdom bonus")[0]), 2) + " |--+\n"
                    + "| Saving Throw     [" + correct_spacing(get_value("Wisdom Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Wisdom Saving Bonus")[0]), 3) + "]   |\n"
                    + "| Animal Handling  [" + correct_spacing(get_value("Animal Handling Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Animal Handling Bonus")[0]), 3) + "]   |\n"
                    + "| Insight          [" + correct_spacing(get_value("Insight Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Insight Bonus")[0]), 3) + "]   |\n"
                    + "| Medicine         [" + correct_spacing(get_value("Medicine Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Medicine Bonus")[0]), 3) + "]   |\n"
                    + "| Perception       [" + correct_spacing(get_value("Perception Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Perception Bonus")[0]), 3) + "]   |\n"
                    + "| Survival         [" + correct_spacing(get_value("Survival Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Survival Bonus")[0]), 3) + "]   |\n"
                    + "+-------------------------------------+```")
    if blockname == "charisma" or blockname == "abilities" or blockname == "complete":
        result.append("3```+-Charisma--------| " + correct_spacing(get_value("Charisma Score")[0], 2) + " |------| " + correct_spacing(bonus_formatter(get_value("Charisma bonus")[0]), 2) + " |--+\n"
                    + "| Saving Throw     [" + correct_spacing(get_value("Charisma Saving Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Charisma Saving Bonus")[0]), 3) + "]   |\n"
                    + "| Deception        [" + correct_spacing(get_value("Deception Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Deception Bonus")[0]), 3) + "]   |\n"
                    + "| Intimidation     [" + correct_spacing(get_value("Intimidation Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Intimidation Bonus")[0]), 3) + "]   |\n"
                    + "| Performance      [" + correct_spacing(get_value("Performance Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Performance Bonus")[0]), 3) + "]   |\n"
                    + "| Persuasion       [" + correct_spacing(get_value("Persuasion Prof")[0], 3) + "]      [" + correct_spacing(bonus_formatter(get_value("Persuasion Bonus")[0]), 3) + "]   |\n"
                    + "+-------------------------------------+```")
    #endregion
    if blockname == "gear" or blockname == "complete":
        armorbonus = get_value("Armor AC Bonus")[0]
        armorbonus = bonus_formatter(armorbonus)
        shieldbonus = get_value("Shield AC Bonus")[0]
        shieldbonus = bonus_formatter(shieldbonus)
        result.append("5```+-Battle Gear-------------------------+\n"
                    + "| Armor:    " + correct_spacing(get_value("Armor Name")[0], 25) + " |\n"
                    + "| AC Bonus: " + correct_spacing(armorbonus,3) + "      Weight: " + correct_spacing(get_value("Armor Weight")[0], 2) + " lbs   |\n"
                    + "+ - - - - - - - - - - - - - - - - - - +\n"
                    + "| Shield:   " + correct_spacing(get_value("Shield Name")[0], 25) + " |\n"
                    + "| AC Bonus: " + correct_spacing(shieldbonus, 3) + "      Weight: " + correct_spacing(get_value("Shield Weight")[0], 2) + " lbs   |\n"
                    + "+-------------------------------------+```")
    return result


#endregion
#endregion
bot.run(token)