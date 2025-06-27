def format_match_for_llm(match_data):
    """
    Format match data for LLM analysis as human-readable text.
    
    Args:
        match_data (dict): The raw match data from the API
        
    Returns:
        str: Human-readable match summary for LLM analysis
    """
    # Extract the match object (could be nested under 'match' or 'context.game')
    if 'match' in match_data:
        match = match_data['match']
    elif 'context' in match_data and 'game' in match_data['context']:
        match = match_data['context']['game']
    else:
        match = match_data
    
    # Get searched summoner info for labeling
    searched_summoner = match.get('searchedSummoner', {})
    searched_puuid = searched_summoner.get('puuid')
    
    # Build the formatted text
    output = []
    
    # Game Info
    queue_type = 'Ranked Solo/Duo' if match.get('gameQueueConfigId') == 420 else 'Other Queue'
    game_length_min = match.get('gameLength', 0) // 60
    game_length_sec = match.get('gameLength', 0) % 60
    
    output.append(f"=== MATCH SUMMARY ===")
    output.append(f"Game Mode: {match.get('gameMode')} ({queue_type})")
    output.append(f"Game Length: {game_length_min}:{game_length_sec:02d}")
    output.append(f"Platform: {match.get('platformId')}")
    output.append(f"Region: {match.get('region')}")
    output.append("")
    
    # Separate teams
    team_100_players = []
    team_200_players = []
    
    for participant in match.get('participants', []):
        is_searched_user = participant.get('puuid') == searched_puuid
        
        # Clean up summoner spell names
        spell1 = participant.get('summonerSpell1Name', '').replace('Summoner', '')
        spell2 = participant.get('summonerSpell2Name', '').replace('Summoner', '')
        
        player_info = {
            'name': participant.get('riotId', 'Unknown'),
            'champion': participant.get('championName'),
            'spells': f"{spell1}/{spell2}",
            'is_me': is_searched_user,
            'puuid': participant.get('puuid')
        }
        
        if participant.get('teamId') == 100:
            team_100_players.append(player_info)
        else:
            team_200_players.append(player_info)
    
    # Format teams
    output.append("=== TEAM 100 (Blue Side) ===")
    for player in team_100_players:
        name_display = f"**{player['name']} (YOU)**" if player['is_me'] else player['name']
        output.append(f"• {name_display} - {player['champion']} ({player['spells']})")
        output.append(f"  PUUID: {player['puuid']}")
    
    output.append("")
    output.append("=== TEAM 200 (Red Side) ===")
    for player in team_200_players:
        name_display = f"**{player['name']} (YOU)**" if player['is_me'] else player['name']
        output.append(f"• {name_display} - {player['champion']} ({player['spells']})")
        output.append(f"  PUUID: {player['puuid']}")
    
    # Banned Champions
    if match.get('bannedChampions'):
        output.append("")
        output.append("=== BANNED CHAMPIONS ===")
        
        # Group bans by team
        team_100_bans = [ban for ban in match.get('bannedChampions', []) if ban.get('teamId') == 100]
        team_200_bans = [ban for ban in match.get('bannedChampions', []) if ban.get('teamId') == 200]
        
        output.append("Blue Team Bans: " + ", ".join([f"Champion ID {ban.get('championId')}" for ban in team_100_bans]))
        output.append("Red Team Bans: " + ", ".join([f"Champion ID {ban.get('championId')}" for ban in team_200_bans]))
    
    # Note about the searched player
    output.append("")
    output.append(f"NOTE: The player marked with **(YOU)** is {searched_summoner.get('riotId', 'the searched player')} - this is the current user you are analyzing for.")
    
    return "\n".join(output)


# Test data
match_data = {
    "gameId": 7444568981,
    "mapId": 11,
    "gameMode": "CLASSIC",
    "gameType": "MATCHED",
    "gameQueueConfigId": 420,
    "region": "euw1",
    "participants": [
        {
            "puuid": "I8mXriJM-uPQrr1v2HzMqj1FV3AkT6GxRm457odTmqD_b54dmexQQSx_kDwGXPZ6-YXHzRjn_gwxaA",
            "teamId": 100,
            "spell1Id": 4,
            "spell2Id": 11,
            "championId": 238,
            "profileIconId": 1149,
            "riotId": "santagotbenched1#2004",
            "bot": False,
            "gameCustomizationObjects": [],
            "perks": {
                "perkIds": [
                    8010,
                    8009,
                    9105,
                    8014,
                    8224,
                    8210,
                    5005,
                    5008,
                    5001
                ],
                "perkStyle": 8000,
                "perkSubStyle": 8200
            },
            "championName": "Zed",
            "championImageId": "Zed",
            "summonerSpell1Name": "SummonerFlash",
            "summonerSpell2Name": "SummonerSmite"
        },
        {
            "puuid": "ntftBPWIdwy9mZ3mGc1L5pjSDE_ol8AAuIHW8At_2N8h_oSw-1BE3ayGTlJpxsZmi0uCAK62wLEFsA",
            "teamId": 100,
            "spell1Id": 4,
            "spell2Id": 12,
            "championId": 136,
            "profileIconId": 4751,
            "riotId": "XadowAsol#2007",
            "bot": False,
            "gameCustomizationObjects": [],
            "perks": {
                "perkIds": [
                    8229,
                    8226,
                    8233,
                    8237,
                    8009,
                    8014,
                    5008,
                    5008,
                    5011
                ],
                "perkStyle": 8200,
                "perkSubStyle": 8000
            },
            "championName": "Aurelion Sol",
            "championImageId": "AurelionSol",
            "summonerSpell1Name": "SummonerFlash",
            "summonerSpell2Name": "SummonerTeleport"
        },
        {
            "puuid": "WD2OmL62dWDGcd_HGxBAlNbOKGpngp7z5Q1r_2ENDFHhmSahEHAgcjkM_K2JkciOTWkqO69BZL1D9g",
            "teamId": 100,
            "spell1Id": 4,
            "spell2Id": 1,
            "championId": 498,
            "profileIconId": 29,
            "riotId": "Sol Tortosa#goatツ",
            "bot": False,
            "gameCustomizationObjects": [],
            "perks": {
                "perkIds": [
                    8008,
                    8009,
                    9103,
                    8017,
                    8304,
                    8345,
                    5005,
                    5008,
                    5011
                ],
                "perkStyle": 8000,
                "perkSubStyle": 8300
            },
            "championName": "Xayah",
            "championImageId": "Xayah",
            "summonerSpell1Name": "SummonerFlash",
            "summonerSpell2Name": "SummonerBoost"
        },
        {
            "puuid": "jp9fni1Nc3-nfriZZxeMThgoTOEsOIesn5Sf0sBsRZLcz8vb4rTzE7X-wDgxgrNEHNWI7G6Dseo5RA",
            "teamId": 100,
            "spell1Id": 14,
            "spell2Id": 4,
            "championId": 99,
            "profileIconId": 6874,
            "riotId": "DοIphιn Ρμssy#MARA",
            "bot": False,
            "gameCustomizationObjects": [],
            "perks": {
                "perkIds": [
                    8229,
                    8226,
                    8210,
                    8237,
                    8126,
                    8106,
                    5008,
                    5008,
                    5001
                ],
                "perkStyle": 8200,
                "perkSubStyle": 8100
            },
            "championName": "Lux",
            "championImageId": "Lux",
            "summonerSpell1Name": "SummonerDot",
            "summonerSpell2Name": "SummonerFlash"
        },
        {
            "puuid": "aTPY2iAFtqexN-ZsiEP7Ks6Jm7kjZh_efJtheAaJFIkrIhMKdw5_fwk-roJFKVd8fRMe1tbMPM0ZKg",
            "teamId": 100,
            "spell1Id": 14,
            "spell2Id": 4,
            "championId": 8,
            "profileIconId": 29,
            "riotId": "rashai#0007",
            "bot": False,
            "gameCustomizationObjects": [],
            "perks": {
                "perkIds": [
                    8214,
                    8275,
                    8210,
                    8237,
                    8299,
                    9105,
                    5007,
                    5008,
                    5011
                ],
                "perkStyle": 8200,
                "perkSubStyle": 8000
            },
            "championName": "Vladimir",
            "championImageId": "Vladimir",
            "summonerSpell1Name": "SummonerDot",
            "summonerSpell2Name": "SummonerFlash"
        },
        {
            "puuid": "lVGomKKc2qfcDK52WT5q-V7gNfW12mJgukOCAUz-jARxJUsjw8Sr4XHScb1t31-4jrsfcsvrJhxroA",
            "teamId": 200,
            "spell1Id": 4,
            "spell2Id": 12,
            "championId": 13,
            "profileIconId": 29,
            "riotId": "Solopreneur#EUW",
            "bot": False,
            "gameCustomizationObjects": [],
            "perks": {
                "perkIds": [
                    8230,
                    8226,
                    8210,
                    8236,
                    8473,
                    8451,
                    5007,
                    5008,
                    5011
                ],
                "perkStyle": 8200,
                "perkSubStyle": 8400
            },
            "championName": "Ryze",
            "championImageId": "Ryze",
            "summonerSpell1Name": "SummonerFlash",
            "summonerSpell2Name": "SummonerTeleport"
        },
        {
            "puuid": "UK0CAZptuKuVUiHqYaYHtuIP5BL2i2vmU-6nyrCOpqqK-u8JlyNnW2lK1EneEmG_LcB8oIxatXOGoQ",
            "teamId": 200,
            "spell1Id": 7,
            "spell2Id": 4,
            "championId": 37,
            "profileIconId": 3840,
            "riotId": "Ylliade#oAo",
            "bot": False,
            "gameCustomizationObjects": [],
            "perks": {
                "perkIds": [
                    8214,
                    8226,
                    8234,
                    8236,
                    8304,
                    8316,
                    5008,
                    5010,
                    5011
                ],
                "perkStyle": 8200,
                "perkSubStyle": 8300
            },
            "championName": "Sona",
            "championImageId": "Sona",
            "summonerSpell1Name": "SummonerHeal",
            "summonerSpell2Name": "SummonerFlash"
        },
        {
            "puuid": "osaQSeh4I45xYeKQ940v0pcQFREV1tlse80z0Ig4YoaslJEsH8Ocbft9Wa28tEuy4XhOmcbJbFG_9Q",
            "teamId": 200,
            "spell1Id": 11,
            "spell2Id": 4,
            "championId": 91,
            "profileIconId": 4896,
            "riotId": "twtv shiftlol5#2005",
            "bot": False,
            "gameCustomizationObjects": [],
            "perks": {
                "perkIds": [
                    8021,
                    9111,
                    9105,
                    8014,
                    8304,
                    8347,
                    5008,
                    5008,
                    5001
                ],
                "perkStyle": 8000,
                "perkSubStyle": 8300
            },
            "championName": "Talon",
            "championImageId": "Talon",
            "summonerSpell1Name": "SummonerSmite",
            "summonerSpell2Name": "SummonerFlash"
        },
        {
            "puuid": "hGk5C7RvmQMPx5qQk9R8ZBNUhnfvBOwmdIbquSnFMErfBgJdGaXMMnGzwUcTFqMcBwVztaf6W_pmfw",
            "teamId": 200,
            "spell1Id": 4,
            "spell2Id": 12,
            "championId": 45,
            "profileIconId": 1115,
            "riotId": "Sukran Reborn#lov",
            "bot": False,
            "gameCustomizationObjects": [],
            "perks": {
                "perkIds": [
                    8369,
                    8304,
                    8345,
                    8347,
                    8226,
                    8210,
                    5007,
                    5008,
                    5001
                ],
                "perkStyle": 8300,
                "perkSubStyle": 8200
            },
            "championName": "Veigar",
            "championImageId": "Veigar",
            "summonerSpell1Name": "SummonerFlash",
            "summonerSpell2Name": "SummonerTeleport"
        },
        {
            "puuid": "_gUkT-gMmNZLuNLk2ykgfm7Wk-8TPjDJrSVSE0w3VVVZOA3H5f382A-TUTxNupv8GTNHkKITjQ0gJA",
            "teamId": 200,
            "spell1Id": 4,
            "spell2Id": 14,
            "championId": 39,
            "profileIconId": 906,
            "riotId": "Suseri#1997",
            "bot": False,
            "gameCustomizationObjects": [],
            "perks": {
                "perkIds": [
                    8010,
                    9111,
                    9104,
                    8299,
                    8473,
                    8453,
                    5005,
                    5008,
                    5001
                ],
                "perkStyle": 8000,
                "perkSubStyle": 8400
            },
            "championName": "Irelia",
            "championImageId": "Irelia",
            "summonerSpell1Name": "SummonerFlash",
            "summonerSpell2Name": "SummonerDot"
        }
    ],
    "observers": {
        "encryptionKey": "xvjICseyzNqlXXyzvQL7K9fR3s+EatJC"
    },
    "platformId": "EUW1",
    "bannedChampions": [
        {
            "championId": 141,
            "teamId": 100,
            "pickTurn": 1
        },
        {
            "championId": 76,
            "teamId": 100,
            "pickTurn": 2
        },
        {
            "championId": 68,
            "teamId": 100,
            "pickTurn": 3
        },
        {
            "championId": 11,
            "teamId": 100,
            "pickTurn": 4
        },
        {
            "championId": 777,
            "teamId": 100,
            "pickTurn": 5
        },
        {
            "championId": 134,
            "teamId": 200,
            "pickTurn": 6
        },
        {
            "championId": 119,
            "teamId": 200,
            "pickTurn": 7
        },
        {
            "championId": 555,
            "teamId": 200,
            "pickTurn": 8
        },
        {
            "championId": 84,
            "teamId": 200,
            "pickTurn": 9
        },
        {
            "championId": 114,
            "teamId": 200,
            "pickTurn": 10
        }
    ],
    "gameStartTime": 1750994594550,
    "gameLength": 154,
    "searchedSummoner": {
        "puuid": "jp9fni1Nc3-nfriZZxeMThgoTOEsOIesn5Sf0sBsRZLcz8vb4rTzE7X-wDgxgrNEHNWI7G6Dseo5RA",
        "gameName": "DοIphιn Ρμssy",
        "tagLine": "MARA",
        "riotId": "DοIphιn Ρμssy#MARA"
    }
}

# Test the function
if __name__ == "__main__":
    print(format_match_for_llm(match_data))  