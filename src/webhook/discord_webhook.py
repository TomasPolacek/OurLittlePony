import requests
import src.config as c

def send_msg(text):
    url = c.discord_text_channel["test"]
    
    data = {
        "content" : ".\nPossible arbitrage\n```" + text["desc"] + "```",
        "username" : "OurLittlePony"
    }
    
    data["embeds"] = [
        {
            "type": "rich",
            "description" : "For payout of 100€, place:",
            "title" : "Expected profit: " + text["magic"],
            "color": 0x00ff04,
        }
    ]
    data["embeds"][0]["fields"] = text["fields"]

    result = requests.post(url, json = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Discord msg sent successfully, code {}.".format(result.status_code))
