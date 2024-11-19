import requests
import re

from utils import json_dump, json_load, data_dir


def correct_name(first_name, last_name):
    # trim spaces
    first_name = first_name.strip()
    last_name = last_name.strip()

    if ("Vladimir" == first_name) and ("Turbaevskiy" == last_name):
        first_name = "Volodimir"
        last_name = "Turbayivskyy"
    if ("Alexander" == first_name) and ("Brukhankov" == last_name):
        first_name = "Alexander"
        last_name = "Bryukhankov"
    if ("Dmitry" == first_name) and ("Polyansky" == last_name):
        first_name = "Dmitry"
        last_name = "Polyanskiy"
    if ("Carlos Javier" == first_name) and ("Quinchara Forero" == last_name):
        first_name = "Carlos"
        last_name = "Quinchara"
    if ("CarlosJavier" == first_name) and ("Quinchara Forero" == last_name):
        first_name = "Carlos"
        last_name = "Quinchara"
    if ("Vladimir" == first_name) and ("Turbayevskiy" == last_name):
        first_name = "Volodimir"
        last_name = "Turbayivskyy"
    if ("JoseMiguel" == first_name) and ("Perez" == last_name):
        first_name = "Jose Miguel"
        last_name = "Perez"
    if ("Javier" == first_name) and ("Gomez" == last_name):
        first_name = "Javier"
        last_name = "Gomez Noya"
    if ("Rostyslav" == first_name) and ("Pevtsov" == last_name):
        first_name = "Rostislav"
        last_name = "Pevtsov"
    if ("LasseNygaard" == first_name) and ("Priester" == last_name):
        first_name = "Lasse Nygaard"
        last_name = "Priester"
    if ("VetleBergsvik" == first_name) and ("Thorn" == last_name):
        first_name = "Vetle Bergsvik"
        last_name = "Thorn"

    if ("Andrea" == first_name) and ("Hewitt" == last_name):
        first_name = "Andrea"
        last_name = "Hansen"
    if ("Magali" == first_name) and ("Di Marco" == last_name):
        first_name = "Magali"
        last_name = "Di Marco Messmer"
    if ("Sarah" == first_name) and ("Groff" == last_name):
        first_name = "Sarah"
        last_name = "True"
    if ("Barbara" == first_name) and ("Riveros Diaz" == last_name):
        first_name = "Barbara"
        last_name = "Riveros"
    if (first_name == "Melanie") and (last_name == "Annaheim"):
        first_name = "Melanie"
        last_name = "Hauss"
    if (first_name == "Yuliya") and (last_name == "Sapunova"):
        first_name = "Yuliya"
        last_name = "Yelistratova"
    if (first_name == "Tomoko") and (last_name == "Sakimoto"):
        first_name = "Tomoko"
        last_name = "Sonoda"
    if (first_name == "Aileen") and (last_name == "Morrison"):
        first_name = "Aileen"
        last_name = "Reid"
    if (first_name == "Pamela") and (last_name == "Oliveira"):
        first_name = "Pamella"
        last_name = "Oliveira"
    if (first_name == "Lauren") and (last_name == "Campbell"):
        first_name = "Lauren"
        last_name = "Groves"
    if (first_name == "Radka") and (last_name == "Vodickova"):
        first_name = "Radka"
        last_name = "Kahlefeldt"
    if ("MaryBeth" == first_name) and ("Ellis" == last_name):
        first_name = "Mary Beth"
        last_name = "Ellis"
    if ("Jillian" == first_name) and ("Petersen" == last_name):
        first_name = "Jillian"
        last_name = "Elliott"
    if ("Jenna" == first_name) and ("Shoemaker" == last_name):
        first_name = "Jenna"
        last_name = "Parker"
    if ("Katie" == first_name) and ("Hursey" == last_name):
        first_name = "Katie"
        last_name = "Zaferes"
    if ("Lucy" == first_name) and ("Hall" == last_name):
        first_name = "Lucy"
        last_name = "Buckingham"
    if ("Marlene" == first_name) and ("Gomez-Islinger" == last_name):
        first_name = "Marlene"
        last_name = "Gomez-Göggel"
    if ("Zsanett" == first_name) and ("Bragmayer" == last_name):
        first_name = "Zsanett"
        last_name = "Kuttor-Bragmayer"
    if ("AlberteKjær" == first_name) and ("Pedersen" == last_name):
        first_name = "Alberte"
        last_name = "Pedersen"
    if ("RosaMaria" == first_name) and ("Tapia Vidal" == last_name):
        first_name = "Rosa Maria"
        last_name = "Tapia Vidal"

    return first_name, last_name


def get_ranking_via_web():
    """dirty but does the job"""

    for suffix in ["m", "w"]:
        saving_path = data_dir / f"web_years_id_rankings_{suffix}.json"

        _suffix = "male" if suffix == "m" else "female"

        if saving_path.exists():
            rankings = json_load(saving_path)
        else:
            rankings = {}

        for year in range(2009, 2025):
            if year == 2020:
                continue

            if str(year) in rankings:
                if len(rankings[str(year)]) > 0:
                    print(f"Skipping {year} because it is not empty")
                    continue

            print(f"\n\n\n{year}\n")
            ranking = []
            # URL of the webpage
            url = f"https://triathlon.org/rankings/world_triathlon_championship_series_{year}/{_suffix}"

            if year < 2020:
                url = f"https://triathlon.org/rankings/itu_world_triathlon_series_{year}/{_suffix}"
            if year == 2024:  # current ranking
                url = f"https://triathlon.org/rankings/itu_world_triathlon_series/{_suffix}"

            # Send a GET request to the webpage
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Get the content of the webpage
                content = response.text

                # Define the regex pattern
                pattern = re.compile(
                    r"<td><(?:strong|b)>(\d+\.?)</(?:strong|b)></td>\s*"
                    r"<td><a href=\"/athletes/profile/([^\"]+)\">([^<]+)</a></td>\s*"
                    r"<td><a href=\"/athletes/profile/[^\"]+\">([^<]+)</a></td>"
                )

                # Find all matches in the content
                matches = pattern.findall(content)

                if matches:
                    # Print the extracted information
                    for match in matches:
                        rank, url_part, first_name, last_name = match
                        first_name = first_name.replace(" ", "")
                        first_name, last_name = correct_name(first_name, last_name)
                        # url = f"/athletes/profile/{url_part}"
                        # print(f"Rank: {rank}, URL: {url}, First Name: {first_name}, Last Name: {last_name}")
                        ranking.append([None, first_name, last_name])
                else:
                    # Define the regex pattern
                    pattern = re.compile(
                        r"<td><strong>(\d+\.?)</strong></td>\s*"
                        r"<td><a href=\"/athletes/profile/(\d+)/[^\"]+\">([^<]+)</a></td>\s*"
                        r"<td><a href=\"/athletes/profile/\d+/[^\"]+\">([^<]+)</a></td>"
                    )

                    # Find all matches in the content
                    matches = pattern.findall(content)

                    if not matches:
                        pattern = re.compile(
                            r"<td><(?:strong|b)>(\d+\.?)</(?:strong|b)></td>\s*"
                            r"<td><a href=\"/athletes/profile/(\d+)/[^\"]+\">([^<]+)</a></td>\s*"
                            r"<td><a href=\"/athletes/profile/\d+/[^\"]+\">([^<]+)</a></td>"
                        )

                        # Find all matches in the content
                        matches = pattern.findall(content)
                        print(f"matches: {matches}")

                    if not matches:
                        pattern = re.compile(
                            r"<td>(\d+\.?)</td>\s*"
                            r"<td><a href='/athletes/profile/(\d+)/[^\"]+'>([^<]+)</a></td>\s*"
                            r"<td><a href='/athletes/profile/\d+/[^\"]+'>([^<]+)</a></td>"
                        )

                        # Find all matches in the content
                        matches = pattern.findall(content)
                        print(f"matches: {matches}")

                    # Print the extracted information
                    for match in matches:
                        rank, athlete_id, first_name, last_name = match
                        first_name, last_name = correct_name(first_name, last_name)
                        ranking.append([athlete_id, first_name, last_name])
                        # print(f"Rank: {rank}, Athlete ID: {athlete_id}, First Name: {first_name}, Last Name: {last_name}")

                    if not matches:
                        pattern = re.compile(
                            r"<td><(?:strong|b)>(\d+\.?)</(?:strong|b)></td>\s*"
                            r"<td><a href='/athletes/profile/\d+/[^\"]+'>([^<]+)</a></td>\s*"
                            r"<td><a href='/athletes/profile/\d+/[^\"]+'>([^<]+)</a></td>"
                        )

                        # Find all matches in the content
                        matches = pattern.findall(content)
                        print(f"matches: {matches}")
                        for match in matches:
                            rank, first_name, last_name = match
                            first_name, last_name = correct_name(first_name, last_name)
                            ranking.append([None, first_name, last_name])

                    if not matches:
                        pattern = re.compile(
                            r"<td><(?:strong|b)>(\d+\.?)</(?:strong|b)></td>\s*"
                            r"<td>([^<]+)</td>\s*"
                            r"<td>([^<]+)</td>\s*"
                        )

                        # Find all matches in the content
                        matches = pattern.findall(content)
                        print(f"matches: {matches}")
                        # Print the extracted information

                        for match in matches:
                            rank, first_name, last_name = match
                            first_name, last_name = correct_name(first_name, last_name)
                            ranking.append([None, first_name, last_name])

                print(f"{year} ranking length: {len(ranking)}")
                rankings[year] = ranking
            else:
                print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

            # save to json
            json_dump(rankings, saving_path)


def clean_rankings():
    athlete_ids_mapping = json_load(data_dir / "athlete_id_name_mapping.json")

    years_rankings = {}
    ranking_len = 50
    for suffix in ["m", "w"]:
        web_years_rankings = json_load(data_dir / f"web_years_id_rankings_{suffix}.json")
        for year, year_ranking in web_years_rankings.items():
            year_ranking = [x for x in year_ranking if (x[0] not in ["12721", "39175", '15849'])]
            if year == "2022":
                year_ranking = [x for x in year_ranking if (x[1] != "Jessica") and (x[2] != "Learmonth")]
            year_ranking = year_ranking[:ranking_len]
            if all(x[0] is not None for x in year_ranking):
                years_rankings[year] = year_ranking
            else:
                year_id_ranking = []
                print(f"looking for id for {year}")
                for _, to_find_first, to_find_last in year_ranking:
                    found = False
                    for a_id, (candidate_first, candidate_last) in athlete_ids_mapping.items():
                        if (candidate_first.lower() == to_find_first.lower()) and (
                                candidate_last.lower() == to_find_last.lower()):
                            year_id_ranking.append((a_id, to_find_first, to_find_last))
                            found = True
                            break
                    if not found:
                        print(f"Could not find id for {to_find_first} {to_find_last}")
                years_rankings[year] = year_id_ranking

        json_dump(years_rankings, data_dir / f"years_id_rankings_{suffix}.json")


if __name__ == '__main__':
    get_ranking_via_web()
    clean_rankings()
