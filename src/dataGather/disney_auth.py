import json
import requests

def get_header():
    r = requests.get("https://disneyworld.disney.go.com/authentication/get-client-token")
    headers = {"Authorization":"BEARER {}".format(json.loads(r.content)["access_token"])}

    return headers
