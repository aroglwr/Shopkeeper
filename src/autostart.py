from API.general import *
import json
from os import system

doKeys = input("would you like to refresh keys? Y/N\n")

if doKeys.lower() == "y":
    try:
        print("opening config.json")
        getConfig = getJSON_local_old("src\config.json")
        getConfig["token"] = (botToken := input("Input bot token (leave blank to not change)\n")) or getConfig.get("token", "")
        getConfig["steam_token"] = (botToken := input("Input Steam API token (leave blank to not change)\n")) or getConfig.get("steam_token", "")
        getConfig["riot_token"] = (botToken := input("Input Riot API token (leave blank to not change)\n")) or getConfig.get("riot_token", "")
        getConfig["nasa_token"] = (botToken := input("Input NASA API token (leave blank to not change)\n")) or getConfig.get("nasa_token", "")
        getConfig["mal_client"] = (botToken := input("Input MyAnimeList Client ID (leave blank to not change)\n")) or getConfig.get("mal_client", "")
    except:
        print("no config file found\ncreating config.json...")
        getConfig = getJSON_local_old("src\config.json.example")
        getConfig["token"] = (botToken := input("Input bot token (leave blank to not add)\n")) or getConfig.get("token", "")
        getConfig["steam_token"] = (botToken := input("Input Steam API token (leave blank to not add)\n")) or getConfig.get("steam_token", "")
        getConfig["riot_token"] = (botToken := input("Input Riot API token (leave blank to not add)\n")) or getConfig.get("riot_token", "")
        getConfig["nasa_token"] = (botToken := input("Input NASA API token (leave blank to not add)\n")) or getConfig.get("nasa_token", "")
        getConfig["mal_client"] = (botToken := input("Input MyAnimeList Client ID (leave blank to not add)\n")) or getConfig.get("mal_client", "")

    with open("src\\testcfg.json", "w", encoding="utf-8") as f:
        json.dump(getConfig, f, ensure_ascii=False, indent=4)

else:
    print("NO")

try:
    getData = getJSON_local_old("src/datatest.json")
    if getData["games"][0] == "GAME_LIST_HERE" or getData["watching"][0] == "WATCHING_LIST_HERE"  or getData["gifs"][0] == "GIF_LIST_HERE" or getData["crunch"][0] == "GIF_LIST_HERE" or getData["faq"].get("QUESTION"):
        print("DEFAULT VALUE DETECTED IN src/data.json\nPLEASE POPULATE")
except:
    print("MISSING src/data.json\nGENERATING DEFAULT - PLEASE POPULATE")
    getData = {
        "games": [
            "GAME_LIST_HERE"
            ],
        "watching": [
            "WATCHING_LIST_HERE"
            ],
        "gifs": [
            "GIF_LIST_HERE"
            ],
        "crunch": [
            "GIF_LIST_HERE"
            ],
        "faq":{
            "QUESTION":"ANSWER"
            },
        "riot":{
            "leagueSummonerSpells":{
                "1":"<:cleanse:1146196429312905287>",
                "4":"<:flash:1146196463089614978>",
                "21":"<:barrier:1146196423369560214>",
                "14":"<:ignite:1146196421406638150>",
                "3":"<:exhaust:1146196462020075550>",
                "6":"<:ghost:1146196413965947051>",
                "7":"<:heal:1146196415152918658>",
                "13":"<:clarity:1146196419938627637>",
                "11":"<:smite:1146196417111666758>",
                "32":"<:mark:1146196425475117197>",
                "12":"<:teleport:1146196418328006797>"
            },
            "leagueRunes":{
                "8437":"<:graspoftheundying:1147242038245466113>",
                "8439":"<:aftershock:1147242028527268002>",
                "8465":"<:guardian:1147242041420550214>",
                "8446":"<:demolish:1147242033677881436>",
                "8463":"<:fontoflife:1147242036559360130>",
                "8401":"<:shieldbash:1147242042909532271>",
                "8429":"<:conditioning:1147242032658661437>",
                "8444":"<:secondwind:1147242048710266968>",
                "8473":"<:boneplating:1147242031270346905>",
                "8451":"<:overgrowth:1147242045782642819>",
                "8453":"<:revitalize:1147242047036735518>",
                "8242":"<:unflinching:1147242050236977222>",

                "8005":"<:presstheattack:1147244864396857435>",
                "8008":"<:lethaltempo:1147244858629705920>",
                "8021":"<:fleetfootwork:1147244849263824916>",
                "8010":"<:conqueror:1147244842020253836>",
                "9101":"<:overheal:1147244860189982780> ",
                "9111":"<:triumph:1147244866556936333> ",
                "8009":"<:presenceofmind:1147244862412963860>",
                "9104":"<:legendalacrity:1147244853307129928>",
                "9105":"<:legendtenacity:1147244856205398026>",
                "9103":"<:legendbloodline:1147244854804496534>",
                "8014":"<:coupdegrace:1147244844557799424>",
                "8017":"<:cutdown:1147244846617202739>",
                "8299":"<:laststand:1147244850689871903>",

                "8214":"<:summonaery:1147246600415088790>",
                "8229":"<:arcanecomet:1147246581704302642>",
                "8230":"<:phaserush:1147246595360968738>",
                "8224":"<:nullifyingorb:1147246592148127885>",
                "8226":"<:manaflowband:1147246587807023265>",
                "8275":"<:nimbuscloak:1147246589778346044>",
                "8210":"<:transcendence:1147246602654842921>",
                "8234":"<:celerity:1147246583914709086>",
                "8233":"<:absolutefocus:1147246580261470228>",
                "8237":"<:scorch:1147246598049497158>",
                "8232":"<:waterwalking:1147246604101881857> ",
                "8236":"<:gatheringstorm:1147246586745847959>",

                "8351":"<:glacialaugment:1147246548212797500>",
                "8360":"<:unsealedspellbook:1147246559784869980>",
                "8369":"<:firststrike:1147246543724879943>",
                "8306":"<:hextechflashtraption:1147246550075056149>",
                "8304":"<:magicalfootwear:1147246551744381009>",
                "8313":"<:perfecttiming:1147246555502485594>",
                "8321":"<:futuresmarket:1147246546199511081>",
                "8316":"<:miniondematerializer:1147246552943951944>",
                "8345":"<:biscuitdelivery:1147246540042285126>",
                "8347":"<:cosmicinsight:1147246541430599691>",
                "8410":"<:approachvelocity:1147246537903181954>",
                "8352":"<:timewarptonic:1147246556555264163>",

                "8112":"<:electrocute:1147246320168476772>",
                "8124":"<:predator:1147246330331275346> ",
                "8128":"<:darkharvest:1147246317312151752>",
                "9923":"<:hailofblades:1147246326111801404>",
                "8126":"<:cheapshot:1147246343790788658>",
                "8139":"<:tasteofblood:1147246335326687243>",
                "8143":"<:suddenimpact:1147246334068412416>",
                "8136":"<:zombieward:1147246371062157363>",
                "8120":"<:ghostporo:1147246323876249780>",
                "8138":"<:eyeballcollection:1147246321615519784>",
                "8135":"<:treasurehunter:1147246338153644133>",
                "8134":"<:ingenioushunter:1147246328582254633>",
                "8105":"<:relentlesshunter:1147246331832840333>",
                "8106":"<:ultimatehunter:1147246339126738966>"
            }
        }
    }
    with open("src\\datatest.json", "w", encoding="utf-8") as f:
        json.dump(getData, f, ensure_ascii=False, indent=4)

system("cls")
print("RUNNING BOT...\n\n\n\n\n")

import main