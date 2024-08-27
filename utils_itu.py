import json
import requests  # pip install requests

from utils import data_dir

url_prefix = "https://api.triathlon.org/v1/"

with open("api_key.txt", "r") as f:
    api_key = f.readline()
headers = {'apikey': api_key}


def get_request(url_suffix, params=""):
    url = url_prefix + url_suffix
    # print(url)
    response = requests.request("GET", url, headers=headers, params=params)
    d = json.loads(response.text)
    d = d["data"]
    return d


def get_athlete_info(athlete_id: int):
    saving_path = data_dir / "athletes" / f"{athlete_id}.json"
    saving_path.parent.mkdir(parents=True, exist_ok=True)
    # check if athlete_id has already been retrieved and saved
    if saving_path.exists():
        with open(saving_path) as f:
            res = json.load(f)
        return res
    url_suffix = f"athletes/{athlete_id}"
    res = get_request(url_prefix + url_suffix)
    with open(saving_path, "w") as f:
        json.dump(res, f)
    return res


category_mapping = {
    343: "games",  # "Major Games",
    345: "games",  # "Recognised Event",
    346: "games",  # "Recognised Games",
    624: "wcs",  # "World Championship Finals",
    351: "wcs",  # "World Championship Series",
    349: "world-cup",  # "World Cup",
}