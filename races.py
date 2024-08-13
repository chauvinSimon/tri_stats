"""

"""

from datetime import datetime
from pathlib import Path

import cv2
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd
import re

import requests
from PIL import Image
from io import BytesIO

from utils import json_dump, data_dir, json_load, res_dir, country_emojis, add_watermark
from utils_itu import get_request

# todo: is it the correct way to set the math fonts?
plt.rcParams["font.family"] = "monospace"  # todo: set in global config
plt.rcParams['mathtext.default'] = 'rm'
plt.rcParams['mathtext.fontset'] = 'cm'  # "stix


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


# get_events_categories()
category_ids = {
    # 483: "Age-Group Event",
    # 612: "Arena Games Finals",
    # 610: "Arena Games Series",
    # 340: "Continental Championships",
    # 341: "Continental Cup",
    # 342: "Continental Junior Cup",
    # 623: "Continental Para Cup",
    # 477: "Development Regional Cup",
    343: "Major Games",
    # 344: "Multisport Series",
    # 352: "Qualification Event",
    345: "Recognised Event",
    346: "Recognised Games",
    # 347: "Regional Championships",
    # 640: "T100 Triathlon World Tour",
    624: "World Championship Finals",
    351: "World Championship Series",
    # 348: "World Championships",
    349: "World Cup",
    # 631: "World Indoor Cup",
    # 449: "World Para Cup",
    # 448: "World Para Series",
    # 350: "World Paratriathlon Event",
}

# get_events_specifications()
specification_ids = [
    # (453, "Aquabike"),
    # (353, "Aquathlon"),
    # (408, "Cross Duathlon"),
    # (354, "Cross Triathlon"),
    # (355, "Duathlon"),
    # (356, "Long Distance Triathlon"),
    (357, "Triathlon"),
    # (595, "Winter Duathlon"),
    # (358, "Winter Triathlon"),
]


def get_program_listings(event_id: int, program_names):
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
        per_page: int = 1000
):
    images_dir = data_dir / "images"
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


program_names = [
    "Elite Men",
    "Elite Women",
]

sports = [
    "swim",
    # "t1",
    "bike",
    # "t2",
    "run"
]

distance_categories = [
    "sprint",
    "standard"
]


def save_race_results():
    start_date = "2009-01-01"
    end_date = "2024-07-31"  # todo: today
    per_page = 1000

    ignored_event_file = data_dir / "events" / "ignored_events.json"
    ignored_event_file.parent.mkdir(parents=True, exist_ok=True)
    if ignored_event_file.exists():
        ignored_events = json_load(ignored_event_file)
    else:
        ignored_events = {}

    # if "66636" not in ignored_events.keys():
    #     ignored_events["66636"] = "2013 ITU World Triathlon Kitzbuehel"  # kitzbuehel 2023 (2.55k on run)

    events_query_file = data_dir / "events" / "events_query.json"
    events_query_file.parent.mkdir(parents=True, exist_ok=True)
    if events_query_file.exists():
        events_queries = json_load(events_query_file)
    else:
        events_queries = {}

    for spec_id, spec_name in specification_ids:
        for cat_id, cat_name in category_ids.items():
            suffix = f"events?category_id={cat_id}&start_date={start_date}&end_date={end_date}"
            suffix += f"&per_page={spec_id}"
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

                saving_path = data_dir / "events" / f"{event_id}.json"
                if saving_path.exists():
                    print(f"\t{event_title} ({event_id}) already processed")
                    continue

                if str(event_id) in ignored_events:
                    print(f"\t{event_title} ({event_id}) already ignored")
                    continue

                res_specification_ids = [s["cat_id"] for s in r["event_specifications"]]
                if spec_id not in res_specification_ids:
                    continue

                listings = get_program_listings(
                    event_id=event_id,
                    program_names=program_names
                )
                if not listings:
                    print("\t\tno listing found")
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
                    event_categories = saving_dict["event_categories"]
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
                        print(f"\t\tERROR: skipping {saving_dict}")
                        for k in required_keys:
                            print(f"\t\t\t{k}: {saving_dict[k]}")
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
        if ("dob" not in r) or (r["dob"] is None):
            di["age"] = None
        else:
            di["age"] = compute_age_with_decimals(date_of_birth=r["dob"], specific_date=prog_data["event_date"])
            assert abs(prog_year - int(r["athlete_yob"]) - di["age"]) < 2
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


def extract_water_temperature(long_string):
    # Define a regular expression pattern to match the water temperature
    pattern = r"water temperature[:\s]*([\d.]+)"

    # Search for the pattern in the string
    match = re.search(pattern, long_string.lower())

    if match:
        # Extract the temperature value from the match
        temperature_str = match.group(1)
        if temperature_str[-1] == ".":
            temperature_str = temperature_str[:-1]
        # Convert the extracted value to float
        temperature = float(temperature_str)

        return temperature
    else:
        if ("temp" in long_string.lower()) or ("water" in long_string.lower()):
            raise ValueError(
                f"maybe regex {pattern} is not good enough to extract water temperature from {long_string}")
        return None


def get_events_results() -> pd.DataFrame:
    print("\nget_events_results\n")

    # todo: these params are important and should be set outside
    n_results_min = 25
    i_first = 5
    i_last = 10  # excluded
    use_best_in_each_sport = True
    # use_best_in_each_sport = False

    # label_manually = False
    label_manually = True

    all_distance_categories = [
        "standard",
        "sprint",
        "super_sprint",
    ]

    events_dir = data_dir / "events"
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

            expected_distances = {
                "sprint": [
                    (700, 800),
                    (18, 23),
                    (4.5, 5.5)
                ],
                "standard": [
                    (1400, 1600),
                    (36, 44),
                    (9, 11)
                ]
            }
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
                        water_temperature = extract_water_temperature(prog_data["prog_notes"])
                        if water_temperature is not None:
                            # print(f"\t\twater_temperature found: {water_temperature}")
                            if water_temperature >= 20:
                                events_result[f"wetsuit{suffix}"] = False
                            else:
                                events_result[f"wetsuit{suffix}"] = True

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

                    times_last = np.array(sorted(list(column_results))[-i_last: -i_first])
                    # times_last = np.array(sorted(list(column_results))[20: 25])
                    if column in [f"{s}_s" for s in sports]:
                        assert times_last[0] > 1, times_last
                    events_result[f"{column.replace('_s', '')}_mean{suffix}_last"] = times_last.mean()
                    events_result[f"{column.replace('_s', '')}_std{suffix}_last"] = times_last.std()

                    first_advance = events_result[f"{column.replace('_s', '')}_mean{suffix}_last"] - events_result[
                        f"{column.replace('_s', '')}_mean{suffix}"]
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

            pack_duration_s = 10
            time_max_s = min(df_results["start_to_t2_s"]) + pack_duration_s
            events_result[f"pack_size{suffix}"] = (df_results["start_to_t2_s"] <= time_max_s).sum()
            events_result[f"is_winner_in_front_pack{suffix}"] = df_results["start_to_t2_s"].iloc[0] <= time_max_s
            id_best_runner = df_results.run_s.idxmin()
            events_result[f"is_best_runner_in_front_pack{suffix}"] = df_results["start_to_t2_s"].iloc[
                                                                         id_best_runner] <= time_max_s
            # print(f"\tpack_size{suffix} = {events_result[f'pack_size{suffix}']}. Winner in: {events_result[f'is_winner_in_front_pack{suffix}']}")

            df_results["total_s"] = df_results["swim_s"] + df_results["t1_s"] + df_results["bike_s"] + df_results[
                "t2_s"] + df_results["run_s"]
            sprint_finish_s = 3

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
                            images_dir = data_dir / "images" / str(prog_data["event_id"])

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
    df.to_csv("tmp_results.csv", index=False)

    return df


def add_year_and_event_cat(df):
    def give_event_category(event_category_ids):
        category_mapping = {
            343: "games",  # "Major Games",
            345: "games",  # "Recognised Event",
            346: "games",  # "Recognised Games",
            624: "wcs",  # "World Championship Finals",
            351: "wcs",  # "World Championship Series",
            349: "world-cup",  # "World Cup",
        }
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

    min_dur = 3 * 60  # todo: params
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
    remove_extreme_diffs = False

    assert set(df.prog_distance_category.unique()) == set(distance_categories)

    for sport in sports:
        df[f"{sport}_diff"] = df[f"{sport}_mean_w"] - df[f"{sport}_mean_m"]
        df[f"{sport}_diff_percent"] = df[f"{sport}_diff"] / df[f"{sport}_mean_m"]

    if remove_extreme_diffs:  # todo: use this to estimate w/m wetsuit difference
        quantile_min = 0.1
        quantile_max = 0.9
        print(f"{len(df)} results (before quantile)")
        for sport in sports:
            df = df[df[f"{sport}_diff_percent"] > df[f"{sport}_diff_percent"].quantile(quantile_min)]
            df = df[df[f"{sport}_diff_percent"] < df[f"{sport}_diff_percent"].quantile(quantile_max)]
        print(f"{len(df)} results (after quantile)")

    return df


def process_results_wetsuit(df):
    # remove outliers?
    outliers = df[df["swim_diff_percent"] >= 0.22]
    print(f"{len(outliers)} swim outliers:")
    print(list(outliers["event_listing"]))
    print(list(outliers["event_title"]))
    print(outliers["swim_diff_percent"])
    df = df[df["swim_diff_percent"] < 0.22]

    print("\n\n\n")
    df_same_wetsuit = df[df['wetsuit_m'] == df['wetsuit_w']]
    df_same_wetsuit = df_same_wetsuit[df_same_wetsuit['wetsuit_m'].notna()]
    df_same_wetsuit = df_same_wetsuit[df_same_wetsuit['wetsuit_w'].notna()]
    print(f"###\n{len(df_same_wetsuit)} same wetsuit combinations (not None):"
          f"\n{df_same_wetsuit['wetsuit_m'].value_counts()}\n###\n")

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 16))

    data_all = df_same_wetsuit["swim_diff_percent"]
    wm_percent = data_all.mean()
    wm_percent_std = data_all.std()

    formatted_formula = f"$wm\\_percent = {wm_percent * 100:.1f}\\%$\n$(std = {wm_percent_std * 100:.1f}\\%)$"
    fig.suptitle(
        f"The DIFFERENCE in SWIM time WOMEN/MEN (in %) is ~independent of WETSUIT and DISTANCE:"
        f"\n{formatted_formula}",
        fontsize=20
    )

    rows_names = []
    for i_wet, use_wetsuit in enumerate([False, True]):

        if use_wetsuit:
            swim_diff_percents = df_same_wetsuit[df_same_wetsuit['wetsuit_m']]["swim_diff_percent"]
        else:
            swim_diff_percents = df_same_wetsuit[~df_same_wetsuit['wetsuit_m'].astype(bool)]["swim_diff_percent"]
        wetsuit_mean = swim_diff_percents.mean()
        wetsuit_std = swim_diff_percents.std()
        name = "WITH wetsuit" if use_wetsuit else "WITHOUT wetsuit"
        rows_names.append(f"{name}\n{wetsuit_mean:.1%} ± {wetsuit_std:.1%} ({len(swim_diff_percents)})")

        for i_distance_category, distance_category in enumerate(distance_categories):
            axes[i_wet, i_distance_category].hist(
                data_all,
                bins="auto",
                density=True,
                alpha=0.5,
                label=f"all ({len(data_all)})",
                color="navy"
            )
            axes[i_wet, i_distance_category].axvline(
                wm_percent,
                color='navy',
                linestyle='--',
                linewidth=1,
                label=f"{wm_percent:.1%} ± {wm_percent_std:.1%}"
            )

            data = swim_diff_percents[df_same_wetsuit['prog_distance_category'] == distance_category]
            mean = data.mean()
            std = data.std()
            print(f"\t[{distance_category}] {mean:.1%} ± {std:.1%} ({len(data)})")
            axes[i_wet, i_distance_category].hist(
                data,
                bins="auto",
                density=True,
                alpha=0.5,
                label=f"{distance_category.upper()} {'WITH' if use_wetsuit else 'WITHOUT'} ({len(data)})",
                color="cyan",
                # edgecolor="black"
            )
            axes[i_wet, i_distance_category].axvline(
                mean,
                color='cyan',
                linestyle='--',
                linewidth=1,
                label=f"{mean:.1%} ± {std:.1%}"
            )

            axes[i_wet, i_distance_category].legend()
            axes[i_wet, i_distance_category].grid()
            axes[i_wet, i_distance_category].set_yticklabels([])

    cols_names = []
    for distance_category in distance_categories:
        data = df_same_wetsuit[df_same_wetsuit['prog_distance_category'] == distance_category]["swim_diff_percent"]
        mean = data.mean()
        std = data.std()
        cols_names.append(f"{distance_category.upper()}\n{mean:.1%} ± {std:.1%} ({len(data)})")
    for ax, col in zip(axes[0], cols_names):
        ax.set_title(col, fontsize=16)
    for ax, row in zip(axes[:, 0], rows_names):
        ax.set_ylabel(row, rotation=90, fontsize=16)

    plt.tight_layout()
    add_watermark(fig, y=0.94)
    plt.savefig(str(res_dir / "wm_swim.png"), dpi=300)
    # plt.savefig(str(res_dir / "wm_swim_20-24.png"), dpi=300)
    # plt.show()

    # conclusion: the difference in swim (in %) is independent of wetsuit and distance

    df_different_wetsuit = df[df['wetsuit_m'] != df['wetsuit_w']]
    df_different_wetsuit = df_different_wetsuit[df_different_wetsuit['wetsuit_m'].notna()]
    df_different_wetsuit = df_different_wetsuit[df_different_wetsuit['wetsuit_w'].notna()]
    print(f"###\n{len(df_different_wetsuit)} different wetsuit combinations\n###")

    swim_diff_percent_women_fast = df_different_wetsuit[df_different_wetsuit['wetsuit_w']]
    swim_diff_percent_women_slow = df_different_wetsuit[~df_different_wetsuit['wetsuit_w'].astype(bool)]
    print(f"men with wetsuit, while women without wetsuit: {len(swim_diff_percent_women_fast)}:")
    for listing in list(swim_diff_percent_women_slow["event_listing"]):
        print(listing)

    # create markdown table
    df_table = swim_diff_percent_women_fast[
        ["event_year", "event_country_noc", "event_listing", "event_venue", "prog_distance_category",
         "swim_diff_percent", "event_category"]]
    # in prog_distance_category, change "standard" to "olympic"
    df_table["prog_distance_category"] = df_table["prog_distance_category"].apply(
        lambda x: x.replace("standard", "olympic"))
    # merge "event_country_noc" and "event_venue"
    df_table["event"] = df_table[["event_country_noc", "event_listing", "event_venue"]].apply(
        lambda
            x: f"[{x.event_venue}]({x.event_listing}) ( {country_emojis[x.event_country_noc] if x.event_country_noc in country_emojis else x.event_country_noc} )",
        axis=1
    )
    df_table.sort_values(["swim_diff_percent"], inplace=True)
    df_table["benefit"] = df_table["swim_diff_percent"].apply(lambda x: f"**{1 - (1 + x) / (1 + wm_percent):.1%}**")
    df_table = df_table[
        ["event_year", "event", "swim_diff_percent", "benefit", "prog_distance_category", "event_category"]]
    df_table["event_category"] = df_table["event_category"].apply(lambda x: x.replace("wcs", "WTCS").upper())
    df_table["swim_diff_percent"] = df_table["swim_diff_percent"].apply(lambda x: f"{x :.1%}")
    df_table.columns = ["YEAR", "EVENT", "DIFF (%) WOMEN-WITH vs MEN-without", "**BENEFIT (%)**", "DISTANCE", "EVENT CATEGORY"]
    print(df_table.to_markdown(
        index=False,
        colalign=["center"] * len(df_table.columns)
    ))

    # ? ignore World Cups
    swim_diff_percent_women_fast = swim_diff_percent_women_fast[
        swim_diff_percent_women_fast["event_category"] != "world-cup"]

    # remove Sydney outlier
    swim_diff_percent_women_fast = swim_diff_percent_women_fast[swim_diff_percent_women_fast["event_id"] != 54370]

    # # remove largest values of 'swim_diff_percent'
    # swim_diff_percent_women_fast = swim_diff_percent_women_fast[
    #     swim_diff_percent_women_fast['swim_diff_percent'] < swim_diff_percent_women_fast['swim_diff_percent'].max()]
    # swim_diff_percent_women_fast = swim_diff_percent_women_fast[
    #     swim_diff_percent_women_fast['swim_diff_percent'] > swim_diff_percent_women_fast['swim_diff_percent'].min()]

    print(f"###\nwomen fast: ({len(swim_diff_percent_women_fast)})")
    wm_percent_w_fast = swim_diff_percent_women_fast['swim_diff_percent'].mean()
    wm_percent_w_fast_std = swim_diff_percent_women_fast['swim_diff_percent'].std()
    print(f"\t{wm_percent_w_fast :.1%} ±{wm_percent_w_fast_std :.1%}")
    for per in sorted(list(swim_diff_percent_women_fast['swim_diff_percent'])):
        print(f"\t\t{per:.1%}")
    print("###")

    improve_percent = 1 - (1 + wm_percent_w_fast) / (1 + wm_percent)
    print(
        f"improve_percent = {improve_percent:.1%} from substitution ({wm_percent = :.1%}) ({wm_percent_w_fast = :.1%})")

    swim_diff_percent_women_fast = swim_diff_percent_women_fast.sort_values(by='swim_diff_percent')

    swim_diff_percents = swim_diff_percent_women_fast["swim_diff_percent"]
    swim_diff_percent_women_fast["name"] = swim_diff_percent_women_fast[
        ["event_date_m", "event_venue", "prog_distance_category", "swim_diff_percent"]].apply(
        lambda
            x: f"{x.event_venue.split(',')[0]} {x.event_date_m[:4]}\n{x.prog_distance_category.replace('standard', 'olympic')}\ndiff = {x.swim_diff_percent:.1%}\n=> benefit = {1 - (1 + x.swim_diff_percent) / (1 + wm_percent):.1%}",
        axis=1
    )
    names = swim_diff_percent_women_fast["name"]

    fig, ax = plt.subplots(figsize=(12, 9))

    y_max = wm_percent + 0.01
    ax.set_ylim(0, y_max)

    ax.axhline(
        wm_percent,
        color='dodgerblue',
        linestyle='-.',
        linewidth=2,
    )
    ax.text(
        0.92,
        wm_percent / y_max + 0.035,  # - 0.05,
        f"W vs M - same equipment\n{wm_percent:.1%} ± {wm_percent_std:.1%}\n(from {len(df_same_wetsuit)} events)",
        color='dodgerblue',
        transform=ax.transAxes,
        rotation=0,
        ha='center',
        va='center',
        fontsize=10
    )

    ax.axhline(
        wm_percent_w_fast,
        color='darkturquoise',
        linestyle='-.',
        linewidth=2,
    )
    ax.text(
        0.92,
        wm_percent_w_fast / y_max + 0.035,
        f"W(wetsuit) vs M(no)\n{wm_percent_w_fast:.1%} ± {wm_percent_w_fast_std:.1%}\n(from {len(swim_diff_percent_women_fast)} events)",
        color='darkturquoise',
        transform=ax.transAxes,
        rotation=0,
        ha='center',
        va='center',
        fontsize=10
    )

    major_ticks = np.arange(0, y_max, 0.01)
    ax.set_yticks(major_ticks)

    ax.bar(
        names,
        swim_diff_percents,
        color='darkturquoise',
        alpha=0.5,
        width=0.2,
        edgecolor='black',
        linewidth=0.5,
    )
    # set ax font size
    # for tick in ax.get_xticklabels():
    #     tick.set_fontsize(8)
    # for tick in ax.get_yticklabels():
    #     tick.set_fontsize(8)

    # Remove axes splines
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)

    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)

    ax.grid(
        color='grey',
        linestyle='-.',
        linewidth=0.5,
        alpha=0.7
    )

    # Add annotation to bars
    # for i in ax.patches:
    #     plt.text(
    #         i.get_width() + 0.002,
    #         i.get_y() + 0.4,
    #         f"{i.get_width():.1%}",
    #         fontsize=10,
    #         fontweight='bold',
    #         color='grey'
    #     )

    ax.invert_xaxis()

    vals = ax.get_yticks()
    ax.set_yticklabels(['{:,.1%}'.format(x) for x in vals])
    ax.set_ylabel("How much slower did women swim\ncompared to men (%)?", fontsize=12)

    wm_percent_w_fast_str = f"{100 * wm_percent_w_fast:.1f}\\%"
    wm_percent_str = f"{100 * wm_percent:.1f}\\%"
    improve_percent_str = f"{100 * improve_percent:.1f}\\%"
    ax.set_title(
        f'MEN without wetsuit swim FASTER than WOMEN with wetsuit, by ${wm_percent_w_fast_str}$'
        f'\nThe benefit from wetsuit can be derived: ${improve_percent_str}$'
        f'\n[ ${improve_percent_str} = 1 - (1 + {wm_percent_w_fast_str}) / (1 + {wm_percent_str})$ ]',
        # loc='left',
        fontsize=15
    )
    add_watermark(fig, y=0.9, x=0.12)
    plt.savefig(str(res_dir / "wetsuit.png"), dpi=300)
    # plt.savefig(str(res_dir / "wetsuit_20-24.png"), dpi=300)
    plt.show()

    # alternative method: compare times with wetsuit vs without

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 16))

    improve_percents = []

    for i_distance_category, distance_category in enumerate(distance_categories):
        x_max = max(
            df[df['prog_distance_category'] == distance_category][f"swim_mean_m"].max(),
            df[df['prog_distance_category'] == distance_category][f"swim_mean_w"].max()
        ) + 10

        x_min = min(
            df[df['prog_distance_category'] == distance_category][f"swim_mean_m"].min(),
            df[df['prog_distance_category'] == distance_category][f"swim_mean_w"].min()
        ) - 10

        for i_suffix, suffix in enumerate(["w", "m"]):
            colours = {
                "w": ("navy", "violet"),
                "m": ("navy", "cyan"),
            }
            df_ = df[(df[f'wetsuit_{suffix}'].notna()) & (df['prog_distance_category'] == distance_category)]
            wet = df_[df_[f'wetsuit_{suffix}']][f"swim_mean_{suffix}"]
            # no_wet = df_[~df_[f'wetsuit_{suffix}'].astype(bool)][f"swim_mean_{suffix}"]
            # removing Mooloolaba 2012
            no_wet_tmp = df_[(~df_[f'wetsuit_{suffix}'].astype(bool)) & (df_[f'event_id'] != 54303)]
            no_wet = no_wet_tmp[f"swim_mean_{suffix}"]
            print("slowest swim:")
            print(no_wet_tmp.sort_values(f"swim_mean_{suffix}")[["event_title", f"swim_mean_{suffix}"]].tail(5))

            axes[i_suffix, i_distance_category].hist(
                wet,
                bins="auto",
                density=True,
                alpha=0.5,
                label=f"wetsuit ({len(wet):,})",
                color=colours[suffix][0],
            )

            axes[i_suffix, i_distance_category].hist(
                no_wet,
                bins="auto",
                density=True,
                alpha=0.5,
                label=f"no wetsuit ({len(no_wet):,})",
                color=colours[suffix][1],
            )

            wet_mean = wet.mean()
            wet_std = wet.std()
            no_wet_mean = no_wet.mean()
            no_wet_std = no_wet.std()

            for i_, (mean, std, colour) in enumerate([(wet_mean, wet_std, 'r'), (no_wet_mean, no_wet_std, 'b')]):
                axes[i_suffix, i_distance_category].axvline(
                    mean,
                    color=colours[suffix][i_],
                    linestyle='-.',
                    linewidth=2,
                    # label=f"{str(datetime.timedelta(seconds=round(mean)))} ± {std:.0f}"
                    label=f"{seconds_to_h_min_sec(round(mean), use_hours=False, sport='swim', use_units=True)}\n± {std:.0f}"
                )
                # axes[i_suffix, i_distance_category].text(
                #     (x_max - mean) / (x_max - x_min) - 0.0015,
                #     0.7,
                #     f"{str(datetime.timedelta(seconds=round(mean)))} ± {std:.0f}",
                #     transform=axes[i_suffix, i_distance_category].transAxes,
                #     color=colours[suffix][i_],
                #     rotation=90,
                #     ha='center',
                #     va='center',
                #     fontsize=10
                # )

            print(f"{distance_category} ({suffix.upper()}) ({len(df_)})")
            print(f"\twet_mean    = {wet_mean:.0f} ±{wet_std:.0f} ({len(wet):,})")
            print(f"\tno_wet_mean = {no_wet_mean:.0f} ±{no_wet_std:.0f} ({len(no_wet):,})")
            improve_percent = (no_wet_mean - wet_mean) / no_wet_mean
            print(f"\timprove_percent = {improve_percent :.1%}")
            print(f"\t range wetsuit: {wet.min()} - {wet.max()} = {wet.max() - wet.min()}")
            print(f"\t range no wetsuit: {no_wet.min()} - {no_wet.max()} = {no_wet.max() - no_wet.min()}")
            improve_percents.append(improve_percent)
            print()

            axes[i_suffix, i_distance_category].legend()
            axes[i_suffix, i_distance_category].grid()
            axes[i_suffix, i_distance_category].set_xlim(x_min, x_max)

            locs = axes[i_suffix, i_distance_category].get_xticks()

            labels = map(
                lambda x: seconds_to_h_min_sec(x, use_hours=True, sport="swim", use_units=False).replace(" (", "\n("),
                locs)
            axes[i_suffix, i_distance_category].set_xticks(locs)
            axes[i_suffix, i_distance_category].set_xticklabels(labels)

    cols = [f"{cat} ({len(df[df.prog_distance_category == cat])})" for cat in distance_categories]
    rows = ["WOMEN", "MEN"]
    for ax, col in zip(axes[0], cols):
        ax.set_title(col.replace("standard", "olympic").upper(), fontsize=16)
    for ax, row in zip(axes[:, 0], rows):
        ax.set_ylabel(row, rotation=90, fontsize=16)

    for ax in axes.flat:
        ax.set_yticklabels([])

    formatted_estimates = ', '.join([f'${round(x * 100, 1)}\\% $' for x in sorted(improve_percents)])
    fig.suptitle(
        "SWIM WITH & WITHOUT WETSUIT\n---\n"
        "Naive approach to estimate the benefit of wetsuit: $improvement = (no\\_wet\\_mean - wet\\_mean) / no\\_wet\\_mean$"
        f"\nResults: {formatted_estimates}",
        fontsize=18
    )

    plt.tight_layout()
    add_watermark(fig)
    plt.savefig(str(res_dir / "wetsuit_2.png"), dpi=300)
    # plt.savefig(str(res_dir / "wetsuit_2_20-24.png"), dpi=300)

    plt.show()


def process_sports(df):
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(16, 16))

    fig.suptitle(
        f"TIMES AND PACES\n({len(df)} events)",
        fontsize=20
    )

    for i_distance_category, distance_category in enumerate(distance_categories):
        for i_sport, sport in enumerate(sports):

            x_max = max(
                df[df['prog_distance_category'] == distance_category][f"{sport}_mean_m"].max(),
                df[df['prog_distance_category'] == distance_category][f"{sport}_mean_w"].max()
            ) + 10

            x_min = min(
                df[df['prog_distance_category'] == distance_category][f"{sport}_mean_m"].min(),
                df[df['prog_distance_category'] == distance_category][f"{sport}_mean_w"].min()
            ) - 10

            for i_suffix, suffix in enumerate(["w", "m"]):
                colours = {
                    "w": "pink",
                    "m": "deepskyblue"
                }
                data = df[df['prog_distance_category'] == distance_category][f"{sport}_mean_{suffix}"]

                if i_sport == 0 and distance_category == "standard":
                    # remove Mooloolaba 2012 outlier
                    data = df[(df['prog_distance_category'] == distance_category) & (df['event_id'] != 54303)][
                        f"{sport}_mean_{suffix}"]

                data_mean = data.mean()
                data_std = data.std()

                axes[i_sport, i_distance_category].hist(
                    data,
                    bins="auto",
                    density=True,
                    alpha=0.5,
                    label=f"{'Women' if suffix == 'w' else 'Men'}",
                    color=colours[suffix],
                )

                axes[i_sport, i_distance_category].axvline(
                    data_mean,
                    color=colours[suffix],
                    linestyle='--',
                    linewidth=2,
                    label=f"{seconds_to_h_min_sec(data_mean, sport=sport)}\n ± {data_std:.0f}s"
                )

                axes[i_sport, i_distance_category].legend()
                axes[i_sport, i_distance_category].grid()
                axes[i_sport, i_distance_category].set_xlim(x_min, x_max)

                locs = axes[i_sport, i_distance_category].get_xticks()

                labels = map(
                    lambda x: seconds_to_h_min_sec(x, use_hours=False, sport=sport, use_units=False).replace(" (",
                                                                                                             "\n("),
                    locs)
                axes[i_sport, i_distance_category].set_xticks(locs)
                axes[i_sport, i_distance_category].set_xticklabels(labels, rotation=0)

    cols = [f"{cat}\n({len(df[df.prog_distance_category == cat])})" for cat in distance_categories]
    rows = sports
    for ax, col in zip(axes[0], cols):
        ax.set_title(col.replace("standard", "olympic").upper(), fontsize=16)
    for ax, row in zip(axes[:, 0], rows):
        if row == "swim":
            row += "\n(/100m)"
        if row == "bike":
            row += "\n(km/h)"
        if row == "run":
            row += "\n(/km)"
        ax.set_ylabel(row.upper(), rotation=90, fontsize=16)

    for ax in axes.flat:
        ax.set_yticklabels([])
        ax.grid()

    fig.tight_layout()

    add_watermark(fig)
    plt.savefig(str(res_dir / "sports_paces.png"), dpi=300)

    plt.show()


def process_results_w_vs_m(df):
    # max_diff_percent = max(df[f"{sport}_diff_percent"].max() for sport in sports)
    max_diff_percent = 0.21
    max_diff_percent += 0.01

    fig, axes = plt.subplots(nrows=len(sports), ncols=2, figsize=(16, 16))
    for i_distance_category, distance_category in enumerate(distance_categories):
        print(distance_category)
        for i_sport, sport in enumerate(sports):
            data = df[df['prog_distance_category'] == distance_category][f"{sport}_diff_percent"]

            if i_sport == 0:
                print(df[(df['prog_distance_category'] == distance_category) & (df[f"{sport}_diff_percent"] > 0.22)])

                # fair to consider same swim equipment
                data = df[
                    (df['prog_distance_category'] == distance_category) &
                    (df[f"{sport}_diff_percent"] < 0.22) &
                    (df["wetsuit_m"] == df["wetsuit_w"])
                    ][f"{sport}_diff_percent"]

            # draw a vertical line at the mean
            data_mean = data.mean()
            data_std = data.std()
            axes[i_sport, i_distance_category].axvline(
                data_mean,
                color='black',
                linestyle='-.',
                linewidth=2
            )
            axes[i_sport, i_distance_category].text(
                data_mean / max_diff_percent - 0.015,
                0.5,
                f"{data_mean:.1%}",
                transform=axes[i_sport, i_distance_category].transAxes,
                rotation=90,
                ha='center',
                va='center',
                fontsize=10
            )
            axes[i_sport, i_distance_category].text(
                data_mean / max_diff_percent + 0.02,
                0.5,
                f"±{data_std:.1%}",
                transform=axes[i_sport, i_distance_category].transAxes,
                rotation=90,
                ha='center',
                va='center',
                fontsize=10
            )
            axes[i_sport, i_distance_category].hist(
                data,
                bins="auto",
                density=True,
                color="deepskyblue",
            )
            # remove y labels since the second percentage could be misleading
            axes[i_sport, i_distance_category].set_yticklabels([])
            # set x tick labels size
            axes[i_sport, i_distance_category].tick_params(axis='x', labelsize=12)

    fig.suptitle(f"WOMEN vs MEN (%)\n({len(df)} events)", fontsize=20)

    cols = [f"{cat} ({len(df[df.prog_distance_category == cat])})" for cat in distance_categories]
    rows = sports
    for ax, col in zip(axes[0], cols):
        ax.set_title(col.replace("standard", "olympic").upper(), fontsize=16)
    for ax, row in zip(axes[:, 0], rows):
        ax.set_ylabel(row.upper(), rotation=90, fontsize=16)

    # use same x range for all subplots
    for ax in axes.flat:
        ax.set_xlim(0, max_diff_percent)

    # use percent as x values
    for ax in axes.flat:
        ax.xaxis.set_major_formatter(PercentFormatter(1))
        ax.grid()

    plt.tight_layout()
    add_watermark(fig)
    plt.savefig(str(res_dir / "wm.png"), dpi=300)
    plt.show()


def process_ages(df):
    # df = df[df["event_category"] != "world-cup"]

    colours = ["pink", "violet", "cyan", "deepskyblue"]
    names_to_plot = ["sprint_w", "olympic_w", "sprint_m", "olympic_m"]

    df["prog_distance_category"] = df["prog_distance_category"].apply(lambda x: x.replace("standard", "olympic"))

    # only keep entries where event_category_ids_m contains one of [624, 351]
    # df = df[df["event_category_ids_m"].apply(lambda x: 624 in x or 351 in x)]

    df = df.sort_values("event_date_m")

    fig = plt.figure(figsize=(20, 9))

    gs = fig.add_gridspec(2, 4)
    ax0 = fig.add_subplot(gs[0, :])

    df_m = df[["age_mean_m", "event_year", "prog_distance_category"]].groupby(
        ["prog_distance_category", "event_year"]).mean("age_mean_m")
    df_w = df[["age_mean_w", "event_year", "prog_distance_category"]].groupby(
        ["prog_distance_category", "event_year"]).mean("age_mean_w")

    count_m = df[["age_mean_m", "event_year", "prog_distance_category"]].groupby(
        ["prog_distance_category", "event_year"]).count()
    count_w = df[["age_mean_w", "event_year", "prog_distance_category"]].groupby(
        ["prog_distance_category", "event_year"]).count()
    df_m["count_m"] = count_m["age_mean_m"]
    df_w["count_w"] = count_w["age_mean_w"]

    df2 = pd.concat([df_m, df_w], axis=1)
    df2.reset_index(inplace=True)

    # assert df2["count_w"].equals(df2["count_m"])

    df_m = df2.pivot(index='event_year', columns='prog_distance_category', values='age_mean_m')
    df_m.columns = [col + "_m" for col in df_m.columns]
    df_w = df2.pivot(index='event_year', columns='prog_distance_category', values='age_mean_w')
    df_w.columns = [col + "_w" for col in df_w.columns]

    df_age = pd.concat([df_m, df_w], axis=1)
    df_age = df_age[names_to_plot]
    df_age.plot(
        kind="bar",
        edgecolor="black",
        ax=ax0,
        color=colours
    )

    age_max = df_age.max().max()
    age_min = df_age.min().min()

    ax0.set_xlabel("")
    ax0.set_xticklabels(ax0.get_xticklabels(), rotation=0, ha='center')
    ax0.legend(ncol=2, loc="upper center")

    # ###

    df_m_2 = df2.copy()
    df_m_2["prog_distance_category"] = df_m_2["prog_distance_category"].apply(lambda x: x + "_m")
    df_m_2 = df_m_2.pivot(index='prog_distance_category', columns='event_year', values='age_mean_m')

    df_w_2 = df2.copy()
    df_w_2["prog_distance_category"] = df_w_2["prog_distance_category"].apply(lambda x: x + "_w")
    df_w_2 = df_w_2.pivot(index='prog_distance_category', columns='event_year', values='age_mean_w')

    df_age_2 = pd.concat([df_m_2, df_w_2], axis=0)
    dict_age = dict(df_age_2.T)
    for _i, name in enumerate(names_to_plot):
        _df = dict_age[name]
        ax = fig.add_subplot(gs[1, _i])

        _mean = _df.mean()
        ax.axhline(_mean, color="black", linestyle="--", alpha=0.4, label=f"avg: {_mean:.1f}")

        _df.plot(
            kind="bar",
            edgecolor="black",
            ax=ax,
            color=colours[_i]
        )

        def change_x_tick_labels(_x):
            # todo: could be cleaned up!
            df3 = df2[["event_year", "count_m", "count_w", "prog_distance_category"]]
            res = df3.loc[
                (df3['event_year'] == int(_x.get_text())) & (df3["prog_distance_category"] == name[:-2])
                ]
            _n_events = res['count' + name[-2:]].iloc[0] if len(res) > 0 else 0
            return f"({_n_events}) {_x.get_text()}"

        new_x_ticklabels = list(map(change_x_tick_labels, ax.get_xticklabels()))
        ax.set_xticklabels(new_x_ticklabels, rotation=90, ha="center")
        x_label = name.split("_")[0].upper() + f" ({name.split('_')[1].upper()})"
        ax.set_xlabel(f"{x_label}\n{_mean :.1f} ± {_df.std():.1f}")

    for ax in fig.get_axes():
        ax.set_ylim(age_min - 1, age_max + 1)
        ax.grid(
            color='grey',
            linestyle='-.',
            linewidth=0.5,
            alpha=0.7
        )
    n_events = dict(df["prog_distance_category"].value_counts())
    n_events_txt = "\n".join([f"({v} {k} events)" for k, v in n_events.items()])
    plt.suptitle(f"AGES\n{n_events_txt}", fontsize=16)
    plt.tight_layout()

    add_watermark(fig, y=0.94)
    plt.savefig(str(res_dir / "ages.png"), dpi=300)
    plt.show()


def process_results_repeated_events(df):
    n_repetitions_min = 4

    df = df.sort_values("event_date_m")

    for i_distance_category, distance_category in enumerate(distance_categories):
        for i_suffix, suffix in enumerate(["w", "m"]):
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(20, 20))
            venue_groups = df[df['prog_distance_category'] == distance_category].groupby("event_venue")

            year_min = df["event_year"].max()
            year_max = df["event_year"].min()

            venue_colours = [
                "black",
                "magenta",
                "darkorange",
                "red",
                "dodgerblue",
                "deepskyblue",
                "blueviolet",
                "pink"
            ]

            venue_groups = [
                v for v in venue_groups
                if (len(v[1]) >= n_repetitions_min) and (set(v[1]["event_category"].values) == {"wcs"})
            ]
            assert len(venue_colours) >= len(
                venue_groups), f"Add colours: {len(venue_groups) = } vs {len(venue_colours) = } {[v[0] for v in venue_groups]}"

            for i_venue, venue_group in enumerate(venue_groups):
                # if len(venue_group[1]) < n_repetitions_min:
                #     continue
                # if set(venue_group[1]["event_category"].values) != {"wcs"}:
                #     continue
                # if venue_group[1]["event_year"].max() < 2020:
                #     continue

                print()
                print(f"venue {i_venue} {venue_group[0]}: ({len(venue_group[1])} events)")

                # print(venue_group[1]["event_year"].value_counts())

                year_min = min(venue_group[1]["event_year"].min(), year_min)
                year_max = max(venue_group[1]["event_year"].max(), year_max)

            for i_sport, sport in enumerate(sports):
                # add std to bars
                data = df[df['prog_distance_category'] == distance_category]

                year_grouping = data.groupby("event_year")
                n_entries = dict(year_grouping["prog_distance_category"].count())
                data_means = year_grouping[f"{sport}_mean_{suffix}"].mean()
                data_stds = year_grouping[f"{sport}_mean_{suffix}"].std()

                # data_means.plot.bar(yerr=data_stds, ax=axes[i_sport])

                axes[i_sport].bar(
                    list(dict(data_means).keys()),
                    list(dict(data_means).values()),
                    # todo: these two lines give other results?
                    # data["event_year"],
                    # data[f"{sport}_mean_{suffix}"],

                    color="gray",
                    # align='edge',
                    align='center',
                    alpha=0.1,
                    width=0.7,
                    yerr=list(dict(data_stds).values()),
                    capsize=10,
                    # fmt="r--o",
                    ecolor="gray",  # The line color of the errorbars.
                    error_kw={"alpha": 0.05},
                    label="All events"
                )

                # a bit dirty, but it works
                cat_bar_dict = {}
                games_venues = {}

                cat_groups = df[df['prog_distance_category'] == distance_category].groupby("event_category")
                for i, (cat_name, cat_group) in enumerate(cat_groups):
                    cat_year_groups = cat_group.groupby("event_year")
                    cat_bar_dict[cat_name] = {}
                    for j, (year, year_group) in enumerate(cat_year_groups):
                        cat_means = year_group[f"{sport}_mean_{suffix}"].mean()
                        cat_stds = year_group[f"{sport}_mean_{suffix}"].std()
                        cat_bar_dict[cat_name][year] = (cat_means, len(year_group))
                        if cat_name == "games":
                            if len(year_group["event_venue"]) == 1:
                                games_venues[year] = year_group["event_venue"].values[0].split(" ")[0]
                                if "test" in year_group["event_title"].values[0].lower():
                                    games_venues[year] += "(test)"
                                elif "olympic qualification" in year_group["event_title"].values[0].lower():
                                    games_venues[year] += "(test)"
                                elif "commonwealth" in year_group["event_title"].values[0].lower():
                                    games_venues[year] += "(commonwealth)"
                            elif len(year_group["event_venue"]) > 1:
                                print(f"more values in one year: {year_group['event_venue'].values}")

                years = sorted(set(year for category in cat_bar_dict.values() for year in category))

                year_min = min(year_min, min(years))
                year_max = max(year_max, max(years))

                # Initialize lists for each category
                games_values = []
                wcs_values = []
                world_cup_values = []

                # Fill the lists with values, using 0 for missing entries
                for year in years:
                    games_values.append(cat_bar_dict['games'].get(year, (0, 0))[0])
                    wcs_values.append(cat_bar_dict['wcs'].get(year, (0, 0))[0])
                    world_cup_values.append(cat_bar_dict['world-cup'].get(year, (0, 0))[0])

                x = np.array(years)  # the label locations
                width = 0.1  # the width of the bars

                bar_kwargs = {
                    "alpha": 0.9,
                    "width": 0.1,
                    # "align": "edge",
                    "align": "center",
                    "edgecolor": "black"
                }

                # Specify colors for the bars
                games_color = 'yellow'
                wcs_color = "lawngreen"  # 'deepskyblue'
                world_cup_color = "cyan"  # 'violet'

                bars1 = axes[i_sport].bar(x - width, world_cup_values, color=world_cup_color, label='World Cup',
                                          **bar_kwargs)
                bars2 = axes[i_sport].bar(x, games_values, color=games_color, label='Games', **bar_kwargs)
                bars3 = axes[i_sport].bar(x + width, wcs_values, color=wcs_color, label='WCS', **bar_kwargs)

                # Add some text for labels, title and custom x-axis tick labels, etc.
                axes[i_sport].set_xticks(x)
                axes[i_sport].set_xticklabels(years)
                if i_sport == 0:
                    axes[i_sport].legend()
                if i_sport == 2:
                    txt = "RUN (WTCS)\n"
                    for i_y, y in enumerate([2019, 2021, 2023]):
                        m, c = cat_bar_dict["wcs"][y]
                        txt += f"{' -->' if i_y > 0 else ''} [{y} ({c}): {seconds_to_h_min_sec(m, sport=sport, use_units=True)}]"
                    axes[i_sport].set_xlabel(txt)
                    axes[i_sport].set_title(txt)  # todo : at bottom

                t_max = data_means.max()
                for max_v in [
                    max(world_cup_values),
                    max(games_values),
                    max(wcs_values),
                    max(venue_group[1][f"{sport}_mean_{suffix}"].max() for venue_group in venue_groups),
                ]:
                    if max_v > 0:
                        t_max = max(t_max, max_v)
                t_min = data_means.min()
                for min_v in [
                    min(world_cup_values),
                    min(games_values),
                    min(wcs_values),
                    min(venue_group[1][f"{sport}_mean_{suffix}"].min() for venue_group in venue_groups),
                ]:
                    if min_v > 0:
                        t_min = min(t_min, min_v)
                axes[i_sport].set_ylim(t_min * 0.95, t_max * 1.02)

                for bar in bars2:
                    x_bar = bar.get_x()
                    for y, ven in games_venues.items():
                        if abs(y - x_bar) < 0.1:
                            scaling_max = 1.00 if sport != "bike" else 1.00
                            axes[i_sport].annotate(
                                ven,
                                xy=(x_bar + bar.get_width() / 2, t_max * scaling_max),

                                # xytext=(x_bar + bar.get_width() / 2, t_max * 1.05),
                                xytext=(0, 2),
                                textcoords="offset fontsize",

                                arrowprops={
                                    # "arrowstyle": "->",
                                    "width": 0.5,
                                    "headwidth": 6,
                                    "headlength": 6,
                                    # "color": games_color
                                },
                                fontsize=11,
                                # color=games_color,
                                fontstyle="normal",
                                ha='center',
                                va='bottom'
                            )

                for i_venue, venue_group in enumerate(venue_groups):
                    # plot the previous events
                    venue_group[1].plot(
                        color=venue_colours[i_venue],
                        kind='line',
                        linestyle='-.',
                        x="event_year",
                        y=f"{sport}_mean_{suffix}",
                        label=f"{venue_group[0]} ({len(venue_group[1])})",
                        ax=axes[i_sport],
                    )
                    venue_group[1].plot(
                        color=venue_colours[i_venue],
                        kind='scatter',
                        marker='o',
                        s=25,
                        x="event_year",
                        y=f"{sport}_mean_{suffix}",
                        ax=axes[i_sport],
                    )

                axes[i_sport].get_legend().remove()
                axes[i_sport].set_xlim(year_min - 1, year_max)
                axes[i_sport].xaxis.set_major_locator(plt.MultipleLocator(1))

                locs = axes[i_sport].get_xticks()
                labels = map(lambda _x: f"{_x:.0f}\n({n_entries[_x] if _x in n_entries else 0:.0f})", locs)
                axes[i_sport].set_xticks(locs)
                axes[i_sport].set_xticklabels(labels, fontsize=13)

                locs = axes[i_sport].get_yticks()
                labels = map(lambda _x: seconds_to_h_min_sec(_x, use_hours=True, sport=sport, use_units=True), locs)
                axes[i_sport].set_yticks(locs)
                axes[i_sport].set_yticklabels(labels)
                # set tick font size
                axes[i_sport].yaxis.set_tick_params(labelsize=13)
                axes[i_sport].set_ylabel(sport.upper(), fontsize=15)

            for ax in axes.flat:
                # ax.get_legend().remove()
                # ax.set_xlim(year_min - 1, year_max + 1)
                # ax.xaxis.set_major_locator(plt.MultipleLocator(1))

                ax.set_xlabel("")
                ax.grid()

            handles, labels = axes[0].get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            fig.legend(
                by_label.values(),  # handles,
                [lab.replace("WCS", "WTCS") for lab in by_label.keys()],  # labels,
                loc='upper center',
                ncol=min(len(venue_groups) + 4, 10),
                shadow=True,
                fontsize=15,
                # bbox_to_anchor = (0.5, 0),
                # bbox_transform = plt.gcf().transFigure
            )

            fig.suptitle(
                f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'}",
                fontsize=20
            )
            plt.tight_layout()
            add_watermark(fig)
            plt.savefig(str(res_dir / f"repeated_events_{distance_category}_{suffix}.png"), dpi=300)
            plt.show()


def process_sprint_finish(df):
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20))

    for i_distance_category, distance_category in enumerate(distance_categories):
        for i_suffix, suffix in enumerate(["w", "m"]):
            df2 = df[
                (df['prog_distance_category'] == distance_category)
            ]
            kwargs = {
                "alpha": 0.5,
                "rwidth": 0.9,
                "density": True,
                "edgecolor": "black",
                "linewidth": 2
            }
            binwidth = 2
            n, bins, patches = axes[i_distance_category, i_suffix].hist(
                df2[f"second_delay_{suffix}"],
                bins=range(0, max(df2[f"second_delay_{suffix}"]) + binwidth, binwidth),
                **kwargs
            )
            patches[0].set_fc('r')
            patches[1].set_fc('orange')

            # set the y-axis ticks:  normalize such that the total area of the histogram equals 1!!!
            axes[i_distance_category, i_suffix].set_yticklabels(map(
                lambda x: f"{binwidth * x:.1%}",
                axes[i_distance_category, i_suffix].get_yticks()
            ))

            # set x ticks from 0 to current max
            axes[i_distance_category, i_suffix].set_xticks(
                range(0, max(df2[f"second_delay_{suffix}"]) + binwidth, binwidth))

            # rotate x ticks by 90
            axes[i_distance_category, i_suffix].set_xticklabels(axes[i_distance_category, i_suffix].get_xticks(),
                                                                rotation=90)

            axes[i_distance_category, i_suffix].grid()

            axes[i_distance_category, i_suffix].xaxis.set_major_locator(plt.MultipleLocator(binwidth))

            large_gap_df = df2[df2[f"second_delay_{suffix}"] >= 30 * (1 + i_distance_category)]
            large_gap_df = large_gap_df[["event_venue", "event_year", f"second_delay_{suffix}", f"winner_{suffix}"]]

            large_gap_df = large_gap_df.sort_values(f"event_year", ascending=False)

            largest_delay = df2[f"second_delay_{suffix}"].max()
            for delay_min in range(0, largest_delay + binwidth, binwidth):
                txt = ""
                for index, row in large_gap_df.iterrows():
                    delay_s = row[f"second_delay_{suffix}"]
                    if delay_min <= delay_s < delay_min + binwidth:
                        txt += f"[{row[f'winner_{suffix}']} ({row['event_year']} {row['event_venue']})]  "
                if txt:
                    txt = txt[:-2]
                    axes[i_distance_category, i_suffix].text(
                        delay_min + 1 if delay_min != largest_delay else delay_min - 1,  # some handle for last bin
                        0.0,
                        txt,
                        fontsize=10 if len(txt) < 70 else 9,
                        rotation=90,
                        va="bottom",
                        ha="center"
                    )
                    # print(len(txt), txt)

            median_delay_s = df2[f'second_delay_{suffix}'].median()
            axes[i_distance_category, i_suffix].axvline(
                median_delay_s,
                color='darkviolet',
                linestyle='dashed',
                linewidth=2,
                alpha=0.7,
            )
            axes[i_distance_category, i_suffix].text(
                median_delay_s - 1,
                max(n),
                f"median={median_delay_s:.0f}s",
                fontsize=10,
                rotation=90,
                va="top",
                ha="center",
                color="darkviolet"
            )

            mean_delay_s = df2[f"second_delay_{suffix}"].mean()
            axes[i_distance_category, i_suffix].axvline(
                mean_delay_s,
                color='green',
                linestyle='dashed',
                linewidth=2,
                alpha=0.7,
            )
            # add text
            axes[i_distance_category, i_suffix].text(
                mean_delay_s + 1,
                max(n),
                f"mean={mean_delay_s:.0f}s",
                fontsize=10,
                rotation=90,
                va="top",
                ha="center",
                color="green"
            )

            axes[i_distance_category, i_suffix].set_title(
                f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'} ({len(df2)} events)"
                # f"\n (median={median_delay_s :.0f}s) - (mean={mean_delay_s:.0f}s)"
                f"\n{n[0] * binwidth:.1%} below 2s (sprint finish)",
                fontsize=20
            )

    plt.suptitle(f"TIME BETWEEN FIRST AND SECOND AT FINISH (seconds)\n ({len(df)} events)", fontsize=20)
    plt.tight_layout()
    add_watermark(fig)
    plt.savefig(str(res_dir / f"sprint_finish.png"), dpi=300)
    plt.show()

    # plot over years

    # df = df[df["event_category"] != "world-cup"]

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20))

    sprint_gap_max_s = 3

    sprint_finish_data = []

    for i_distance_category, distance_category in enumerate(distance_categories):
        for i_suffix, suffix in enumerate(["w", "m"]):
            df2 = df[
                (df['prog_distance_category'] == distance_category)
            ]

            print(
                f"{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'}:")
            for index, row in df2.iterrows():
                if row[f"second_delay_{suffix}"] < 2:
                    print(
                        f"\t{row['event_year']} - {row['event_venue']} {row[f'winner_{suffix}']} outperforms {row[f'second_{suffix}']} ({row[f'second_delay_{suffix}']}s)")
                    print(f"\t\tlink:{row['event_title']}")

                    first_country = row[f"winner_country_{suffix}"]
                    second_country = row[f"second_country_{suffix}"]
                    event_country = row["event_country_noc"]

                    first_country_emoji = country_emojis[
                        first_country] if first_country in country_emojis else first_country
                    second_country_emoji = country_emojis[
                        second_country] if second_country in country_emojis else second_country
                    event_country_emoji = country_emojis[
                        event_country] if event_country in country_emojis else event_country

                    first = row[f"winner_{suffix}"]
                    second = row[f"second_{suffix}"]

                    event_venue = row["event_venue"].replace("Jintang, Chengdu, Sichuan Province, China", "Chengdu")

                    event_listing = row['event_listing']
                    # event_listing = "http://www.triathlon.org"
                    assert "http" in event_listing

                    sprint_finish_data.append({
                        "suffix": suffix,

                        "year": f"[{row['event_year']}]({event_listing})",
                        "venue": f"[{event_venue}]({event_listing}) ( {event_country_emoji} )",
                        "event_country": event_country,

                        "dist.": row["prog_distance_category"].replace("standard", "olympic"),

                        "race category": row["event_category"],

                        "first": f'{first} ( {first_country_emoji} )',
                        "first_country": first_country,

                        "second": f'{second} ( {second_country_emoji} )',
                        "second_country": second_country,

                        # "title": row["event_title"],
                        # "url": f"[link]({event_listing})",
                        # "second_delay": row[f"second_delay_{suffix}"],
                    })

            df2 = df2[["event_year", f"second_delay_{suffix}"]]

            year_datas = {}
            for year, year_data in df2.groupby(["event_year"]):
                year_datas[year[0]] = {
                    "second_delays": year_data[f"second_delay_{suffix}"].values,
                    "second_delay_mean": year_data[f"second_delay_{suffix}"].mean(),
                    "second_delay_std": year_data[f"second_delay_{suffix}"].std(),
                    "second_delay_count": year_data[f"second_delay_{suffix}"].count(),
                    "is_win_by_sprint": [v < sprint_gap_max_s for v in year_data[f"second_delay_{suffix}"].values],
                }
                year_datas[year[0]]["is_win_by_sprint_mean"] = np.mean(year_datas[year[0]]["is_win_by_sprint"])
                year_datas[year[0]]["is_win_by_sprint_std"] = np.std(year_datas[year[0]]["is_win_by_sprint"])

            df3 = pd.DataFrame.from_dict(year_datas, orient="index")

            axes[i_distance_category, i_suffix].bar(
                df3.index,
                df3[f"second_delay_mean"],
                color="gray",
                # align='edge',
                align='center',
                alpha=0.5,
                width=0.7,
                # yerr=list(dict(df3[f"second_delay_std"]).values()),
                capsize=10,
                # fmt="r--o",
                ecolor="gray",  # The line color of the errorbars.
                error_kw={"alpha": 0.3},
            )

            # add text on the bars
            for _x, second_delays in zip(df3.index, df3[f"second_delays"]):
                axes[i_distance_category, i_suffix].text(
                    _x,
                    0.5,
                    " ".join(map(str, sorted(second_delays))),
                    ha="center",
                    rotation=90,
                    fontsize=8
                )
            ax2 = axes[i_distance_category, i_suffix].twinx()

            # set Nan if is_win_by_sprint_count is less than 3
            min_n_data = 3
            df3[f"is_win_by_sprint_mean"] = df3[f"is_win_by_sprint_mean"].where(
                df3["second_delay_count"] > min_n_data - 1, np.nan)

            ax2.plot(
                df3.index,
                df3[f"is_win_by_sprint_mean"],
                color="red",
                marker="o",
                alpha=0.5,
            )

            # set y min (keep current y max)
            axes[i_distance_category, i_suffix].set_ylim(0, axes[i_distance_category, i_suffix].get_ylim()[1])

            # set y limits
            ax2.set_ylim(0, 1.1)

            # set x ticks
            axes[i_distance_category, i_suffix].set_xticks(df3.index)
            axes[i_distance_category, i_suffix].set_xticklabels(df3.index, rotation=90)

            # set y name
            axes[i_distance_category, i_suffix].set_ylabel("FIRST <-> SECOND (s)")

            if i_suffix == 1:
                ax2.set_ylabel(
                    f"SPRINT FINISH\n(DIFFERENCE < {sprint_gap_max_s}s)\n(at least {min_n_data} events per year)")

            ax2.yaxis.label.set_color("red")
            ax2.yaxis.set_major_formatter(PercentFormatter(1))
            # color the yaxis tick labels
            ax2.tick_params(axis="y", colors="red")

            # grid horizontal
            ax2.grid(axis="y", alpha=0.5)

            delays_all = [s for li in df3["second_delays"].tolist() for s in li]
            axes[i_distance_category, i_suffix].set_title(
                f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'} "
                f"({len(df2)} events)"
                f"\nAvg. {np.mean(delays_all):.1f} s",
                fontsize=20
            )

    fig.suptitle(
        "TIME BETWEEN FIRST AND SECOND AT FINISH (seconds)"
        f"\n{len(df):,} EVENTS",
        fontsize=20
    )

    sprint_finish_df = pd.DataFrame(sprint_finish_data)

    country_names = sorted(list(set(
        sprint_finish_df["first_country"].unique().tolist() + sprint_finish_df["second_country"].unique().tolist() +
        sprint_finish_df["event_country"].unique().tolist())))
    print(country_names)

    # remove first_country column
    sprint_finish_df.drop("first_country", axis=1, inplace=True)
    sprint_finish_df.drop("second_country", axis=1, inplace=True)
    sprint_finish_df.drop("event_country", axis=1, inplace=True)

    print()

    for suffix in ["w", "m"]:
        sprint_finish_df2 = sprint_finish_df[sprint_finish_df.suffix == suffix].reset_index(drop=True)
        sprint_finish_df2["race category"] = sprint_finish_df2["race category"].apply(lambda x: x.replace("wcs", "wtcs"))
        sprint_finish_df2.drop("suffix", axis=1, inplace=True)
        sprint_finish_df2.columns = ["YEAR", "VENUE", "DIST.", "RACE CATEGORY", "FIRST-COL", "SECOND-COL"]
        txt = sprint_finish_df2.sort_values(["YEAR"]).to_markdown(
            index=False,
            colalign=["center"] * len(sprint_finish_df2.columns)
        )
        txt = txt.replace(" FIRST-COL", " FIRST ( :1st_place_medal: )")
        txt = txt.replace(" SECOND-COL", " SECOND ( :2nd_place_medal: )")
        print(txt)

    fig.tight_layout()
    add_watermark(fig)
    plt.savefig(str(res_dir / f"sprint_finish_over_years.png"), dpi=300)
    plt.show()


def process_scenarios(df):
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20))

    df = df[df["event_category"] != "world-cup"]
    # df = df[df["event_category"] == "world-cup"]

    for i_distance_category, distance_category in enumerate(distance_categories):
        for i_suffix, suffix in enumerate(["w", "m"]):
            df2 = df[
                (df['prog_distance_category'] == distance_category)
            ]
            kwargs = {
                "alpha": 0.5,
                "rwidth": 0.9,
                "density": True,
                "edgecolor": "black",
                "color": "mediumvioletred" if suffix == "w" else "mediumturquoise",
                "linewidth": 2
            }
            binwidth = 5
            axes[i_distance_category, i_suffix].hist(
                df2[f"pack_size_{suffix}"],
                bins=range(0, max(df2[f"pack_size_{suffix}"]) + binwidth, binwidth),
                **kwargs
            )

            # set the font size of x ticks
            axes[i_distance_category, i_suffix].tick_params(axis="x", labelsize=18)

            # set the font size of y ticks
            axes[i_distance_category, i_suffix].tick_params(axis="y", labelsize=18)
            # set the y-axis ticks:  normalize such that the total area of the histogram equals 1!!!
            axes[i_distance_category, i_suffix].set_yticklabels(map(
                lambda x: f"{binwidth * x:.1%}",
                axes[i_distance_category, i_suffix].get_yticks()
            ))

            axes[i_distance_category, i_suffix].grid()

            percent_winner_in_pack = df2[f"is_winner_in_front_pack_{suffix}"].sum() / len(df2)
            percent_best_runner_in_pack = df2[f"is_best_runner_in_front_pack_{suffix}"].sum() / len(df2)
            axes[i_distance_category, i_suffix].set_title(
                f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'}"
                f"\nWinner in front pack: {percent_winner_in_pack:.1%}"
                f"\nBest runner in front pack: {percent_best_runner_in_pack:.1%}" f"",
                fontsize=20
            )
            axes[i_distance_category, i_suffix].xaxis.set_major_locator(plt.MultipleLocator(binwidth))

    fig.suptitle(
        f"FRONT-PACK SIZES ($pack\\_duration\\_s = 10$) AFTER BIKE"
        f"\n{len(df):,} WTCS AND GAMES-RELATED EVENTS",
        # f"\n{len(df):,} WORLD-CUP EVENTS ONLY",
        fontsize=20
    )

    plt.tight_layout()
    add_watermark(fig)
    plt.savefig(str(res_dir / f"scenarios.png"), dpi=300)
    # plt.savefig(str(res_dir / f"scenarios_wc.png"), dpi=300)
    plt.show()

    table_info = []
    for suffix in ["w", "m"]:
        df_table = df[(df[f"pack_size_{suffix}"] < 4) & (df2[f"is_winner_in_front_pack_{suffix}"])]
        df_table.sort_values(
            by=[
                f"pack_size_{suffix}",
                f"event_year"
            ],
            ascending=True,
            inplace=True
        )
        print(f"{suffix.upper()}")
        for i_row, row in df_table.iterrows():
            winner_name = row[f'winner_{suffix}']
            table_info.append({
                "pack_size": row[f"pack_size_{suffix}"],
                "year": row["event_year"],
                "winner": f"{winner_name} ( {country_emojis[row[f'winner_country_{suffix}']] if row[f'winner_country_{suffix}'] in country_emojis else row['winner_country_noc']} )",
                "distance": row["prog_distance_category"].replace("standard", "olympic").upper(),
                "cat": row["event_category"].upper().replace("WCS", "WTCS"),
                "event": f"[{row['event_title']} ( {country_emojis[row['event_country_noc']] if row['event_country_noc'] in country_emojis else row['event_country_noc']} )]({row['event_listing']})",
            })

        table_info.append({
            "pack_size": "...",
            "year": "...",
            "winner": "...",
            "distance": "...",
            "cat": "...",
            "event": "...",
        })

    # print markdown
    df_table = pd.DataFrame(table_info)
    print(df_table.to_markdown(
        index=False,
        colalign=["center"] * len(df_table.columns)
    ))

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20))

    for i_distance_category, distance_category in enumerate(distance_categories):
        for i_suffix, suffix in enumerate(["w", "m"]):
            df2 = df[
                (df['prog_distance_category'] == distance_category)
            ]
            df2 = df2[["event_year", f"pack_size_{suffix}", f"is_winner_in_front_pack_{suffix}",
                       f"is_best_runner_in_front_pack_{suffix}"]]

            year_datas = {}
            for year, year_data in df2.groupby(["event_year"]):
                year_datas[year[0]] = {
                    "pack_sizes": year_data[f"pack_size_{suffix}"].values,
                    "pack_size_mean": year_data[f"pack_size_{suffix}"].mean(),
                    "pack_size_std": year_data[f"pack_size_{suffix}"].std(),
                    "pack_size_count": year_data[f"pack_size_{suffix}"].count(),
                    "is_winner_in_front_packs": year_data[f"is_winner_in_front_pack_{suffix}"].values,
                    "is_winner_in_front_pack_mean": year_data[f"is_winner_in_front_pack_{suffix}"].mean(),
                    "is_winner_in_front_pack_std": year_data[f"is_winner_in_front_pack_{suffix}"].std(),
                    "is_best_runner_in_front_packs": year_data[f"is_best_runner_in_front_pack_{suffix}"].values,
                    "is_best_runner_in_front_pack_mean": year_data[f"is_best_runner_in_front_pack_{suffix}"].mean(),
                    "is_best_runner_in_front_pack_std": year_data[f"is_best_runner_in_front_pack_{suffix}"].std(),
                }

            df3 = pd.DataFrame.from_dict(year_datas, orient="index")

            axes[i_distance_category, i_suffix].bar(
                df3.index,
                df3[f"pack_size_mean"],
                color="gray",
                # align='edge',
                align='center',
                alpha=0.5,
                width=0.7,
                yerr=list(dict(df3[f"pack_size_std"]).values()),
                capsize=10,
                # fmt="r--o",
                ecolor="gray",  # The line color of the errorbars.
                error_kw={"alpha": 0.3},
                label="All events"
            )

            # add text on the bars
            for _x, pack_sizes in zip(df3.index, df3[f"pack_sizes"]):
                axes[i_distance_category, i_suffix].text(
                    _x,
                    0.5,
                    " ".join(map(str, sorted(pack_sizes))),
                    ha="center",
                    rotation=90,
                    fontsize=8
                )
            ax2 = axes[i_distance_category, i_suffix].twinx()
            ax2.plot(
                df3.index,
                df3[f"is_winner_in_front_pack_mean"],
                color="red",
                marker="o",
                alpha=0.5,
                label="Winner in front pack"
            )

            # ax3 = axes[i_distance_category, i_suffix].twinx()
            # ax3.spines.right.set_position(("axes", 1.1))
            # ax3.plot(
            #     df3.index,
            #     df3[f"is_best_runner_in_front_pack_mean"],
            #     color="green",
            #     marker="o",
            #     alpha=0.5,
            #     label="Best runner in front pack"
            # )
            # ax3.yaxis.set_major_formatter(PercentFormatter(1))

            # ax2.fill_between(
            #     df3.index,
            #     df3[f"is_winner_in_front_pack_mean"] - df3[f"is_winner_in_front_pack_std"],
            #     df3[f"is_winner_in_front_pack_mean"] + df3[f"is_winner_in_front_pack_std"],
            #     color="red",
            #     alpha=0.2
            # )

            # set y min (keep current y max)
            axes[i_distance_category, i_suffix].set_ylim(0, axes[i_distance_category, i_suffix].get_ylim()[1])

            # set y limits
            ax2.set_ylim(0, 1.1)
            # ax3.set_ylim(0, 1.1)

            # set x ticks
            axes[i_distance_category, i_suffix].set_xticks(df3.index)
            axes[i_distance_category, i_suffix].set_xticklabels(df3.index, rotation=90)

            # set y name
            if i_suffix == 0:
                axes[i_distance_category, i_suffix].set_ylabel("pack size".upper())

            # ax3.yaxis.set_ticklabels([])
            if i_suffix == 1:
                ax2.set_ylabel("winner in front pack (%)".upper())
                # ax3.set_ylabel("best runner in front pack (%)".upper())

                ax2.yaxis.label.set_color("red")
                # ax3.yaxis.label.set_color("green")
                ax2.yaxis.set_major_formatter(PercentFormatter(1))

            else:
                ax2.yaxis.set_ticklabels([])

            # grid horizontal
            ax2.grid(axis="y", alpha=0.5)

            pack_sizes_all = [s for li in df3["pack_sizes"].tolist() for s in li]
            axes[i_distance_category, i_suffix].set_title(
                f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'} "
                f"({len(df2)} events)\nAverage front pack size: {np.mean(pack_sizes_all):.1f}",
                fontsize=20
            )

    fig.suptitle(
        f"FRONT-PACK SIZES ($pack\\_duration\\_s = 10$) AFTER BIKE"
        f"\nAND PRESENCE OF THE WINNER IN THE FRONT-PACK"
        f"\n{len(df):,} WTCS AND GAMES-RELATED EVENTS",
        # f"\n{len(df):,} WORLD-CUP EVENTS ONLY",
        fontsize=20
    )

    fig.tight_layout()

    add_watermark(fig, y=0.96)
    plt.savefig(str(res_dir / f"scenarios_over_years.png"), dpi=300)
    # plt.savefig(str(res_dir / f"scenarios_over_years_wc.png"), dpi=300)
    plt.show()

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20))

    for i_distance_category, distance_category in enumerate(distance_categories):
        for i_suffix, suffix in enumerate(["w", "m"]):
            # histogram of best_runner_wins per year
            df3 = df[
                (df["prog_distance_category"] == distance_category)
            ].groupby("event_year").agg(
                best_runner_wins_=(f"best_runner_wins_{suffix}", "mean"),
            )

            axes[i_distance_category, i_suffix].bar(
                df3.index,
                df3["best_runner_wins_"],
                color="mediumvioletred" if suffix == "w" else "mediumturquoise",
                alpha=0.5,
                edgecolor='black',
            )

            axes[i_distance_category, i_suffix].set_title(
                f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'} "
                f"({len(df3)} events)",
                fontsize=20
            )

            # set y as percent
            axes[i_distance_category, i_suffix].yaxis.set_major_formatter(PercentFormatter(1))

            # compute mean of
            df4 = df[(df["prog_distance_category"] == distance_category)][f"best_runner_wins_{suffix}"]
            mean = df4.mean()

            # add line
            axes[i_distance_category, i_suffix].axhline(
                mean,
                linestyle="-.",
                linewidth=1,
                alpha=1,
                color="black",
                label=f"Average: {mean:.1%}"
            )
            axes[i_distance_category, i_suffix].legend()

            # set subtitle
            axes[i_distance_category, i_suffix].set_ylabel("best runner wins (%)".upper())

            # set title
            axes[i_distance_category, i_suffix].set_title(
                f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'} "
                f"({len(df4)} events)\nAverage: {mean:.1%}",
                fontsize=20
            )

            # count events per year
            count_dict = df[(df["prog_distance_category"] == distance_category)].groupby("event_year").agg(
                events_count=(f"event_id", "count"),
            )["events_count"].to_dict()

            # set x ticks
            axes[i_distance_category, i_suffix].set_xticks(df3.index)
            axes[i_distance_category, i_suffix].set_xticklabels([
                f"{year} ({count_dict[year]})"
                for year in df3.index
            ], rotation=90)

    fig.suptitle(
        f"BEST RUNNER WINS"
        f"\n{len(df):,} WTCS AND GAMES-RELATED EVENTS",
        # f"\n{len(df):,} WORLD-CUP EVENTS ONLY",
        fontsize=20
    )

    fig.tight_layout()

    add_watermark(fig)
    plt.savefig(str(res_dir / f"best_runner_wins.png"), dpi=300)
    # plt.savefig(str(res_dir / f"best_runner_wins_wc.png"), dpi=300)
    plt.show()


def process_sport_proportion(df):
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 16))

    for i_suffix, suffix in enumerate(["w", "m"]):
        df[f"total_mean_{suffix}"] = df[f"swim_mean_{suffix}"] + df[f"t1_mean_{suffix}"] + df[f"bike_mean_{suffix}"] + \
                                     df[
                                         f"t2_mean_{suffix}"] + df[f"run_mean_{suffix}"]
        df[f"swim_prop_{suffix}"] = df[f"swim_mean_{suffix}"] / df[f"total_mean_{suffix}"]
        df[f"t1_prop_{suffix}"] = df[f"t1_mean_{suffix}"] / df[f"total_mean_{suffix}"]
        df[f"bike_prop_{suffix}"] = df[f"bike_mean_{suffix}"] / df[f"total_mean_{suffix}"]
        df[f"t2_prop_{suffix}"] = df[f"t2_mean_{suffix}"] / df[f"total_mean_{suffix}"]
        df[f"run_prop_{suffix}"] = df[f"run_mean_{suffix}"] / df[f"total_mean_{suffix}"]

    rows_names = []
    for i_distance_category, distance_category in enumerate(distance_categories):
        for i_suffix, suffix in enumerate(["w", "m"]):
            pie_sports = ["swim", "t1", "bike", "t2", "run"]
            means = [
                df[f"{sport}_prop_{suffix}"][df['prog_distance_category'] == distance_category].mean()
                for sport in pie_sports
            ]
            stds = [
                df[f"{sport}_prop_{suffix}"][df['prog_distance_category'] == distance_category].std()
                for sport in pie_sports
            ]

            t1_mean = df[f"t1_mean_{suffix}"][df['prog_distance_category'] == distance_category].mean()
            t2_mean = df[f"t2_mean_{suffix}"][df['prog_distance_category'] == distance_category].mean()
            print(
                f"{distance_category} {suffix}: {t1_mean = :.3f} s, {t2_mean = :.3f} s  - should be distance independent")

            axes[i_suffix, i_distance_category].pie(
                means,
                labels=[
                    f"{sport.upper()}\n{mean:.1%} \n±{std:.1%}" for sport, mean, std in zip(pie_sports, means, stds)
                ],
                counterclock=False,
                wedgeprops={
                    "edgecolor": "k",
                    'linewidth': 1,
                    # 'linestyle': 'dashed',
                    # 'antialiased': True
                },
                colors=["deepskyblue", "yellow", "tomato", "yellow", "lawngreen"],
                # autopct='%1.1f%%',
                # shadow=True,
                textprops={'fontsize': 12},
                startangle=90
            )

            if i_suffix == 0:
                axes[i_suffix, i_distance_category].set_title(
                    f"{distance_category.replace('standard', 'olympic').upper()}\n({len(df[df['prog_distance_category'] == distance_category]):,} events)",
                    fontsize=20
                )

    rows = ["WOMEN", "MEN"]
    for ax, row in zip(axes[:, 0], rows):
        ax.set_ylabel(row, rotation=90, fontsize=20)

    for ax, row in zip(axes[:, 0], rows_names):
        ax.set_ylabel(row, rotation=90, size='large')

    title = "PROPORTION OF EACH LEG"

    swim_mean = 0.5 * (df[f"swim_prop_w"].mean() + df[f"swim_prop_m"].mean())
    t1_mean = 0.5 * (df[f"t1_prop_w"].mean() + df[f"t1_prop_m"].mean())
    bike_mean = 0.5 * (df[f"bike_prop_w"].mean() + df[f"bike_prop_m"].mean())
    t2_mean = 0.5 * (df[f"t2_prop_w"].mean() + df[f"t2_prop_m"].mean())
    run_mean = 0.5 * (df[f"run_prop_w"].mean() + df[f"run_prop_m"].mean())

    title += f"\nSWIM ({swim_mean:.1%}) | T1 ({t1_mean:.1%}) | BIKE ({bike_mean:.1%}) | T2 ({t2_mean:.1%}) | RUN ({run_mean:.1%})"

    for i_suffix, suffix in enumerate(["w", "m"]):
        t1_mean = df[f"t1_mean_{suffix}"].mean()
        t2_mean = df[f"t2_mean_{suffix}"].mean()
        title += f"\n{suffix}: T1 = {t1_mean:.0f} s, T2 = {t2_mean :.0f} s"

    title += f"\n({len(df)} events)"

    fig.suptitle(
        title,
        fontsize=20
    )

    plt.tight_layout()
    add_watermark(fig)
    plt.savefig(str(res_dir / "sport_proportion.png"), dpi=300)
    plt.show()

    df["t1+t2_mean_m"] = df["t1_mean_m"] + df["t2_mean_m"]
    df["t1+t2_mean_w"] = df["t1_mean_w"] + df["t2_mean_w"]
    for t_what in ["t1", "t2", "t1+t2"]:
        table_info = []
        for ascending, ascending_name in [(True, "shortest"), (False, "longest")]:
            print("### " * 5)
            print(f"{ascending_name} {t_what.upper()}")
            for suffix in ["m", "w"]:
                print(f"{suffix.upper()}")
                for i_row, row in df.sort_values(by=f"{t_what}_mean_{suffix}", ascending=ascending).head(10).iterrows():
                    t_time = row[f"{t_what}_mean_{suffix}"]
                    print(f'{row["event_title"]}: {t_time :.1f}s ({seconds_to_h_min_sec(t_time)})')
                    print(f'\t{row["event_listing"]}')
                    print(f'\t{row["prog_distance_category"]}')
                    event_listing = row["event_listing"]
                    table_info.append({
                        "t_time": seconds_to_h_min_sec(t_time),
                        "EVENT": f"[{row['event_title']} ( {country_emojis[row['event_country_noc']] if row['event_country_noc'] in country_emojis else row['event_country_noc']} )]({event_listing})",
                        "DISTANCE": row["prog_distance_category"].replace("standard", "olympic").upper(),
                    })
                print("---")
                table_info.append({
                    "t_time": ".",
                    "EVENT": ".",
                })

            table_info.append({
                "t_time": "...",
                "EVENT": "...",
            })

        # print markdown
        df_table = pd.DataFrame(table_info)
        print(df_table.to_markdown(
            index=False,
            colalign=["center"] * len(df_table.columns)
        ))
    print("why some T not plausible, e.g. 7s for T1 at 2016 ITU World Triathlon Gold Coast?")

    print(df["t1+t2_mean_m"].describe())
    print(df["t1+t2_mean_w"].describe())


def process_swim_gaps(df):
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 16))

    df = df[df["event_category"] != "games"]
    # df = df[df["event_category"] != "world-cup"]

    for suffix in ["w", "m"]:
        df[f'swim_gap_{suffix}'] = df[f'swim_mean_{suffix}_last'] - df[f'swim_mean_{suffix}']

    gap_diffs = []
    for i_distance_category, distance_category in enumerate(distance_categories):
        for i_suffix, suffix in enumerate(["w", "m"]):
            df_ = df[(df[f'wetsuit_{suffix}'].notna()) & (df['prog_distance_category'] == distance_category)]
            wet = df_[df_[f'wetsuit_{suffix}']][f"swim_gap_{suffix}"]
            no_wet = df_[~df_[f'wetsuit_{suffix}'].astype(bool)][f"swim_gap_{suffix}"]
            colours = {
                "w": ("navy", "violet"),
                "m": ("navy", "cyan"),
            }

            axes[i_suffix, i_distance_category].hist(
                wet,
                bins="auto",
                density=True,
                alpha=0.5,
                label=f"wetsuit ({len(wet):,})",
                color=colours[suffix][0],
            )

            axes[i_suffix, i_distance_category].hist(
                no_wet,
                bins="auto",
                density=True,
                alpha=0.5,
                label=f"no wetsuit ({len(no_wet):,})",
                color=colours[suffix][1],
            )

            wet_mean = wet.mean()
            wet_std = wet.std()
            no_wet_mean = no_wet.mean()
            no_wet_std = no_wet.std()

            gap_diff = wet_mean - no_wet_mean
            gap_diffs.append(gap_diff)

            for i_, (mean, std, colour) in enumerate([(wet_mean, wet_std, 'r'), (no_wet_mean, no_wet_std, 'b')]):
                axes[i_suffix, i_distance_category].axvline(
                    mean,
                    color=colours[suffix][i_],
                    linestyle='-.',
                    linewidth=2,
                    # label=f"{str(datetime.timedelta(seconds=round(mean)))} ± {std:.0f}"
                    label=f" {mean:.1f} ± {std:.0f} s"
                )

            print(f"{distance_category} ({suffix.upper()}) ({len(df_)})")
            print(f"\twet_mean    = {wet_mean:.0f} ±{wet_std:.0f} ({len(wet):,})")
            print(f"\tno_wet_mean = {no_wet_mean:.0f} ±{no_wet_std:.0f} ({len(no_wet):,})")
            improve_percent = (no_wet_mean - wet_mean) / wet_mean
            print(f"\timprove_percent = {improve_percent :.1%}")
            print()

            # print rows with larger gap_diff
            # df_[["event_title", f"wetsuit_{suffix}", f"swim_gap_{suffix}"]][df_[f"swim_gap_{suffix}"] > 30]

            axes[i_suffix, i_distance_category].legend()
            axes[i_suffix, i_distance_category].grid()

            if gap_diff > 0:
                _title = "LARGER gaps with WETSUIT"
            else:
                _title = "SMALLER gaps with WETSUIT"
            _title += f": {gap_diff:.1f} s (avg.)"
            if i_suffix == 0:
                _title = f'{distance_category.replace("standard", "olympic").upper()}\n{_title}'
            axes[i_suffix, i_distance_category].set_title(_title)

    rows = ["WOMEN", "MEN"]
    # for ax, col in zip(axes[0], cols):
    #     ax.set_title(col.replace("standard", "olympic").upper())
    for ax, row in zip(axes[:, 0], rows):
        ax.set_ylabel(row, rotation=90, size='large')

    for ax in axes.flat:
        ax.set_yticklabels([])

    title = "SWIM GAPS"
    if all(diff > 0 for diff in gap_diffs):
        title += "\nON AVG. GAPS ARE LARGER WITH WETSUIT"
        title += ": ("
        title += ", ".join([str(round(diff, 1)) for diff in sorted(gap_diffs)])
        title += " s)"
    title += "\n(between first 5-9th and last 5-9th)\n(using WTCS and world-cups events)"
    # title += "\n(between first 5-9th and last 5-9th)\n(using WTCS events only)"
    # title += "\n(between first 5-9th and 20-24th)\n(using WTCS events only)"
    # title += "\n(between first 5-9th and 20-24th)\n(using WTCS and world-cups events)"

    fig.suptitle(
        title,
        fontsize=18
    )

    plt.tight_layout()
    add_watermark(fig)
    plt.savefig(str(res_dir / "swim_gaps.png"), dpi=300)
    # plt.savefig(str(res_dir / "swim_gaps-wcs.png"), dpi=300)
    # plt.savefig(str(res_dir / "swim_gaps_20-24-wcs.png"), dpi=300)
    # plt.savefig(str(res_dir / "swim_gaps_20-24.png"), dpi=300)

    plt.show()


def process_event_country(df):
    for event_cat in ["wcs", "world-cup", "all"]:
        df_ = df.copy()
        if event_cat != "all":
            df_ = df[df["event_category"] == event_cat]
        value_counts = df_["event_country_noc"].value_counts()

        df_table = pd.DataFrame({
            "COUNTRY": [f"{country} ( {country_emojis[country]} )" if country in country_emojis else country for country
                        in value_counts.index],
            "COUNT": value_counts.values
        })

        def f_venue(row):
            country_noc = row["COUNTRY"][:3]
            # return ', '.join(set(df_[df_["event_country_noc"] == row["Country"][:3]]["event_venue"].unique()))
            venue_dict = df_[df_["event_country_noc"] == country_noc]["event_venue"].value_counts().to_dict()
            # sort by values descending
            venue_dict = dict(sorted(venue_dict.items(), key=lambda item: item[1], reverse=True))
            # create "k1(v1) k2(v2) k3(v3)"
            return ', '.join([f"{k} ({v})" for k, v in venue_dict.items()])

        df_table["VENUES"] = df_table.apply(f_venue, axis=1)
        print(f"\n\n{event_cat.upper()}")
        print(df_table.to_markdown(
            index=False,
            colalign=["center"] * len(df_table.columns)
        ))


def process_event_dates(df):

    durations_all = {}

    for event_cat in ["wcs", "world-cup"]:
        durations = {}
        df_ = df[df["event_category"] == event_cat]
        table_info = []
        for year_group in df_.groupby("event_year"):
            df_tmp = year_group[1].sort_values(by="event_date_m")

            first_event_date = df_tmp["event_date_m"].iloc[0][5:]
            first_country_noc = df_tmp["event_country_noc"].iloc[0]
            first_country_emoji = country_emojis[first_country_noc] if first_country_noc in country_emojis else first_country_noc
            first_event_listing = df_tmp["event_listing"].iloc[0]
            first_event_venue = df_tmp["event_venue"].iloc[0]

            last_event_date = df_tmp["event_date_m"].iloc[-1][5:]
            last_country_noc = df_tmp["event_country_noc"].iloc[-1]
            last_country_emoji = country_emojis[last_country_noc] if last_country_noc in country_emojis else last_country_noc
            last_event_listing = df_tmp["event_listing"].iloc[-1]
            last_event_venue = df_tmp["event_venue"].iloc[-1]

            last_event_venue = last_event_venue.replace("Cannigione, Arzachena", "Arzachena")
            first_event_venue = first_event_venue.replace("Cannigione, Arzachena", "Arzachena")

            last_day = int(last_event_date[:2]) * 30 + int(last_event_date[3:5])
            first_day = int(first_event_date[:2]) * 30 + int(first_event_date[3:5])
            duration = last_day - first_day
            durations[year_group[0]] = duration
            duration_months = round(duration / 30, 1)
            symbol = "_" if year_group[0] in [2020, 2021, 2022] else ""
            table_info.append({
                "Year": f"{symbol}{year_group[0]}{symbol}",
                "Num. events": f"{symbol}{len(df_tmp)}{symbol}",
                "Season duration": f"{symbol}{duration} days (~ {duration_months} m){symbol}",
                "Start": f"{symbol}**{first_event_date[:2]}**{first_event_date[-3:]}{symbol}",
                "End": f"{symbol}**{last_event_date[:2]}**{last_event_date[-3:]}{symbol}",
                "First event": f'{symbol}[{first_event_venue} ( {first_country_emoji} )]({first_event_listing}){symbol}',
                "Last event": f'{symbol}[{last_event_venue} ( {last_country_emoji} )]({last_event_listing}){symbol}'
            })
            if duration == 0:
                table_info[-1]["Season duration"] = f"{symbol}{duration} days{symbol} ( :mask: :face_with_thermometer: )" # covid in 2020
        df_table = pd.DataFrame(table_info)
        if event_cat == "wcs":
            print("\n\n### World Series\n\n")
        else:
            print("\n\n### World Cup\n\n")
        print(df_table.to_markdown(
            index=False,
            colalign=["center"] * len(df_table.columns)
        ))
        durations_all[event_cat] = durations

    # plot durations

    fig, ax = plt.subplots(figsize=(16, 16))
    colours = {
        "wcs": "gold",
        "world-cup": "silver"
    }
    for event_cat, durations in durations_all.items():
        durations = {k: v for k, v in durations.items() if k < 2024}

        pre_covid_keys = [y for y in durations.keys() if y < 2020]
        pre_covid_vals = [durations[k] for k in pre_covid_keys]
        post_covid_keys = [y for y in durations.keys() if y >= 2022]
        post_covid_vals = [durations[k] for k in post_covid_keys]
        during_covid_keys = [2019, 2020, 2021, 2022, 2023]
        during_covid_vals = [durations[k] for k in during_covid_keys]
        kwargs = {
            "linestyle": "-",
            "linewidth": 5,
            "zorder": 1,
            "color": colours[event_cat],
        }
        ax.plot(
            pre_covid_keys,
            pre_covid_vals,
            label=(event_cat.replace("wcs", "world-serie") + "s").upper(),
            **kwargs
        )
        ax.plot(
            post_covid_keys,
            post_covid_vals,
            **kwargs
        )

        if during_covid_vals[1] == 0:
            during_covid_keys = during_covid_keys[2:]
            during_covid_vals = during_covid_vals[2:]

        ax.plot(
            during_covid_keys,
            during_covid_vals,
            **kwargs
        #     color=colours[event_cat],
        #     linestyle="dotted"
        )

        non_zero_d = {k: v for k, v in durations.items() if v > 0}
        ax.scatter(
            non_zero_d.keys(),
            non_zero_d.values(),
            marker="o",
            s=100,
            zorder=2,
            color="black"
        )

        # set x ticks to be durations.keys
        ax.set_xticks(list(durations.keys()))
        ax.set_xticklabels(durations.keys())

    ax.set_ylabel("Season duration (days)".upper(), fontsize=16)
    ax.set_xlabel("Year".upper(), fontsize=16)

    # add 365 as y tick to current ones
    ax.set_yticks(list(ax.get_yticks()) + [365])
    ax.set_ylim(0, 375)

    for i_month in range(13):
        # draw horizontal line
        ax.axhline(30 * i_month, color="black", linestyle="dotted", alpha=0.4)

    ax.tick_params(axis='both', which='major', labelsize=14)

    for suffix in ["w", "m"]:
        athlete_season_durations = json_load(Path(f"data/athlete_season_durations_{suffix}.json"))
        athlete_season_durations = {int(k): v for k, v in athlete_season_durations.items()}
        pre_covid_keys = [k for k in athlete_season_durations.keys() if k < 2020]
        pre_covid_vals = [athlete_season_durations[k] for k in pre_covid_keys]
        post_covid_keys = [k for k in athlete_season_durations.keys() if k >= 2021]
        post_covid_vals = [athlete_season_durations[k] for k in post_covid_keys]
        kwargs = {
            "linestyle": ":",
            "color": "deepskyblue" if suffix == "m" else "hotpink",
            "zorder": 3,
            "marker": "o",
            "markersize": 4
        }
        ax.plot(
            pre_covid_keys,
            pre_covid_vals,
            label=f"TOP-50 ATHLETES ({suffix.upper()})",
            **kwargs
        )
        ax.plot(
            post_covid_keys,
            post_covid_vals,
            **kwargs
        )

    ax.grid(axis="x", alpha=0.5)
    ax.legend(loc='upper right', fontsize=15)
    max_days = max(list(durations_all["wcs"].values()) + list(durations_all["world-cup"].values()))
    fig.suptitle(
        "SEASON DURATION"
        f"\nMax: {max_days} days ({max_days/(12*30):.0%} of the year)\n",
        fontsize=18
    )

    plt.tight_layout()
    add_watermark(fig)
    plt.savefig(str(res_dir / "season_duration.png"), dpi=300)

    plt.show()


def main():
    save_race_results()

    df = get_events_results()
    # df = pd.read_csv("tmp_results.csv")

    df = clean_results(df)
    df = compute_diff(df)
    df = add_year_and_event_cat(df)

    # process_sports(df.copy())
    process_results_wetsuit(df.copy())
    # process_results_w_vs_m(df.copy())
    # process_results_repeated_events(df.copy())
    # process_scenarios(df.copy())
    # process_sprint_finish(df.copy())
    # process_ages(df.copy())
    # process_sport_proportion(df.copy())
    # process_swim_gaps(df.copy())
    # process_event_country(df.copy())
    # process_event_dates(df.copy())  # make sure to reduce the min-participants: n_results_min


if __name__ == '__main__':
    main()
