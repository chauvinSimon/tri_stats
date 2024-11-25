"""

"""

from datetime import datetime
from typing import Optional

import cv2
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import re

import requests
from PIL import Image
from io import BytesIO

from utils import json_dump, data_dir, cache_dir, ignored_dir, json_load, load_config
from utils_itu import get_request, get_athlete_info

tmp_results_file_path = ignored_dir / "tmp_results.csv"
log_file_path = ignored_dir / "log.json"
conditions_logs_path = ignored_dir / "conditions_inconsistencies.json"
conditions_logs_path.parent.mkdir(parents=True, exist_ok=True)

# todo: is it the correct way to set the math fonts?
plt.rcParams["font.family"] = "monospace"  # todo: set in global config
plt.rcParams['mathtext.default'] = 'rm'
plt.rcParams['mathtext.fontset'] = 'cm'  # "stix


def clean_up_log_file():
    json_dump({}, log_file_path)


def clean_up_conditions_log_file():
    json_dump([], conditions_logs_path)


def update_log_file(
        category: str,
        event_id: int,
        txt: str = "",
        event_title: str = "",
        event_listing: str = ""
):
    if not log_file_path.exists():
        clean_up_log_file()

    log_data = json_load(log_file_path)

    all_cats = ["loaded", "ignored", "returned"]
    assert category in all_cats, f"{category = } not in {all_cats = }"
    for cat in all_cats:
        if cat not in log_data:
            log_data[cat] = {}

    if event_id in log_data[category]:
        log_data[category][event_id]["txt"] = log_data[category][event_id]["txt"] + "\n" + txt
    else:
        log_data[category][event_id] = {"txt": txt, "event_title": event_title, "event_listing": event_listing}
    json_dump(log_data, log_file_path)

def print_log_file():
    log_data = json_load(log_file_path)
    loaded_data = log_data['loaded']
    ignored_data = log_data['ignored']
    returned_data = log_data['returned']

    print(f"loaded events:   {len(loaded_data)}")
    print(f"ignored events:  {len(ignored_data)}")
    print(f"returned events: {len(returned_data)}")

    if len(loaded_data) != len(ignored_data) + len(returned_data):
        print(f"events not processed: {len(loaded_data) - len(ignored_data) - len(returned_data)}")
    for event_id in loaded_data:
        if event_id not in ignored_data and event_id not in returned_data:
            print(f"\t-{event_id}: {loaded_data[event_id]['event_title']}")
    print()

    print(f"### ### ###\n{len(ignored_data)} ignored events:\n### ### ###\n")
    for event_id, event_data in sorted(ignored_data.items(), key=lambda item: item[1]['txt']):
        print(f"event [{event_id}] ignored: {event_data['event_title']}")
        print("\t" + event_data['txt'])
        print("\t" + event_data['event_listing'])

    # save to csv
    rows_dicts = [
        {"event_id": k, "txt": v["txt"], "event_title": v["event_title"], "event_listing": v["event_listing"]} for k, v in ignored_data.items()
    ]
    df = pd.DataFrame(rows_dicts)
    if not df.empty:
        df.sort_values("txt", inplace=True)
    df.to_csv(ignored_dir / "ignored_events_after_processing.csv")


def seconds_to_h_min_sec(
        time_sec: float,
        use_hours: bool = True,
        sport: str = None,
        use_units: bool = True
) -> str:
    minutes, seconds = divmod(time_sec, 60)
    hours, minutes_h = divmod(minutes, 60)

    info = ""
    if sport == "run":
        distance = 10 if minutes > 25 else 5
        min_sec = divmod(time_sec / distance, 60)
        suffix = " /km)" if use_units else ")"
        info = f"({min_sec[0]:02.0f}:{min_sec[1]:02.0f}{suffix}"
    elif sport == "swim":
        distance = 15 if minutes > 13 else 7.5
        min_sec = divmod(time_sec / distance, 60)
        suffix = " /100m)" if use_units else ")"
        info = f"({min_sec[0]:02.0f}:{min_sec[1]:02.0f}{suffix}"
    elif sport == "bike":
        distance = 40 if minutes > 45 else 20
        speed_km_h = distance / (time_sec / 3600)
        suffix = " km/h)" if use_units else ")"
        info = f"({speed_km_h:.1f}{suffix}"

    if hours > 0:
        if use_hours:
            res = f"{hours:02.0f}:{minutes_h:02.0f}:{seconds:02.0f}"
        else:
            res = f"{minutes:02.0f}:{seconds:02.0f}"
    else:
        res = f"{minutes:02.0f}:{seconds:02.0f}"
    if info:
        res += f" {info}"
    return res


def get_events_categories():
    suffix = "events/categories?show_children=true"
    res = get_request(url_suffix=suffix)
    for r in res:
        print(r["cat_id"], r["cat_name"])
    print(res)
    return res


def get_events_specifications():
    suffix = "events/specifications?show_children=true"
    res = get_request(url_suffix=suffix)
    for r in res:
        print(r["cat_id"], r["cat_name"])
    print(res)
    return res


def get_program_listings(event_id: int, program_names: list):
    suffix = f"events/{event_id}/programs"
    res_req = get_request(url_suffix=suffix)
    res = []
    if res_req is None:
        return res
    for r in res_req:
        if r["prog_name"] in program_names:
            res.append({"prog_id": r["prog_id"], "prog_name": r["prog_name"]})
    return res


def get_program_info(event_id: int, prog_id: int):
    suffix = f"events/{event_id}/programs/{prog_id}"
    res_req = get_request(url_suffix=suffix)
    return res_req


def save_images(
        event_id: int,
        event_title: str = "",
        per_page: int = 1000
):
    images_dir = cache_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    saving_dir = images_dir / f"{event_id}"

    if saving_dir.exists():
        return
    saving_dir.mkdir(parents=True, exist_ok=True)

    suffix = f"events/{event_id}/images?per_page={per_page}"
    res_req = get_request(url_suffix=suffix)
    if res_req is None or len(res_req) == 0:
        print(f"\t!! No images found for event {event_id}: {event_title}")
        return
    urls = {
        r["image_filename"]: r["thumbnail"]  # r["image_url"]
        for r in res_req if "image_url" in r
    }
    print(f"\tfound {len(urls)} images for event {event_id}: {event_title}")
    assert per_page >= len(urls), f"per_page ({per_page}) must be >= len(urls) ({len(urls)})"
    for filename, url in urls.items():
        saving_path = saving_dir / filename
        if saving_path.exists():
            continue

        # download image
        try:
            response = requests.get(
                url,
                # headers=headers
            )
            if response.status_code == 200:
                # with saving_path.open('wb') as file:
                #     file.write(response.content)

                # Open the image from the response content
                image = Image.open(BytesIO(response.content))

                # Define the maximum size
                max_size = (600, 600)  # Example max size, you can change this

                # Resize the image while maintaining aspect ratio
                image.thumbnail(max_size, Image.LANCZOS)

                # Save the resized image
                image.save(str(saving_path))

            else:
                print(f"\tFailed to retrieve image. Status code: {response.status_code}")
        except Exception as e:
            print(e)
            print(url)
            print(filename)


def save_race_results(events_config: dict):
    ###
    program_names = events_config["program_names"]
    specification_ids = events_config["specification_ids"]
    category_ids = events_config["category_ids"]

    start_date = events_config["query"]["start_date"]
    end_date = events_config["query"]["end_date"]
    per_page = events_config["query"]["per_page"]
    ###

    ignored_event_file = cache_dir / "events" / "ignored_events.json"
    ignored_event_file.parent.mkdir(parents=True, exist_ok=True)
    if ignored_event_file.exists():
        ignored_events = json_load(ignored_event_file)
    else:
        ignored_events = {}

    events_query_file = cache_dir / "events" / "events_query.json"
    events_query_file.parent.mkdir(parents=True, exist_ok=True)
    if events_query_file.exists():
        events_queries = json_load(events_query_file)
    else:
        events_queries = {}

    for spec_id, spec_name in specification_ids:
        for cat_id, cat_name in category_ids.items():
            # https://developers.triathlon.org/reference/event-listings
            suffix = f"events?category_id={cat_id}&start_date={start_date}&end_date={end_date}"
            suffix += f"&specification_id={spec_id}"
            suffix += f"&per_page={per_page}"
            if suffix in events_queries.keys():
                res = events_queries[suffix]
            else:
                res = get_request(url_suffix=suffix)
                if isinstance(res, dict) and (list(res.keys()) == ["errors"]):
                    raise ValueError(f"ERROR: for {suffix}: no results: {res['errors']}. (Maybe the date does not exist, e.g. 31st of Sept?)")
                events_queries[suffix] = res
                json_dump(data=events_queries, p=events_query_file)

            print(f"\n### ### ###\n{spec_name = } ({spec_id = }), {cat_name = } ({cat_id = }): {len(res) = }\n### ### ###")
            assert len(res) < per_page, f"More than {per_page = } results! Increase per_page"
            for r in res:
                event_id = r["event_id"]
                event_title = r["event_title"]
                event_listing = r["event_listing"]

                res_specification_ids = [s["cat_id"] for s in r["event_specifications"]]
                assert spec_id in res_specification_ids, f"{event_title} ({event_id}): {spec_id = } not in {res_specification_ids = }"

                print(f"{event_title} ({event_id}): {spec_id = } {cat_id = }")
                if cat_name == "Recognised Games":
                    if "Commonwealth Games" not in event_title:
                        continue
                    print()

                if cat_name == "Major Games":
                    if "Youth" in event_title:
                        continue
                    if "Olympic Games" not in event_title:
                        continue
                    print(f"\t{event_title} ({event_id})")

                if cat_name == "Recognised Event":
                    if not any([e in event_title for e in ["Olympic Games Test", "Olympic Qualification Event"]]):
                        continue
                    print(f"\t{event_title} ({event_id})")

                saving_path = cache_dir / "events" / f"{event_id}.json"
                if saving_path.exists():
                    print(f"\t{event_title} ({event_id}) already processed")
                    continue

                if str(event_id) in ignored_events:
                    print(f"\t{event_title} ({event_id}) already ignored")
                    continue

                res_specification_ids = [s["cat_id"] for s in r["event_specifications"]]
                if spec_id not in res_specification_ids:
                    print(f"\t{event_title} ({event_id}): {res_specification_ids = }")
                    continue

                listings = get_program_listings(event_id=event_id, program_names=program_names)
                if not listings:
                    print(f"\nERROR: no listing found for {event_title} ({event_id})\n")
                    ignored_events[event_id] = {
                        "event_title": event_title,
                        "event_listing": event_listing,
                        "txt": f"no listing found"
                    }
                    json_dump(ignored_events, p=ignored_event_file)
                    continue

                saving_path.parent.mkdir(parents=True, exist_ok=True)
                saving_dicts = {}

                print(f"{event_title} ({event_id})")
                for listing in listings:
                    saving_dict = {
                        "prog_name": listing['prog_name'],
                        "event_title": event_title,
                        "event_id": event_id,
                        "event_venue": r["event_venue"],
                        "event_date": r["event_date"],
                        "event_country_noc": r["event_country_noc"],
                        "event_listing": r["event_listing"],
                    }

                    print(f"\t{listing['prog_id']} {listing['prog_name']}")

                    suffix = f"events/{event_id}/programs/{listing['prog_id']}"
                    res = get_request(url_suffix=suffix)
                    saving_dict["prog_distances"] = res["prog_distances"]

                    saving_dict["prog_distance_category"] = res["prog_distance_category"]
                    saving_dict["prog_notes"] = res["prog_notes"]

                    if saving_dict["prog_distance_category"] is None or saving_dict["prog_distance_category"] == "":
                        if (res["prog_notes"] is not None) and ("750" in res["prog_notes"]):
                            print("\t\tfallback: 750 -> sprint")
                            saving_dict["prog_distance_category"] = "sprint"
                        elif (res["prog_notes"] is not None) and ("1500" in res["prog_notes"]):
                            print("\t\tfallback: 1500 -> standard")
                            saving_dict["prog_distance_category"] = "standard"
                        elif saving_dict["prog_distances"] and saving_dict["prog_distances"][0]["distance"] == 750:
                            print("\t\tfallback2: 750 -> sprint")
                            saving_dict["prog_distance_category"] = "sprint"
                        elif saving_dict["prog_distances"] and saving_dict["prog_distances"][0]["distance"] == 1500:
                            print("\t\tfallback2: 1500 -> standard")
                            saving_dict["prog_distance_category"] = "standard"
                        else:
                            print("\t\tERROR: cannot detect distance")

                    suffix = f"events/{event_id}/programs/{listing['prog_id']}/results"
                    res = get_request(url_suffix=suffix)
                    saving_dict["results"] = res["results"]
                    saving_dict["prog_gender"] = res["prog_gender"]
                    saving_dict["event_categories"] = res["event"]["event_categories"]
                    # event_categories = saving_dict["event_categories"]
                    saving_dict["headers"] = res["headers"]
                    if not saving_dict["prog_distance_category"]:
                        if saving_dict["results"]:
                            winner_time = saving_dict['results'][0]['total_time']
                            print(f"\t\t\twinner time: {winner_time}")
                            if winner_time[:4] in ["00:4", "00:5", "01:0", "01:1"]:
                                print(f"\t\t\tfallback3: {winner_time} -> sprint")
                                saving_dict["prog_distance_category"] = "sprint"
                            elif winner_time[:4] in ["01:3", "01:4", "01:5", "02:0", "02:1"]:
                                print(f"\t\t\tfallback3: {winner_time} -> standard")
                                saving_dict["prog_distance_category"] = "standard"

                    required_keys = [
                        "headers",
                        "results",
                        "prog_gender",
                        "prog_distance_category",
                        # "prog_distances"
                    ]
                    missing_keys = [key for key in required_keys if not saving_dict.get(key)]
                    if missing_keys:
                        print(f"\t\tERROR: Skipping {event_title} (ID: {event_id})")
                        print(f"\t\t\tMissing keys: {', '.join(missing_keys)}")
                        ignored_events[event_id] = {
                            "event_title": event_title,
                            "event_listing": event_listing,
                            "txt": f"Missing keys: {', '.join(missing_keys)}"
                        }

                        # Save ignored events to file
                        json_dump(ignored_events, p=ignored_event_file)
                        continue

                    saving_dicts[listing['prog_id']] = saving_dict

                if saving_dicts:
                    json_dump(data=saving_dicts, p=saving_path)

    ignored_events = {event_id: event_data for event_id, event_data in sorted(ignored_events.items(), key=lambda item: item[1]['txt'])}
    json_dump(ignored_events, p=ignored_event_file)
    # save as csv
    rows_dicts = [{
        "event_id": k,
        "txt": v["txt"],
        "event_listing": v["event_listing"],
        "event_title": v["event_title"]
    }
        for k, v in ignored_events.items()
    ]
    df = pd.DataFrame(rows_dicts)
    if not df.empty:
        df.sort_values("txt", inplace=True)
    df.to_csv(ignored_dir / "ignored_events_before_processing.csv")


def compute_age_with_decimals(date_of_birth: str, specific_date: str) -> float:
    dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
    specific = datetime.strptime(specific_date, "%Y-%m-%d")

    delta = specific - dob
    return delta.days / 365.25


def update_athlete_ids(r):
    athlete_nocs_file = data_dir / "athlete_nocs.json"
    athlete_nocs = json_load(athlete_nocs_file)

    athlete_ids_file = data_dir / "athlete_id_name_mapping.json"
    athlete_ids = json_load(athlete_ids_file)
    athlete_id = r["athlete_id"]
    if athlete_id not in athlete_ids:
        athlete_ids[athlete_id] = [r["athlete_first"], r["athlete_last"]]
        json_dump(athlete_ids, athlete_ids_file)

    if athlete_id not in athlete_nocs:
        athlete_nocs[athlete_id] = r["athlete_noc"]
        json_dump(athlete_nocs, athlete_nocs_file)

def get_level_for_year(
        years_id_rankings: dict,
        prog_year: str,
        athletes_infos: list,
        n_top: int = 10,
        default_ranking: int = 50    # use 50 as default if not found because len(ranking) should be 50
) -> Optional[float]:
    if prog_year not in years_id_rankings:
        return None

    year_id_rankings = years_id_rankings[prog_year]
    year_athlete_ids = [int(r[0]) for r in year_id_rankings]

    rankings = []
    for i_start_num, athlete_info in enumerate(athletes_infos):
        if i_start_num > n_top:
            break
        if athlete_info["athlete_id"] in year_athlete_ids:
            athlete_ranking = year_athlete_ids.index(athlete_info["athlete_id"]) + 1
            rankings.append(athlete_ranking)
        else:
            # print(f"{athlete_info} not found")
            rankings.append(default_ranking)

    # print(rankings)
    if len(rankings) == 0:
        return None

    return sum(rankings) / len(rankings)


def get_level(prog_data: dict) -> Optional[float]:  # optional
    prog_year = str(prog_data["event_date"][:4])

    athletes_infos = []
    for r in prog_data["results"]:
        if r["position"] in ["DNF", "DNS", "DSQ", "LAP"]:
            continue
        if r["start_num"] is None:
            continue
        athletes_infos.append({
            "athlete_id": r["athlete_id"],
            "athlete_name": f'{r["athlete_first"]} {r["athlete_last"]}',
            "start_num": r["start_num"],
        })

    athletes_infos_by_start_nums = sorted(athletes_infos, key=lambda x: x["start_num"])

    gender_dict = {"male": "m", "female": "w"}
    prog_gender = prog_data["prog_gender"]
    if prog_gender not in gender_dict:
        print(f"ERROR: {prog_gender} not in {list(gender_dict.keys())}")
        return None
    gender = gender_dict[prog_gender]
    json_path = data_dir / f"years_id_rankings_{gender}.json"
    if not json_path.exists():
        print(f"ERROR: {json_path} not found")
        return None
    years_id_rankings = json_load(data_dir / f"years_id_rankings_{gender}.json")

    levels = [
        # using the order of start numbers
        get_level_for_year(years_id_rankings, prog_year, athletes_infos_by_start_nums),
        get_level_for_year(years_id_rankings, str(int(prog_year) - 1), athletes_infos_by_start_nums),
        get_level_for_year(years_id_rankings, str(int(prog_year) + 1), athletes_infos_by_start_nums),

        # using the order of race results
        get_level_for_year(years_id_rankings, prog_year, athletes_infos),
        get_level_for_year(years_id_rankings, str(int(prog_year) - 1), athletes_infos),
        get_level_for_year(years_id_rankings, str(int(prog_year) + 1), athletes_infos),
    ]
    levels = [l for l in levels if l is not None]
    if len(levels) == 0:
        return None
    return sum(levels) / len(levels)


def get_prog_results_df(prog_data: dict) -> pd.DataFrame:
    column_names = [header["name"] for header in prog_data["headers"]]
    # create a dataframe from the results
    df_list = []
    prog_year = int(prog_data["event_date"][:4])
    for r in prog_data["results"]:
        # update_athlete_ids(r)
        if r["position"] in ["DNF", "DNS", "DSQ", "LAP"]:
            continue
        di = dict(zip(column_names, r["splits"]))
        # todo: for accuracy in the age, prefer dob over yob - but it requires a lot of API calls for all athletes
        # if ("dob" not in r) or (r["dob"] is None):
        #     athlete_id = r["athlete_id"]
        #     athlete_info = get_athlete_info(athlete_id)
        #     if (athlete_info is not None) and ("dob" in athlete_info):
        #         r["dob"] = athlete_info["dob"]
        #     else:
        #         print(f"{athlete_id}: no 'dob' info ({r['athlete_first']} {r['athlete_last']} [{r['athlete_noc']}])")

        di["age"] = None
        if ("dob" not in r) or (r["dob"] is None):
            if "athlete_yob" in r:
                if r["athlete_yob"] is not None:
                    di["age"] = compute_age_with_decimals(date_of_birth=f'{r["athlete_yob"]}-07-01', specific_date=prog_data["event_date"])  # on average, a person was born on July, 1st
        else:
            di["age"] = compute_age_with_decimals(date_of_birth=r["dob"], specific_date=prog_data["event_date"])
            assert abs(prog_year - int(r["athlete_yob"]) - di["age"]) < 2

        if di["age"] is None:
            print(f"WARNING: no age for {r['athlete_id']}: {r['athlete_first']} {r['athlete_last']} [{r['athlete_noc']}]")
        df_list.append(di)
    df = pd.DataFrame(df_list)
    if len(df) < 1:
        print(f"{prog_data['event_title']}: only {len(df)} valid results")
        return df

    def str_to_seconds(x):
        h, m, s = x.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)

    for column_name in column_names:
        df[f"{column_name.lower()}_s"] = df[column_name].apply(str_to_seconds)

    # discard the column with name in headers
    df = df.drop(columns=column_names)

    # drop lines with 0 as run_s (DNF or DNS)
    df = df[(df["swim_s"] > 0) & (df["bike_s"] > 0) & (df["run_s"] > 0)]

    return df


def find_substring_with_context(long_string, target_word, context_size=3):
    if long_string is None:
        return
    # Split the long string into words
    words = long_string.split()

    # Iterate through the list to find the target word
    for index, word in enumerate(words):
        # Check if the current word matches the target word, ignoring case
        if target_word.lower() in word.lower():
            # Calculate the start and end indices for the context
            start = max(0, index - context_size)
            end = min(len(words), index + context_size + 1)

            # Extract the context words
            context_words = words[start:end]

            # Join the context words into a substring
            context_substring = ' '.join(context_words)

            # Print the context substring
            print(f"\t\t{context_substring}")


def extract_air_and_water_temperatures(long_string):
    if long_string is None:
        return None, None
    if not long_string:
        return None, None

    res = []

    for measure in ["air", "water"]:
        # Define a regular expression pattern to match the water temperature
        pattern = f"{measure} temperature[:\s]*([\d.]+)"

        # Search for the pattern in the string
        match = re.search(pattern, long_string.lower())

        if match:
            # Extract the temperature value from the match
            temperature_str = match.group(1)
            if temperature_str[-1] == ".":
                temperature_str = temperature_str[:-1]
            # Convert the extracted value to float
            temperature = float(temperature_str)

            res.append(temperature)
        else:
            # if ("temp" in long_string.lower()) or ("water" in long_string.lower()):
            #     raise ValueError(f"maybe regex {pattern} is not good enough: {long_string}")
            # print(f"{long_string}")
            res.append(None)

    return res


def extract_air_water_and_wetsuit(
        prog_id: int,
        prog_data,
        suffix: str,
        label_manually: bool
) -> tuple[float|None, float|None, bool|None]:
    if prog_data["prog_name"] == "Elite Men":
        assert suffix == "_m"
    elif prog_data["prog_name"] == "Elite Women":
        assert suffix == "_w"
    else:
        raise ValueError(f"{prog_data['prog_name']} not supported")

    log_dict = {
        "event_id": prog_data["event_id"],
        "event_title": prog_data["event_title"],
        "event_listing": prog_data["event_listing"],
        "event_venue": prog_data["event_venue"],
        "event_country_noc": prog_data["event_country_noc"],
        "event_date": prog_data["event_date"],
        "prog_id": prog_id,
        "prog_name": prog_data["prog_name"],
        "issues": []
    }

    if conditions_logs_path.exists():
        conditions_logs = json_load(conditions_logs_path)
    else:
        conditions_logs = []

    air_temperatures = []
    water_temperatures = []
    wetsuits = []

    # 1st method: should be the most reliable
    # url --request GET --url 'https://api.triathlon.org/v1/events/183774/programs/635344?per_page=10&order=asc' --header 'accept: application/json' --header 'apikey: 2649776ef9ece4c391003b521cbfce7a'
    prog_file_path = cache_dir / "prog_info" / f"{prog_data['event_id']}_{prog_id}.json"
    if prog_file_path.exists():
        prog_info = json_load(prog_file_path)
    else:
        prog_info = get_program_info(event_id=prog_data["event_id"], prog_id=prog_id)
        prog_file_path.parent.mkdir(parents=True, exist_ok=True)
        json_dump(prog_info, prog_file_path)

    try:
        air_temperatures.append(prog_info["meta"]["temperature_air"])
    except Exception as e:
        print(e)
    try:
        water_temperatures.append(prog_info["meta"]["temperature_water"])
    except Exception as e:
        print(e)
    try:
        wetsuits.append(prog_info["meta"]["wetsuit"])
    except Exception as e:
        print(e)

    # 2nd method
    if prog_data["prog_notes"] is not None:
        if any(substring in prog_data["prog_notes"].lower() for substring in
               ["wetsuits allowed", "wetsuit allowed", ". wetsuit swim."]):
            wetsuits.append(True)
        elif "wetsuits not allowed" in prog_data["prog_notes"].lower():
            wetsuits.append(False)

    # 3rd method
    air_and_water_temps = extract_air_and_water_temperatures(prog_data["prog_notes"])
    air_temperatures.append(air_and_water_temps[0])
    water_temperatures.append(air_and_water_temps[1])

    # 4th method
    manual_labelled_wetsuit_file = data_dir / "manual_labelled_wetsuit.json"
    if manual_labelled_wetsuit_file.exists():
        manual_labelled_wetsuit = json_load(manual_labelled_wetsuit_file)
    else:
        manual_labelled_wetsuit = {}

    wetsuit_key = f'{prog_data["event_id"]}{suffix}'
    if wetsuit_key in manual_labelled_wetsuit:
        wetsuits.append(manual_labelled_wetsuit[wetsuit_key]["wetsuit"])

    # resolve air temperature
    air_temperatures = [t for t in air_temperatures if t is not None]
    air_temperatures = [float(t) if isinstance(t, int) else t for t in air_temperatures]
    # isnumeric only works for int numbers
    air_temperatures = [float(t) if (isinstance(t, str) and t.replace(".", "", 1).isdigit()) else t for t in air_temperatures]
    if not air_temperatures:
        air_temperature = None
    else:
        if len(set(air_temperatures)) != 1:
            print(f"different {air_temperatures = }")
            log_dict["issues"].append(f"{air_temperatures = }")
        air_temperature = air_temperatures[0]


    # resolve water temperature
    water_temperatures = [t for t in water_temperatures if t is not None]
    water_temperatures = [float(t) if isinstance(t, int) else t for t in water_temperatures]
    # isnumeric only works for int numbers
    water_temperatures = [float(t) if (isinstance(t, str) and t.replace(".", "", 1).isdigit()) else t for t in water_temperatures]


    if not water_temperatures:
        water_temperature = None
    else:
        if len(set(water_temperatures)) != 1:
            print(f"different {water_temperatures = }")
            log_dict["issues"].append(f"{water_temperatures = }")
        water_temperature = water_temperatures[0]

    # 5th method
    if water_temperature is not None:
        try:
            if float(water_temperature) >= 20:
                wetsuits.append(False)
            else:
                wetsuits.append(True)
        except Exception as e:
            print(f"cannot compare {water_temperature = } to 20°: {e}")

    # resolve wetsuit
    wetsuits = [w for w in wetsuits if w is not None]
    wetsuits = [True if (isinstance(w, str) and w.lower() == "allowed") else w for w in wetsuits]
    wetsuits = [True if (isinstance(w, str) and w.lower() == "mandatory") else w for w in wetsuits]
    wetsuits = [False if (isinstance(w, str) and w.lower() == "forbidden") else w for w in wetsuits]
    if not wetsuits:
        wetsuit = None
    else:
        if len(set(wetsuits)) != 1:
            print(f"different {wetsuits = }")
            log_dict["issues"].append(f"{wetsuits = } (retrieved {water_temperatures = }) (retrieved {air_temperatures = })")
        wetsuit = wetsuits[0]

    # 6th method
    if wetsuit is not None:
        print(f"unknown wetsuit: {wetsuit_key} ({prog_data['event_title']})")
        if prog_data["prog_notes"] is not None:
            print(prog_data["prog_notes"])

        if label_manually:
            save_images(
                event_id=prog_data["event_id"],
                event_title=prog_data["event_title"],
                per_page=1000
            )

            images_dir = cache_dir / "images" / str(prog_data["event_id"])

            # glob png and jpg and jpeg
            image_paths = list(images_dir.glob("*.[jpJP][npNP][egEG]*"))
            if len(image_paths) == 0:
                print(f"no images for manual wetsuit label: {wetsuit_key}")
            else:
                for image_file in image_paths:
                    img = cv2.imread(str(image_file))

                    # img = cv2.resize(img, (2000, 2000))

                    # resize if shape too big
                    shape = img.shape
                    if shape[0] > 2000 or shape[1] > 2000:
                        img = cv2.resize(img, (2000, 2000))

                    cv2.imshow(f'{prog_data["event_id"]} - {prog_data["event_title"]}', img)
                    k = cv2.waitKey(0)
                    if k in [ord("q"), 27]:
                        cv2.destroyAllWindows()
                        break

                # input, ask for wetsuit
                response = input(f"wetsuit for {prog_data['prog_name']}? (y/n/?)")
                if response == "y":
                    wetsuit = True
                elif response == "n":
                    wetsuit = False
                else:
                    wetsuit = None

                manual_labelled_wetsuit[wetsuit_key] = {
                    "wetsuit": wetsuit,
                    "event_title": prog_data["event_title"],
                    "event_listing": prog_data["event_listing"]
                }
                json_dump(manual_labelled_wetsuit, manual_labelled_wetsuit_file)

    log_dict["air_temperature"] = air_temperature
    log_dict["water_temperature"] = water_temperature
    log_dict["wetsuit"] = wetsuit

    if len(log_dict["issues"]) > 0:
        conditions_logs.append(log_dict)
        json_dump(data=conditions_logs, p=conditions_logs_path)

    return air_temperature, water_temperature, wetsuit


def get_events_results(events_config: dict) -> pd.DataFrame:
    ###
    start_date = events_config["query"]["start_date"]
    end_date = events_config["query"]["end_date"]

    sports = events_config["sports"]
    category_ids = events_config["category_ids"]

    pack_duration_s = events_config["pack_duration_s"]

    n_results_min = events_config["cleaning"]["n_results_min"]

    distance_categories = events_config["distance_categories"]
    label_manually = events_config["label_manually"]

    i_first = events_config["mean_computation"]["i_first"]
    i_last = events_config["mean_computation"]["i_last"]
    use_best_in_each_sport = events_config["mean_computation"]["use_best_in_each_sport"]

    per_page = events_config["query"]["per_page"]
    ###

    print("\nget_events_results\n")

    events_dir = cache_dir / "events"
    events_results = []

    for event_file in events_dir.glob("*.json"):
        if not event_file.stem.isnumeric():  # ignore `events_query.json` and `ignored_events.json`
            continue
        event_dict = json_load(event_file)
        _event_id = 0
        try:
            _event_id = set([prog_data["event_id"] for prog_data in event_dict.values()])
            assert len(_event_id) == 1
            _event_id = _event_id.pop()
        except Exception as e:
            print(f"cannot find single event_id: {event_file.stem} - {e}")

        _event_title = ""
        try:
            _event_title = set([prog_data["event_title"] for prog_data in event_dict.values()])
            assert len(_event_title) == 1
            _event_title = _event_title.pop()
        except Exception as e:
            print(f"cannot find single event_title: {event_file.stem} - {e}")

        _event_listing = ""
        try:
            _event_listing = set([prog_data["event_listing"] for prog_data in event_dict.values()])
            assert len(_event_listing) == 1
            _event_listing = _event_listing.pop()
        except Exception as e:
            print(f"cannot find single event_listing: {event_file.stem} - {e}")
        update_log_file(
            category="loaded",
            event_id=_event_id,
            event_title=_event_title,
            event_listing=_event_listing
        )

        if len(event_dict) < 2:
            print(f"{event_file.stem}\n\tnot enough data: {list(event_dict.keys())}")
            update_log_file(
                category="ignored",
                event_id=_event_id,
                event_title=_event_title,
                event_listing=_event_listing,
                txt=f"not enough data: {[prog_data['prog_name'] for prog_data in event_dict.values()]}"
            )
            continue

        valid = True
        for prog_id, prog_data in event_dict.items():
            if prog_data["event_date"] < start_date or prog_data["event_date"] > end_date:
                print(f"{prog_id} - {prog_data['prog_name']} - {prog_data['prog_distance_category']} - "
                      f"{len(prog_data['results'])} results ({prog_data['event_title']})")
                print(f"\tskipped because date ({prog_data['event_date']}) not in range [{start_date}, {end_date}]")
                valid = False
                update_log_file(
                    category="ignored",
                    event_id=prog_data["event_id"],
                    event_title=prog_data["event_title"],
                    event_listing=prog_data["event_listing"],
                    txt=f"date ({prog_data['event_date']}) not in range [{start_date}, {end_date}] for {prog_data['prog_name']}"
                )
        if not valid:
            continue

        valid = True
        for prog_id, prog_data in event_dict.items():
            if prog_data["prog_notes"] is not None:
                if any(substring in prog_data["prog_notes"].lower() for substring in [
                    "race was modified to a",
                    "race modified  to",
                    "swim was shortened",
                    "swim distance was reduced from 1500 m to 750m"  # Cape Town 2015
                ]):
                    print(f"\tskipping {prog_data['prog_name']}:\n###\n{prog_data['prog_notes']}\n###\n")
                    valid = False
                    prog_notes = prog_data['prog_notes'].replace('\n', '\n\t\t')
                    update_log_file(
                        category="ignored",
                        event_id=prog_data["event_id"],
                        event_title=prog_data["event_title"],
                        event_listing=prog_data["event_listing"],
                        txt=f"prog_notes for {prog_data['prog_name']}: {prog_notes}"
                    )
        if not valid:
            continue

        events_result = {}
        prog_ids = list(event_dict.keys())

        # check that all dicts in event_dict have same values for the keys [event_venue, event_date]
        for shared_key in ["event_id", "event_title", "event_venue", "event_listing", "event_country_noc"]:
            if len(set([d[shared_key] for d in event_dict.values()])) != 1:
                raise ValueError(f"{event_dict.values() = }")
            events_result[shared_key] = event_dict[prog_ids[0]][shared_key]
            if shared_key == "event_venue":
                # remove space as last char, if the case
                events_result[shared_key] = events_result[shared_key].rstrip()

        program_name_cat = "Elite"  # todo: implement U23 and Junior
        for prog_id, prog_data in event_dict.items():
            if prog_data["prog_name"] == f"{program_name_cat} Men":
                suffix = "_m"
            elif prog_data["prog_name"] == f"{program_name_cat} Women":
                suffix = "_w"
            else:
                raise NotImplemented(f"{prog_data['prog_name'] = }. Only supporting '{program_name_cat}'.")

            if prog_data["prog_distance_category"] not in distance_categories:
                print(f"prog_distance_category '{prog_data['prog_distance_category']}' not in {distance_categories = }")
                update_log_file(
                    category="ignored",
                    event_id=prog_data["event_id"],
                    event_title=prog_data["event_title"],
                    event_listing=prog_data["event_listing"],
                    txt=f"prog_distance_category for {prog_data['prog_name']}: '{prog_data['prog_distance_category']}' not in {distance_categories = }"
                )
                events_result["invalid"] = True
                continue

            print(f"{prog_id} - {prog_data['prog_name']} - {prog_data['prog_distance_category']} - "
                  f"{len(prog_data['results'])} results ({prog_data['event_title']})")
            events_result[f"event_date{suffix}"] = prog_data["event_date"]
            events_result[f"prog_distance_category{suffix}"] = prog_data["prog_distance_category"]
            events_result[f"prog_notes{suffix}"] = prog_data["prog_notes"] if prog_data[
                                                                                  "prog_notes"] is not None else ""
            events_result[f"event_category_ids{suffix}"] = [e['cat_id'] for e in prog_data["event_categories"]]
            if not set(events_result[f"event_category_ids{suffix}"]).intersection(set(category_ids.keys())):
                print(f"\tevent_category_ids {events_result[f'event_category_ids{suffix}']} not in {list(category_ids.keys())}")
                update_log_file(
                    category="ignored",
                    event_id=prog_data["event_id"],
                    event_title=prog_data["event_title"],
                    event_listing=prog_data["event_listing"],
                    txt=f"event_category_ids for {prog_data['prog_name']}: {events_result[f'event_category_ids{suffix}']} not in {category_ids.keys()}"
                )
                events_result["invalid"] = True
                continue

            expected_distances = events_config["expected_distances"]
            if prog_data["headers"] is not None:
                if len(prog_data["headers"]):
                    for i_distance, i_header in enumerate([0, 2, 4]):
                        if "distance" in prog_data["headers"][i_header]:
                            distance = prog_data["headers"][i_header]["distance"]
                            print(f"\t\t{distance = } {prog_data['prog_distance_category'] = }")
                            if prog_data['prog_distance_category'] in expected_distances:
                                d_min, d_max = expected_distances[prog_data['prog_distance_category']][i_distance]
                                is_distance_correct = d_min <= distance <= d_max
                                if not is_distance_correct:
                                    print(f"\t\t\t{distance = } not in {d_min = }, {d_max = }")
                                    events_result["invalid"] = True
                                    update_log_file(
                                        category="ignored",
                                        event_id=prog_data["event_id"],
                                        event_title=prog_data["event_title"],
                                        event_listing=prog_data["event_listing"],
                                        txt=f"distance #{i_distance} for {prog_data['prog_name']}: `{distance}` not in {d_min = }, {d_max = }"
                                    )
                                    break
                    if "invalid" in events_result:
                        break

            level = get_level(prog_data=prog_data)
            events_result[f"level{suffix}"] = level

            df_results = get_prog_results_df(prog_data=prog_data)
            n_results = len(df_results)
            if n_results < n_results_min:
                print(f"\t\tSkipping - only {n_results} results")
                events_result["invalid"] = True
                update_log_file(
                    category="ignored",
                    event_id=prog_data["event_id"],
                    event_title=prog_data["event_title"],
                    event_listing=prog_data["event_listing"],
                    txt=f"only {n_results = } for {prog_data['prog_name']}"
                )
                break

            if use_best_in_each_sport:
                for column in df_results.columns:
                    if column == "age":
                        continue
                    column_results = df_results[column]
                    # drop all value=0 in column_results
                    len_before = len(column_results)
                    column_results = column_results[column_results != 0]
                    len_after = len(column_results)
                    if len_before - len_after > 0:
                        print(f"dropped {len_before - len_after} values for column {column}. Remaining: {len_after}")
                    if len(column_results) < n_results_min:
                        print(f"\t\tSkipping - only {len(column_results)} results for {column}")
                        if column in [f"{s}_s" for s in sports]:  # ignore missing t1 and t2
                            events_result["invalid"] = True
                            update_log_file(
                                category="ignored",
                                event_id=prog_data["event_id"],
                                event_title=prog_data["event_title"],
                                event_listing=prog_data["event_listing"],
                                txt=f"only {len(column_results) = } for {prog_data['prog_name']} for {column}"
                            )
                            break
                    times = np.array(sorted(list(column_results))[i_first:i_last])
                    if column in [f"{s}_s" for s in sports]:
                        assert times[0] > 1, times
                    events_result[f"{column.replace('_s', '')}_mean{suffix}"] = times.mean() if len(times) > 0 else 0
                    events_result[f"{column.replace('_s', '')}_std{suffix}"] = times.std() if len(times) > 0 else 0
                    events_result[f"{column.replace('_s', '')}_all{suffix}"] = column_results.to_list()

                    times_last = np.array(sorted(list(column_results))[-i_last: -i_first if i_first > 0 else None]) if len(column_results) > 0 else np.array([])
                    # times_last = np.array(sorted(list(column_results))[19: 24])
                    if column in [f"{s}_s" for s in sports]:
                        assert times_last[0] > 1, times_last
                    events_result[f"{column.replace('_s', '')}_mean{suffix}_last"] = times_last.mean() if len(times_last) > 0 else 0
                    events_result[f"{column.replace('_s', '')}_std{suffix}_last"] = times_last.std() if len(times_last) > 0 else 0

                    # first_advance = events_result[f"{column.replace('_s', '')}_mean{suffix}_last"] - events_result[
                    #     f"{column.replace('_s', '')}_mean{suffix}"]
                    # if column in [f"{s}_s" for s in sports]:
                    #     assert first_advance > 0, f"{events_result['event_title']}: {first_advance}"
                if "invalid" in events_result:
                    break

                df_age = df_results["age"].iloc[i_first:i_last]
                if df_age.isnull().values.any():
                    # usually happens for games (olympics, commonwealth, etc.)
                    n_null = df_age.isnull().values.sum()
                    print(f"\t\tAge: {n_null} null values for event {prog_data['event_title']}:\n{df_age}")
                age_mean_std = df_age.agg(["mean", "std"])
                for k, v in age_mean_std.items():
                    events_result[f"age_{k.replace('_s', '')}{suffix}"] = v
            else:
                df_results = df_results.iloc[i_first:i_last]
                # compute the mean for each column
                mean_std = df_results.agg(["mean", "std"])
                for k, v in mean_std.items():
                    for _k, _v in dict(v).items():
                        events_result[f"{k.replace('_s', '')}_{_k}{suffix}"] = _v
            df_results["start_to_t2_s"] = df_results["swim_s"] + df_results["t1_s"] + df_results["bike_s"]

            events_result[f"n_finishers{suffix}"] = len(df_results)

            time_max_s = min(df_results["start_to_t2_s"]) + pack_duration_s
            events_result[f"pack_size{suffix}"] = int((df_results["start_to_t2_s"] <= time_max_s).sum())
            events_result[f"is_winner_in_front_pack{suffix}"] = df_results["start_to_t2_s"].iloc[0] <= time_max_s
            id_best_runner = df_results.run_s.idxmin()
            events_result[f"is_best_runner_in_front_pack{suffix}"] = df_results["start_to_t2_s"].iloc[
                                                                         id_best_runner] <= time_max_s
            # print(f"\tpack_size{suffix} = {events_result[f'pack_size{suffix}']}. Winner in: {events_result[f'is_winner_in_front_pack{suffix}']}")

            df_results["total_s"] = df_results["swim_s"] + df_results["t1_s"] + df_results["bike_s"] + df_results[
                "t2_s"] + df_results["run_s"]

            # get name of best runner
            id_best_runner = df_results.run_s.idxmin()
            id_winner = df_results.total_s.idxmin()
            events_result[f"best_runner_wins{suffix}"] = id_best_runner == id_winner

            if prog_data["results"][0]["total_time"] is not None:
                def str_to_seconds(x):
                    h, m, s = x.split(":")
                    return int(h) * 3600 + int(m) * 60 + int(s)

                df_tmp = pd.DataFrame(prog_data["results"])
                # drop rows with postion in ["DNF", "DNS", "DSQ", "LAP"]
                df_tmp = df_tmp[~df_tmp["position"].isin(["DNF", "DNS", "DSQ", "LAP"])]
                # drop rows with total time in ["DNF", "DNS", "DSQ", "LAP"]
                df_tmp = df_tmp[~df_tmp["total_time"].isin(["DNF", "DNS", "DSQ", "LAP"])]

                # set position as int
                df_tmp["position"] = df_tmp["position"].astype(int)
                # sort by position
                df_tmp.sort_values("position", inplace=True)

                assert df_tmp["position"].iloc[0] == 1
                assert df_tmp["position"].iloc[1] == 2

                first_s = str_to_seconds(df_tmp["total_time"].iloc[0])
                second_s = str_to_seconds(df_tmp["total_time"].iloc[1])
                events_result[f"second_delay{suffix}"] = int(second_s - first_s)
            else:
                print("\tno total time")
                events_result[f"second_delay{suffix}"] = df_results["total_s"].iloc[1] - df_results["total_s"].iloc[0]

            events_result[f"winner{suffix}"] = prog_data["results"][0]["athlete_title"]
            events_result[f"winner_country{suffix}"] = prog_data["results"][0]["athlete_noc"]
            events_result[f"second{suffix}"] = prog_data["results"][1]["athlete_title"]
            events_result[f"second_country{suffix}"] = prog_data["results"][1]["athlete_noc"]

            assert "invalid" not in events_result
            if "invalid" not in events_result:
                air_temperature, water_temperature, wetsuit = extract_air_water_and_wetsuit(
                    prog_id=prog_id,
                    prog_data=prog_data,
                    label_manually=label_manually,
                    suffix=suffix
                )
                events_result[f"air_temperature{suffix}"] = air_temperature
                events_result[f"water_temperature{suffix}"] = water_temperature
                events_result[f"wetsuit{suffix}"] = wetsuit

        if "invalid" in events_result:
            continue

        events_results.append(events_result)

    # assert that the dicts of events_results have all same length, and same keys
    if len(events_results) > 1:
        keys = events_results[0].keys()
        for events_result in events_results[1:]:
            assert events_result.keys() == keys, f"{events_result.keys()} != {keys}"

    df = pd.DataFrame(events_results)

    df = df.dropna(subset=['swim_mean_m', 'bike_mean_m', 'run_mean_m'])
    df.reset_index(drop=True, inplace=True)

    none_wetsuit_m = df[df['wetsuit_m'].isnull()]
    n_none_wetsuit_m = len(none_wetsuit_m)
    print(f"{n_none_wetsuit_m}/{len(df)} = {n_none_wetsuit_m / len(df):.1%} rows have 'wetsuit_m' None:")
    for row in none_wetsuit_m.itertuples(index=False):  # index=False excludes the index column from the tuple
        print(f"- {row.event_id}: {row.event_title}\n\t{row.event_listing}")

    none_wetsuit_w = df[df['wetsuit_w'].isnull()]
    n_none_wetsuit_w = len(none_wetsuit_w)
    print(f"{n_none_wetsuit_w}/{len(df)} = {n_none_wetsuit_w / len(df):.1%} rows have 'wetsuit_w' None:")
    for row in none_wetsuit_w.itertuples(index=False):  # index=False excludes the index column from the tuple
        print(f"- {row.event_id}: {row.event_title}\n\t{row.event_listing}")

    # save df for faster access
    df.to_csv(str(tmp_results_file_path), index=False)

    log_data = json_load(log_file_path)
    assert len(df) == len(log_data['loaded']) - len(log_data['ignored']), f"missing logs of ignored: {len(log_data['loaded']) - len(log_data['ignored'])}"

    return df


def add_year_and_event_cat(df, event_category_mapping):
    def give_event_category(event_category_ids):
        # if len(event_category_ids) != 1:
        #     print(f"not an single event_cat: {event_category_ids}")
        assert isinstance(event_category_ids[0], int)
        return event_category_mapping[event_category_ids[0]]

    df["event_category"] = df["event_category_ids_m"].apply(give_event_category)

    df = df.sort_values("event_date_m")
    df["event_year"] = df["event_date_m"].apply(lambda x: x[:4]).astype(int)

    return df


def clean_results(df, min_duration_s: float, sports, distance_categories):
    print(f"###\nprocessing {len(df)} results\n###")

    # drop rows where prog_distance_category_m != prog_distance_category_w
    df_different_distance = df[df['prog_distance_category_m'] != df['prog_distance_category_w']]
    if len(df_different_distance) > 0:
        print(f"dropping {len(df_different_distance)} rows where prog_distance_category_m != prog_distance_category_w")
        for row in df_different_distance.itertuples(index=False):  # index=False excludes the index column from the tuple
            update_log_file(
                category="ignored",
                event_id=row.event_id,
                event_title=row.event_title,
                event_listing=row.event_listing,
                txt=f"{row.prog_distance_category_m = } != {row.prog_distance_category_w = }"
            )
    df = df[df['prog_distance_category_m'] == df['prog_distance_category_w']]
    df["prog_distance_category"] = df["prog_distance_category_m"]
    df = df.drop(["prog_distance_category_m", "prog_distance_category_w"], axis=1)

    # drop rows where wetsuit_m or wetsuit_w is none
    df_wetsuit_unknown = df[(df['wetsuit_m'].isna()) | (df['wetsuit_w'].isna())]
    if len(df_wetsuit_unknown) > 0:
        print(f"dropping {len(df_wetsuit_unknown)} rows where wetsuit is unknown")
        for row in df_wetsuit_unknown.itertuples(index=False):  # index=False excludes the index column from the tuple
            update_log_file(
                category="ignored",
                event_id=row.event_id,
                event_title=row.event_title,
                event_listing=row.event_listing,
                txt=f"wetsuit is unknown: {row.wetsuit_m = }, {row.wetsuit_m = }"
            )
    df = df[~((df['wetsuit_m'].isna()) | (df['wetsuit_w'].isna()))]

    min_dur = min_duration_s
    df_not_long_enough_m = df[(df['swim_mean_m'] < min_dur) | (df['bike_mean_m'] < min_dur) | (df['run_mean_m'] < min_dur)]
    df_not_long_enough_w = df[(df['swim_mean_w'] < min_dur) | (df['bike_mean_w'] < min_dur) | (df['run_mean_w'] < min_dur)]
    for row in df_not_long_enough_m.itertuples(index=False):  # index=False excludes the index column from the tuple
        update_log_file(
            category="ignored",
            event_id=row.event_id,
            event_title=row.event_title,
            event_listing=row.event_listing,
            txt=f"{row.swim_mean_m = } < {min_dur} or {row.bike_mean_m = } < {min_dur} or {row.run_mean_m = } < {min_dur}"
        )
    for row in df_not_long_enough_w.itertuples(index=False):  # index=False excludes the index column from the tuple
        update_log_file(
            category="ignored",
            event_id=row.event_id,
            event_title=row.event_title,
            event_listing=row.event_listing,
            txt=f"{row.swim_mean_w = } < {min_dur} or {row.bike_mean_w = } < {min_dur} or {row.run_mean_w = } < {min_dur}"
        )
    df = df[(df['swim_mean_m'] >= min_dur) & (df['bike_mean_m'] >= min_dur) & (df['run_mean_m'] >= min_dur)]
    df = df[(df['swim_mean_w'] >= min_dur) & (df['bike_mean_w'] >= min_dur) & (df['run_mean_w'] >= min_dur)]

    for sport in sports:
        df[f"{sport}_diff"] = df[f"{sport}_mean_w"] - df[f"{sport}_mean_m"]
    # look at rows where one of the diffs is negative
    df_negative_diff = df[(df['swim_diff'] < 0) | (df['bike_diff'] < 0) | (df['run_diff'] < 0)]
    for row in df_negative_diff.itertuples(index=False):  # index=False excludes the index column from the tuple
        update_log_file(
            category="ignored",
            event_id=row.event_id,
            event_title=row.event_title,
            event_listing=row.event_listing,
            txt=f"{row.swim_diff = :.2f} < 0 or {row.bike_diff = :.2f} < 0 or {row.run_diff = :.2f} < 0"
        )
    # todo: why some of these have negative diffs? something is wrong!
    df = df[(df['swim_diff'] >= 0) & (df['bike_diff'] >= 0) & (df['run_diff'] >= 0)]

    # drop prog_distance_category that are not in distance_categories
    df_not_in_dist_cat = df[~df['prog_distance_category'].isin(distance_categories)]
    for row in df_not_in_dist_cat.itertuples(index=False):  # index=False excludes the index column from the tuple
        update_log_file(
            category="ignored",
            event_id=row.event_id,
            event_title=row.event_title,
            event_listing=row.event_listing,
            txt=f"{row.prog_distance_category = } not in {distance_categories}"
        )
    df = df[df['prog_distance_category'].isin(distance_categories)]

    print(f"###\nprocessing {len(df)} results (after filter)\n###")
    return df


def compute_diff(df, sports, distance_categories, remove_extreme_diffs: bool, quantile_min: float, quantile_max: float):
    assert set(df.prog_distance_category.unique()) == set(distance_categories)

    for sport in sports:
        df[f"{sport}_diff"] = df[f"{sport}_mean_w"] - df[f"{sport}_mean_m"]
        df[f"{sport}_diff_percent"] = df[f"{sport}_diff"] / df[f"{sport}_mean_m"]

    if remove_extreme_diffs:  # todo: use this to estimate w/m wetsuit difference
        print(f"{len(df)} results (before quantile)")
        for sport in sports:
            df = df[df[f"{sport}_diff_percent"] > df[f"{sport}_diff_percent"].quantile(quantile_min)]
            df = df[df[f"{sport}_diff_percent"] < df[f"{sport}_diff_percent"].quantile(quantile_max)]
        print(f"{len(df)} results (after quantile)")

    return df


def drop_outliers(data, i_sport: int, sport_outliers: list):
    for _i_sport, event_id in sport_outliers:
        if i_sport == _i_sport:
            if event_id in data['event_id'].values:
                # event_row = data[data['event_id'] == event_id].iloc[0]
                # print(f"dropping {sports[_i_sport]} of {event_id}: {event_row['event_title']}")
                # sport_emoji = [":one_piece_swimsuit:", ":bike:", ":athletic_shoe:"]
                # print(f"dropping {sport_emoji[_i_sport]} of [{event_row['event_year']} {event_row['event_venue']} ( {country_emojis[event_row['event_country_noc']] if event_row['event_country_noc'] in country_emojis else event_row['event_country_noc']} )]({event_row['event_listing']}) ({event_row['prog_distance_category'].replace('standard', 'olympic')}).")
                data = data[data['event_id'] != event_id]
    return data


def get_events_df(events_config: dict = None):
    clean_up_log_file()
    clean_up_conditions_log_file()

    if events_config is None:
        config = load_config()
        events_config = config["events"]

    ###
    distance_categories = events_config["distance_categories"]
    sports = events_config["sports"]
    event_category_mapping = events_config["event_category_mapping"]

    remove_extreme_diffs = events_config["cleaning"]["remove_extreme_diffs"]
    quantile_min = events_config["cleaning"]["quantile_min"]
    quantile_max = events_config["cleaning"]["quantile_max"]

    min_duration_s = events_config["cleaning"]["min_duration_s"]
    ###

    save_race_results(events_config=events_config)

    df = get_events_results(events_config=events_config)
    # df = pd.read_csv(str(tmp_results_file_path))

    df = clean_results(df, min_duration_s=min_duration_s, sports=sports, distance_categories=distance_categories)
    df = compute_diff(df, sports=sports, distance_categories=distance_categories, remove_extreme_diffs=remove_extreme_diffs, quantile_min=quantile_min, quantile_max=quantile_max)
    df = add_year_and_event_cat(df, event_category_mapping=event_category_mapping)

    # sort df by date and reset index
    df = df.sort_values("event_date_m").reset_index(drop=True)

    for event_id in df['event_id'].tolist():
        update_log_file(category="returned", event_id=event_id)

    print_log_file()

    return df

if __name__ == '__main__':
    _df = get_events_df()
    print(f"{len(_df)} events in final df")
