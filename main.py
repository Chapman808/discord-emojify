from ast import parse
import json
import requests
import base64
import argparse

def get_users(api_key : str, guild: str, role : str) -> list:
    headers = {"Authorization" : "Bot " + api_key}
    url = "https://discord.com/api/v9/guilds/" + guild + "/members?limit=1000"
    try:
        r = requests.get(url, headers=headers)
    except:
        return ["fail"]
    members = json.loads(r.text)
    return [{
        "username" : user["user"]["username"], 
        "roles" : user["roles"], 
        "avatar" : user["user"]["avatar"],
        "id" : user["user"]["id"]} 
    for user in members if role in user["roles"]]

def get_avatar_bytes(user : dict):
    userId = user["id"]
    avatarId = user["avatar"]
    url = "https://cdn.discordapp.com/avatars/" + userId + "/" + avatarId + "?size=128p"
    try:
        r = requests.get(url, stream=True)
    except:
        return ["fail"]
    avatar = r.content
    print("successfully fetched avatar for " + user["username"])
    return avatar
    #with open('avatars/' + userId + '.jpg', 'wb') as handler:
    #    handler.write(avatar)

def upload_server_emoji(guildId : str, user: dict, image : bytes, api_key : str):
    string_img = "data:image/png;base64," + base64.b64encode(image).decode("utf8")
    headers = {"Authorization" : "Bot " + api_key}
    emoji_data = {
        "name" : user["username"], 
        "image" : string_img,
        "roles" : ["559139679388172304"]
    }
    url = "https://discord.com/api/v9/guilds/" + guildId + "/emojis"
    r = requests.post(url=url, json=emoji_data, headers=headers)
    print(r.status_code, r.text)

def delete_user_emoji(guildId : str, user: dict, api_key : str):
    headers = {"Authorization" : "Bot " + api_key}
    emojiId = _get_user_emoji_id(guildId, user, api_key)
    if not emojiId: 
        return "user emoji did not exist for " + user["username"]
    url = "https://discord.com/api/v9/guilds/" + guildId + "/emojis/" + emojiId
    r = requests.delete(url=url, headers=headers)
    return r.text


def _get_user_emoji_id(guildId : str, user: dict, api_key : str):
    #get emoji ID for user emoji
    headers = {"Authorization" : "Bot " + api_key}
    url = "https://discord.com/api/v9/guilds/" + guildId + "/emojis"
    r = requests.get(url=url, headers=headers)
    for emoji in json.loads(r.text):
        if emoji["name"] == user["username"]: return emoji["id"]
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='utility to upload custom server emojis for each users on a Discord server')
    parser.add_argument('--key', required=True)
    parser.add_argument('--guild', help="guild id", required=True)
    parser.add_argument('--role', help='discord role users must be in to be emoji-fied', required=True)  
    args = parser.parse_args()

    api_key, guild, role = args.key, args.guild, args.role
    users = get_users(api_key, guild, role)

    for user in users:
        avatar = get_avatar_bytes(user)
        print(delete_user_emoji(guildId=guild, user=user, api_key=api_key))
        upload_server_emoji(guildId=guild, user=user, image=avatar, api_key=api_key)

        