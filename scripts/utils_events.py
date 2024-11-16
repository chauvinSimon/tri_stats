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
from utils_itu import get_request, get_athlete_info, category_mapping

tmp_results_file_path = ignored_dir / "tmp_results.csv"

# todo: is it the correct way to set the math fonts?
plt.rcParams["font.family"] = "monospace"  # todo: set in global config
plt.rcParams['mathtext.default'] = 'rm'
plt.rcParams['mathtext.fontset'] = 'cm'  # "stix


config = load_config()
events_config = config["events"]

distance_categories = events_config["distance_categories"]
sports = events_config["sports"]
program_names = events_config["program_names"]
specification_ids = events_config["specification_ids"]
category_ids = events_config["category_ids"]

sport_outliers = events_config["cleaning"]["sport_outliers"]

start_date = events_config["query"]["start_date"]
end_date = events_config["query"]["end_date"]
per_page = events_config["query"]["per_page"]

pack_duration_s = events_config["pack_duration_s"]

remove_extreme_diffs = events_config["cleaning"]["remove_extreme_diffs"]
quantile_min = events_config["cleaning"]["quantile_min"]
quantile_max = events_config["cleaning"]["quantile_max"]

min_duration_s = events_config["cleaning"]["min_duration_s"]
n_results_min = events_config["cleaning"]["n_results_min"]

all_distance_categories = events_config["all_distance_categories"]
label_manually = events_config["label_manually"]

i_first = events_config["mean_computation"]["i_first"]
i_last = events_config["mean_computation"]["i_last"]
use_best_in_each_sport = events_config["mean_computation"]["use_best_in_each_sport"]



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


def get_program_listings(event_id: int):
    suffix = f"events/{event_id}/programs"
    res_req = get_request(url_suffix=suffix)
    res = []
    if res_req is None:
        return res
    for r in res_req:
        if r["prog_name"] in program_names:
            res.append({"prog_id": r["prog_id"], "prog_name": r["prog_name"]})
    return res


def save_images(
        event_id: int,
        event_title: str = "",
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


def save_race_results():
    ignored_event_file = cache_dir / "events" / "ignored_events.json"
    ignored_event_file.parent.mkdir(parents=True, exist_ok=True)
    if ignored_event_file.exists():
        ignored_events = json_load(ignored_event_file)
    else:
        ignored_events = {}

    # if "66636" not in ignored_events.keys():
    #     ignored_events["66636"] = "2013 ITU World Triathlon Kitzbuehel"  # kitzbuehel 2023 (2.55k on run)

    events_query_file = cache_dir / "events" / "events_query.json"
    events_query_file.parent.mkdir(parents=True, exist_ok=True)
    if events_query_file.exists():
        events_queries = json_load(events_query_file)
    else:
        events_queries = {}

    for spec_id, spec_name in specification_ids:
        for cat_id, cat_name in category_ids.items():
            suffix = f"events?category_id={cat_id}&start_date={start_date}&end_date={end_date}"
            suffix += f"&per_page={per_page}"
            if suffix in events_queries.keys():
                res = events_queries[suffix]
            else:
                res = get_request(url_suffix=suffix)
                events_queries[suffix] = res
                json_dump(data=events_queries, p=events_query_file)

            print(
                f"\n### ### ###\n{spec_name = } ({spec_id = }), {cat_name = } ({cat_id = }): {len(res) = }\n### ### ###")
            assert len(res) < per_page, f"More than {per_page = } results! Increase per_page"
            for r in res:
                event_id = r["event_id"]
                event_title = r["event_title"]

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
                    continue

                listings = get_program_listings(event_id=event_id)
                if not listings:
                    print(f"\nERROR: no listing found for {event_title} ({event_id})\n")
                    ignored_events[event_id] = event_title
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
                    if not all(saving_dict[k] for k in required_keys):
                        print(f"\t\tERROR: skipping {event_title} ({event_id}):")
                        for k in required_keys:
                            if not saving_dict[k]:
                                print(f"\t\t\tno value for {k}: {saving_dict[k]}")
                        ignored_events[event_id] = event_title
                        json_dump(ignored_events, p=ignored_event_file)
                        continue

                    saving_dicts[listing['prog_id']] = saving_dict

                if saving_dicts:
                    json_dump(data=saving_dicts, p=saving_path)


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
        print(f"ERROR: {prog_gender} not in {gender_dict.keys()}")
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


def get_events_results() -> pd.DataFrame:
    print("\nget_events_results\n")

    events_dir = cache_dir / "events"
    events_results = []

    for event_file in events_dir.glob("*.json"):
        # todo: should consider only the events of the query, not all that are saved
        # ignore `events_query.json` and `ignored_events.json`
        if not event_file.stem.isnumeric():
            continue
        event_dict = json_load(event_file)
        if len(event_dict) < 2:
            print(f"{event_file.stem}\n\tnot enough data: {list(event_dict.keys())}")
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
        if not valid:
            continue

        events_result = {}
        prog_ids = list(event_dict.keys())

        # check that all dicts in event_dict have same values for the keys [event_venue, event_date]
        for shared_key in ["event_id", "event_title", "event_venue", "event_listing", "event_country_noc"]:
            if len(set([d[shared_key] for d in event_dict.values()])) != 1:
                raise ValueError(f"{event_dict.values() = }")
            events_result[shared_key] = event_dict[prog_ids[0]][shared_key]

        for prog_id, prog_data in event_dict.items():
            if prog_data["prog_name"] == "Elite Men":
                suffix = "_m"
            elif prog_data["prog_name"] == "Elite Women":
                suffix = "_w"
            else:
                raise ValueError(f"{prog_data['prog_name'] = }")

            if prog_data["prog_distance_category"] not in all_distance_categories:
                raise ValueError(f"{prog_data['prog_distance_category'] = } not in {all_distance_categories = }")

            print(f"{prog_id} - {prog_data['prog_name']} - {prog_data['prog_distance_category']} - "
                  f"{len(prog_data['results'])} results ({prog_data['event_title']})")
            events_result[f"event_date{suffix}"] = prog_data["event_date"]
            events_result[f"prog_distance_category{suffix}"] = prog_data["prog_distance_category"]
            events_result[f"prog_notes{suffix}"] = prog_data["prog_notes"] if prog_data[
                                                                                  "prog_notes"] is not None else ""
            events_result[f"event_category_ids{suffix}"] = [e['cat_id'] for e in prog_data["event_categories"]]
            assert [cat_id for cat_id in events_result[f"event_category_ids{suffix}"] if cat_id in category_ids]

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

            events_result[f"wetsuit{suffix}"] = None
            if prog_data["prog_notes"] is not None:
                if any(substring in prog_data["prog_notes"].lower() for substring in
                       ["wetsuits allowed", "wetsuit allowed", ". wetsuit swim."]):
                    events_result[f"wetsuit{suffix}"] = True
                elif "wetsuits not allowed" in prog_data["prog_notes"].lower():
                    events_result[f"wetsuit{suffix}"] = False

            if events_result[f"wetsuit{suffix}"] is None:
                # print(f"\tcannot determine wetsuit - {prog_data['event_title'] = }")
                if prog_data["prog_notes"] is not None:
                    if prog_data["prog_notes"]:
                        # print(prog_data["prog_notes"])
                        # find_substring_with_context(long_string=prog_data["prog_notes"], target_word="wetsuit")
                        # find_substring_with_context(long_string=prog_data["prog_notes"], target_word="temperature")
                        # find_substring_with_context(long_string=prog_data["prog_notes"], target_word="water")
                        _, water_temperature = extract_air_and_water_temperatures(prog_data["prog_notes"])
                        if water_temperature is not None:
                            # print(f"\t\twater_temperature found: {water_temperature}")
                            if water_temperature >= 20:
                                events_result[f"wetsuit{suffix}"] = False
                            else:
                                events_result[f"wetsuit{suffix}"] = True

            level = get_level(prog_data=prog_data)
            events_result[f"level{suffix}"] = level

            df_results = get_prog_results_df(prog_data=prog_data)
            n_results = len(df_results)
            if n_results < n_results_min:
                print(f"\t\tSkipping - only {n_results} results")
                events_result["invalid"] = True
                continue

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
                        print(f"\t\tSkipping - only {len(column_results)} results")
                        events_result["invalid"] = True
                        continue
                    times = np.array(sorted(list(column_results))[i_first:i_last])
                    if column in [f"{s}_s" for s in sports]:
                        assert times[0] > 1, times
                    events_result[f"{column.replace('_s', '')}_mean{suffix}"] = times.mean()
                    events_result[f"{column.replace('_s', '')}_std{suffix}"] = times.std()
                    events_result[f"{column.replace('_s', '')}_all{suffix}"] = column_results.to_list()

                    times_last = np.array(sorted(list(column_results))[-i_last: -i_first if i_first > 0 else None])
                    # times_last = np.array(sorted(list(column_results))[19: 24])
                    if column in [f"{s}_s" for s in sports]:
                        assert times_last[0] > 1, times_last
                    events_result[f"{column.replace('_s', '')}_mean{suffix}_last"] = times_last.mean()
                    events_result[f"{column.replace('_s', '')}_std{suffix}_last"] = times_last.std()

                    # first_advance = events_result[f"{column.replace('_s', '')}_mean{suffix}_last"] - events_result[
                    #     f"{column.replace('_s', '')}_mean{suffix}"]
                    # if column in [f"{s}_s" for s in sports]:
                    #     assert first_advance > 0, f"{events_result['event_title']}: {first_advance}"

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
            events_result[f"pack_size{suffix}"] = (df_results["start_to_t2_s"] <= time_max_s).sum()
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

            # extract temperatures
            air_temperature, water_temperature = extract_air_and_water_temperatures(prog_data["prog_notes"])
            events_result[f"air_temperature{suffix}"] = air_temperature
            events_result[f"water_temperature{suffix}"] = water_temperature

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
                events_result[f"second_delay{suffix}"] = second_s - first_s
            else:
                print("\tno total time")
                events_result[f"second_delay{suffix}"] = df_results["total_s"].iloc[1] - df_results["total_s"].iloc[0]

            events_result[f"winner{suffix}"] = prog_data["results"][0]["athlete_title"]
            events_result[f"winner_country{suffix}"] = prog_data["results"][0]["athlete_noc"]
            events_result[f"second{suffix}"] = prog_data["results"][1]["athlete_title"]
            events_result[f"second_country{suffix}"] = prog_data["results"][1]["athlete_noc"]

            if "invalid" not in events_result:
                if events_result[f"wetsuit{suffix}"] is None:
                    manual_labelled_wetsuit_file = data_dir / "manual_labelled_wetsuit.json"
                    if manual_labelled_wetsuit_file.exists():
                        manual_labelled_wetsuit = json_load(manual_labelled_wetsuit_file)
                    else:
                        manual_labelled_wetsuit = {}

                    wetsuit_key = f'{prog_data["event_id"]}{suffix}'
                    if wetsuit_key in manual_labelled_wetsuit:
                        events_result[f"wetsuit{suffix}"] = manual_labelled_wetsuit[wetsuit_key]
                    else:
                        print(f"unknown wetsuit: {wetsuit_key}")
                        save_images(
                            event_id=prog_data["event_id"],
                            event_title=prog_data["event_title"],
                        )

                        if label_manually:
                            images_dir = cache_dir / "images" / str(prog_data["event_id"])

                            # glob png and jpg and jpeg
                            image_paths = list(images_dir.glob("*.[jpJP][npNP][egEG]*"))
                            if len(image_paths) == 0:
                                print(f"no images for manual wetsuit label: {wetsuit_key}")
                                continue
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
                            response = input(f"wetsuit for {suffix}? (y/n/?)")
                            if response == "y":
                                events_result[f"wetsuit{suffix}"] = True
                            elif response == "n":
                                events_result[f"wetsuit{suffix}"] = False
                            else:
                                events_result[f"wetsuit{suffix}"] = None

                            manual_labelled_wetsuit[wetsuit_key] = events_result[f"wetsuit{suffix}"]
                            json_dump(manual_labelled_wetsuit, manual_labelled_wetsuit_file)

        if "invalid" in events_result:
            continue

        events_results.append(events_result)

    df = pd.DataFrame(events_results)

    df = df.dropna(subset=['swim_mean_m', 'bike_mean_m', 'run_mean_m'])
    df.reset_index(drop=True, inplace=True)

    n_none_wetsuit_m = (df['wetsuit_m'].isnull()).sum()
    print(f"{n_none_wetsuit_m}/{len(df)} = {n_none_wetsuit_m / len(df):.0%} rows have 'wetsuit_m' None")
    n_none_wetsuit_w = (df['wetsuit_w'].isnull()).sum()
    print(f"{n_none_wetsuit_w}/{len(df)} = {n_none_wetsuit_w / len(df):.0%} rows have 'wetsuit_w' None")

    # save df for faster access
    df.to_csv(str(tmp_results_file_path), index=False)

    return df


def add_year_and_event_cat(df):
    def give_event_category(event_category_ids):
        assert isinstance(event_category_ids[0], int)
        return category_mapping[event_category_ids[0]]

    df["event_category"] = df["event_category_ids_m"].apply(give_event_category)

    df = df.sort_values("event_date_m")
    df["event_year"] = df["event_date_m"].apply(lambda x: x[:4]).astype(int)

    return df


def clean_results(df):
    print(f"###\nprocessing {len(df)} results\n###")

    # drop rows where prog_distance_category_m != prog_distance_category_w
    # df_different_distance = df[df['prog_distance_category_m'] != df['prog_distance_category_w']]
    df = df[df['prog_distance_category_m'] == df['prog_distance_category_w']]
    df["prog_distance_category"] = df["prog_distance_category_m"]
    # drop prog_distance_category_m and prog_distance_category_w columns
    df = df.drop(["prog_distance_category_m", "prog_distance_category_w"], axis=1)

    min_dur = min_duration_s
    # df_not_long_enough_m = df[(df['swim_mean_m'] < min_dur) | (df['bike_mean_m'] < min_dur) | (df['run_mean_m'] < min_dur)]
    # df_not_long_enough_w = df[(df['swim_mean_w'] < min_dur) | (df['bike_mean_w'] < min_dur) | (df['run_mean_w'] < min_dur)]
    df = df[(df['swim_mean_m'] > min_dur) & (df['bike_mean_m'] > min_dur) & (df['run_mean_m'] > min_dur)]
    df = df[(df['swim_mean_w'] > min_dur) & (df['bike_mean_w'] > min_dur) & (df['run_mean_w'] > min_dur)]

    for sport in sports:
        df[f"{sport}_diff"] = df[f"{sport}_mean_w"] - df[f"{sport}_mean_m"]
    # look at rows where one of the diffs is negative
    # df_negative_diff = df[(df['swim_diff'] < 0) | (df['bike_diff'] < 0) | (df['run_diff'] < 0)]
    # todo: why some of these have negative diffs?
    df = df[(df['swim_diff'] > 0) & (df['bike_diff'] > 0) & (df['run_diff'] > 0)]

    # drop prog_distance_category that are not in distance_categories
    df = df[df['prog_distance_category'].isin(distance_categories)]

    print(f"###\nprocessing {len(df)} results (after filter)\n###")
    return df


def compute_diff(df):
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


def drop_outliers(data, i_sport: int):
    for _i_sport, event_id in sport_outliers:
        if i_sport == _i_sport:
            if event_id in data['event_id'].values:
                # event_row = data[data['event_id'] == event_id].iloc[0]
                # print(f"dropping {sports[_i_sport]} of {event_id}: {event_row['event_title']}")
                # sport_emoji = [":one_piece_swimsuit:", ":bike:", ":athletic_shoe:"]
                # print(f"dropping {sport_emoji[_i_sport]} of [{event_row['event_year']} {event_row['event_venue']} ( {country_emojis[event_row['event_country_noc']] if event_row['event_country_noc'] in country_emojis else event_row['event_country_noc']} )]({event_row['event_listing']}) ({event_row['prog_distance_category'].replace('standard', 'olympic')}).")
                data = data[data['event_id'] != event_id]
    return data

def get_events_df():
    save_race_results()

    df = get_events_results()
    # df = pd.read_csv(str(tmp_results_file_path))

    df = clean_results(df)
    df = compute_diff(df)
    df = add_year_and_event_cat(df)

    # sort df by date and reset index
    df = df.sort_values("event_date_m").reset_index(drop=True)

    return df

if __name__ == '__main__':
    _df = get_events_df()
    print(_df)