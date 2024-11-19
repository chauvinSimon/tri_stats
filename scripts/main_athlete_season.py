"""
want to use "World Triathlon Rankings (formerly ITU Points List)" - but missing years (2018, 2020, 2021, 2023)
using the "World Triathlon Championship Series Rankings" instead

https://triathlon.org/rankings/archive
# todo: where to find 2023?
"""

from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd
from scipy.stats import norm

from utils import json_load, json_dump, res_dir, interpolate_colors, cache_dir, data_dir, country_emojis, add_watermark, \
    load_config
from utils_itu import get_request, category_mapping

plt.rcParams["font.family"] = "monospace"  # todo: set in global config
plt.rcParams['mathtext.default'] = 'rm'
plt.rcParams['mathtext.fontset'] = 'cm'  # "stix

config = load_config()
suffix = config["seasons"]["suffix"]

# https://triathlon.org/rankings/archive

years = [
    2009,
    2010,
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,  # no data
    2019,
    # 2020,  # no data. no series data
    2021,  # no ITU data
    2022,
    2023,  # no data
    2024
]

years_id_rankings_file = data_dir / f"years_id_rankings_{suffix}.json"
athlete_ids_mapping = json_load(data_dir / "athlete_id_name_mapping.json")
ranking_len = 50


# def create_id_ranking():
#     years_name_rankings = json_load(data_dir / f"years_name_rankings_{suffix}.json")
#
#     if years_id_rankings_file.exists():
#         years_id_rankings = json_load(years_id_rankings_file)
#     else:
#         years_id_rankings = {}
#
#     for year in years:
#         if str(year) in years_id_rankings:
#             if len(years_id_rankings[str(year)]) == ranking_len:
#                 continue
#
#         year_id_ranking = []
#         year_name_ranking = years_name_rankings[str(year)]
#         assert len(year_name_ranking) == ranking_len, f"{year} has {len(year_name_ranking)} athletes"
#
#         for to_find_first, to_find_last in year_name_ranking:
#             found = False
#             for a_id, (candidate_first, candidate_last) in athlete_ids_mapping.items():
#                 if (candidate_first.lower() == to_find_first.lower()) and (
#                         candidate_last.lower() == to_find_last.lower()):
#                     year_id_ranking.append((a_id, to_find_first, to_find_last))
#                     found = True
#                     break
#             if not found:
#                 print(f"Could not find id for {to_find_first} {to_find_last}")
#
#         years_id_rankings[str(year)] = year_id_ranking
#         json_dump(years_id_rankings, years_id_rankings_file)


def count_days_until(full_date_str):
    """
    Count the number of days in the year until the given date.

    Parameters:
    date_str (str): The date in 'MM-DD' format.

    Returns:
    int: The number of days from the start of the year to the given date.
    """
    # Parse the date
    date = datetime.strptime(full_date_str, "%Y-%m-%d")

    # Calculate the number of days from the start of the year
    day_of_year = date.timetuple().tm_yday

    return day_of_year

def update_athletes(years_to_update: list):
    for _suffix in ["m", "w"]:
        years_id_rankings = json_load(data_dir / f"years_id_rankings_{_suffix}.json")
        for year in years_to_update:
            for i_athlete, athlete_info in enumerate(years_id_rankings[str(year)]):
                print(f"updating #{i_athlete} {athlete_info} ...")
                athlete_id = athlete_info[0]
                url_suffix = f"athletes/{athlete_id}/results?per_page=1000"
                athlete_results_res = get_request(url_suffix)

                athlete_results_file = cache_dir / f"athletes_results/{athlete_id}.json"
                athlete_results_file.parent.mkdir(parents=True, exist_ok=True)
                json_dump(athlete_results_res, athlete_results_file)


def get_athlete_seasons(athlete_ids):
    all_dfs = []
    i_athlete = 0
    for athlete_id in athlete_ids:
        i_athlete += 1
        if i_athlete > 100:
            break
        print(f"{athlete_id}: {athlete_ids_mapping[athlete_id]}")
        athlete_results_file = cache_dir / f"athletes_results/{athlete_id}.json"
        if athlete_results_file.exists():
            athlete_results_res = json_load(athlete_results_file)
        else:
            url_suffix = f"athletes/{athlete_id}/results?per_page=1000"
            athlete_results_res = get_request(url_suffix)
            athlete_results_file.parent.mkdir(parents=True, exist_ok=True)
            json_dump(athlete_results_res, athlete_results_file)

        if athlete_results_res is None:
            print(f"ERROR: no data found for {athlete_id = }")

        athlete_results_info = []
        for result in athlete_results_res:
            event_category = None
            for event_cat in result["event_categories"]:
                if event_cat["cat_id"] in category_mapping.keys():
                    event_category = category_mapping[event_cat["cat_id"]]
                    continue
            if event_category is None:
                continue
            position = result["position"]
            if position == "DNS":
                continue
            athlete_results_info.append(
                {
                    "event_id": result["event_id"],
                    "event_name": result["event_title"],
                    "event_category": event_category,
                    "event_date": result["event_date"],
                    "event_year": int(result["event_date"][:4]),
                    "event_date_day": count_days_until(result["event_date"]),
                    "position": position
                }
            )
        # print(len(athlete_results_info))
        df = pd.DataFrame(athlete_results_info)
        df = df.groupby("event_year").agg(
            event_count=("event_id", "count"),
            wcs_event_count=("event_category", lambda x: (x == "wcs").sum()),
            wc_event_count=("event_category", lambda x: (x == "world-cup").sum()),
            games_event_count=("event_category", lambda x: (x == "games").sum()),
            first_date=("event_date", "min"),
            last_date=("event_date", "max"),
            season_start=("event_date_day", lambda x: x.min()),
            season_duration_days=("event_date_day", lambda x: x.max() - x.min()),
            wcs_positions=("position", lambda x: list(x[df['event_category'] == "wcs"])),
            wcs_days=("event_date_day", lambda x: list(x[df['event_category'] == "wcs"])),
            wc_positions=("position", lambda x: list(x[df['event_category'] == "world-cup"])),
            wc_days=("event_date_day", lambda x: list(x[df['event_category'] == "world-cup"])),
        )

        all_dfs.append(df)
    return all_dfs


def plot_athlete_seasons(years_dfs):
    n_years = len(years)
    for year in years:
        assert len(years_dfs[year]) == ranking_len

    fig, axes = plt.subplots(
        nrows=ranking_len + 2,
        ncols=n_years,
        figsize=(16, 16),
        gridspec_kw={'wspace': 0.0, 'hspace': 0}
    )
    # fig = plt.figure()
    # axes = fig.add_subplot(ranking_len, n_years, 1)

    durations = {
        year: df_year['season_duration_days'].mean()
        for year, df_year in years_dfs.items()
    }
    duration_colours = interpolate_colors(
        color1="mistyrose",
        color2="lightcoral",
        values=list(durations.values()), output_format="rgb"
    )
    event_counts = {
        year: df_year['event_count'].mean()
        for year, df_year in years_dfs.items()
    }
    duration_n_events = interpolate_colors(
        color1="mistyrose",
        color2="lightcoral",
        values=list(event_counts.values()), output_format="rgb"
    )

    # dump to file
    json_dump(durations, data_dir / f"athlete_season_durations_{suffix}.json")

    for i_year, year in enumerate(years):
        df_year = years_dfs[year]

        axes[0, i_year].text(x=365/2, y=0.5, s=f"~{durations[year]:.0f} days", va="center", ha="center")
        axes[1, i_year].text(365/2, 0.5, f"~{event_counts[year]:.1f} races", va="center", ha="center")

        # axes[0, i_year].axis("off")  # this removes the facecolor
        # axes[1, i_year].axis("off")

        axes[0, i_year].set_facecolor(duration_colours[i_year])
        axes[1, i_year].set_facecolor(duration_n_events[i_year])

        for i_athlete, (_, row) in enumerate(df_year.iterrows()):
            ax = axes[i_athlete + 2, i_year]

            marker_size = 20

            for i_cat, cat in enumerate(["wcs", "wc"]):
                marker = "^" if cat == "wcs" else "v"
                color = "dodgerblue" if cat == "wcs" else "limegreen"
                color_podium = "red" if cat == "wcs" else "darkorange"
                if len(row[f"{cat}_positions"]) == 0:
                    ax.set_facecolor("lightyellow" if cat == "wcs" else "lightcyan")

                for day, pos in zip(row[f"{cat}_days"], row[f"{cat}_positions"]):
                    if isinstance(pos, str):
                        continue
                    _cat = "w-cup" if cat == "wc" else "wtcs"
                    label = f"{_cat}-podium" if pos < 4 else f"{_cat}"
                    ax.scatter(
                        x=[day],
                        y=[i_cat],
                        marker=marker,
                        s=marker_size,
                        zorder=3 if pos < 4 else 4,
                        color=color_podium if pos < 4 else color,
                        label=label
                    )
                    write_pos = False
                    if write_pos:
                        ax.text(
                            day,
                            i_cat,
                            pos,
                            ha="center",
                            va="center",
                            fontsize=7,
                            color="white" if pos > 3 else "black",
                            zorder=4
                        )

    for i_year, year in enumerate(years):
        for i_row in range(ranking_len + 2):
            ax = axes[i_row, i_year]

            # y
            ax.set_ylim(-1, 2)
            ax.set_yticklabels([])
            ax.set_yticks([])
            if i_year == 0 and (i_row > 1):
                ax.set_ylabel(i_row - 1, rotation=0, ha="right", va="center", fontsize=8)

            # x
            ax.set_xlim(0, 365)
            ax.set_xticks(range(0, 365, 30))
            ax.set_xticklabels([])
            if i_row > 1:
                ax.grid()

            if i_row == ranking_len + 2 - 1:
                # add month between ticks
                ax.set_xticklabels('')
                ax.set_xticks(range(15, 365, 30), minor=True)
                ax.tick_params(axis='x', colors='white', which='major')
                ax.set_xticklabels(["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"], minor=True, fontsize=6)

            if i_row == 0:
                ax.set_title(year)

    lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    # grab unique labels
    unique_labels = ["wtcs", "w-cup", "wtcs-podium", "w-cup-podium"]
    # assign labels and legends in dict
    legend_dict = dict(zip(labels, lines))
    # sort legend
    legend_dict = {k: legend_dict[k] for k in unique_labels}
    # query dict based on unique labels
    unique_lines = [legend_dict[x] for x in unique_labels]

    import matplotlib.patches as mpatches
    wtcs_patch = mpatches.Patch(color='lightcyan', edgecolor='black')
    unique_lines.append(wtcs_patch)
    unique_labels.append('wtcs only')

    wc_patch = mpatches.Patch(color='lightyellow', edgecolor='black')
    unique_lines.append(wc_patch)
    unique_labels.append('w-cups only')

    fig.legend(unique_lines, unique_labels, scatterpoints=1, loc='upper right', ncol=3)

    fig.suptitle(
        "ATHLETE SEASONS",
        fontsize=18
    )
    # ax = fig.add_subplot(111)  # The big subplot
    # ax.set_ylabel('common ylabel')

    plt.tight_layout()
    add_watermark(fig, y=0.98, x=0.1)
    plt.savefig(str(res_dir / f"athlete_season_duration_{suffix}.png"), dpi=300)

    plt.show()


def get_athlete_nocs(athlete_ids):
    athlete_nocs_file = data_dir / "athlete_nocs.json"
    athlete_nocs = json_load(athlete_nocs_file)

    nocs = []
    for id_ in athlete_ids:
        if id_ in athlete_nocs:
            nocs.append(athlete_nocs[id_])
        else:
            print(f"Could not find noc for {id_}")

    return nocs


def print_nocs(years_nocs):
    from collections import Counter
    for year, nocs in years_nocs.items():
        counter = Counter(nocs)
        # print most represented noc
        highest_count = counter.most_common(1)[0]
        noc = highest_count[0]
        c = highest_count[1]
        print(f"{year} - {country_emojis[noc] if noc in country_emojis else noc} ({c} / {len(nocs)} = {c / len(nocs) * 100:.1f}%)")
        # print all indices of noc in nocs
        for i, n in enumerate(nocs):
            if n == noc:
                print(i+1)

    # compute means
    all_nocs = [y for yl in years_nocs.values() for y in yl]

    nocs_counter = Counter(all_nocs)
    print(nocs_counter.most_common(10))
    print(nocs_counter.values())
    d_percent = {k: v / len(all_nocs) for k, v in dict(nocs_counter.most_common(1000)).items()}
    d_percent = {k: v for k, v in d_percent.items() if v > 0.00}

    print("Considering nations with an high percentage of athletes in top-50, let's compute **how many athletes miss the olympics** because of **the _'max-3-rule'_**:")
    print(f"- {'Men:' if suffix == 'm' else 'Women:'}")
    n_spots = 55
    for k, v in d_percent.items():
        if v > 3/n_spots:
            emp = ""
            plural = ""
            if v > 4/n_spots:
                emp = "**"
                plural = "s"
            print(f"  - {country_emojis[k] if k in country_emojis else k} : ~{v:.1%} => {emp}~{n_spots * v - 3:.1f}{emp} top-50 athlete{plural} rejected. :disappointed:")

    df_lines = []
    p_max = int(100 * max(d_percent.values())) + 1
    for bin_min, bin_max in zip(range(p_max, -1, -1), range(p_max + 1, 0, -1)):
        sub_d = {k: v for k, v in d_percent.items() if (100 * v >= bin_min) and (100 * v < bin_max)}
        print(f"{bin_min}-{bin_max}: {sub_d}")

        join_str = " ".join([f" {country_emojis[k] if k in country_emojis else k}  ({v:.1%})" for k, v in sub_d.items()])
        df_lines.append({
            "index": bin_min,
            f"RANGE (%) ({suffix.upper()})": f"{bin_min}-{bin_max}",
            f"NATIONS ({suffix.upper()})": join_str if join_str else " "
        })
    df_table = pd.DataFrame(df_lines)

    # save df
    df_table.to_csv(data_dir / f"nocs_{suffix}.csv", index=False)

    if (data_dir / f"nocs_m.csv").exists() and (data_dir / f"nocs_w.csv").exists():
        df_m = pd.read_csv(data_dir / f"nocs_m.csv")
        df_m.index = list(df_m["index"])
        df_m.drop("index", axis=1, inplace=True)
        print("- MEN:" + ",".join(df_m.iloc[:6]["NATIONS (M)"].tolist()))

        df_w = pd.read_csv(data_dir / f"nocs_w.csv")
        df_w.index = list(df_w["index"])
        df_w.drop("index", axis=1, inplace=True)
        df_table = pd.concat([df_m, df_w], axis=1).sort_index(ascending=False)
        print("- WOMEN:" + ",".join(df_w.iloc[:6]["NATIONS (W)"].tolist()))

        # reorder columns
        df_table = df_table[
            ["RANGE (%) (W)", "RANGE (%) (M)", "NATIONS (W)", "NATIONS (M)"]
        ]

        if df_w.index.max() > df_m.index.max():
            df_table.drop(["RANGE (%) (M)"], axis=1, inplace=True)
            df_table.rename(columns={"RANGE (%) (W)": "RANGE (%)"}, inplace=True)
        else:
            df_table.drop(["RANGE (%) (W)"], axis=1, inplace=True)
            df_table.rename(columns={"RANGE (%) (M)": "RANGE (%)"}, inplace=True)

        # replace NaN
        df_table = df_table.fillna(" ")

    print(df_table.to_markdown(
        index=False,
        colalign=["center"] * len(df_table.columns)
    ))


def plot_end_of_career():
    all_ids = set()
    min_num_races = 10
    year_limit = 2019

    for _suffix in ["m", "w"]:
        years_id_rankings = json_load(data_dir / f"years_id_rankings_{_suffix}.json")
        for year in years:
            year_id_ranking = years_id_rankings[str(year)]
            athlete_ids = [a_id for a_id, _, _ in year_id_ranking]
            # add to the set
            all_ids |= set(athlete_ids)

    print(f"{len(all_ids):,} athletes")
    athletes_infos = []
    for athlete_id in all_ids:
        print(f"{athlete_id}: {athlete_ids_mapping[athlete_id]}")
        athlete_results_file = cache_dir / f"athletes_results/{athlete_id}.json"
        if athlete_results_file.exists():
            athlete_results_res = json_load(athlete_results_file)
        else:
            url_suffix = f"athletes/{athlete_id}/results?per_page=1000"
            athlete_results_res = get_request(url_suffix)
            athlete_results_file.parent.mkdir(parents=True, exist_ok=True)
            json_dump(athlete_results_res, athlete_results_file)

        if athlete_results_res is None:
            print(f"ERROR: no data found for {athlete_id = }")

        if len(athlete_results_res) < min_num_races:
            continue

        # filter res: only keep world-cups, wtcs and major games
        athlete_results_res_cleaned = []
        for r in athlete_results_res:
            if any(cat["cat_id"] in category_mapping.keys() for cat in r["event_categories"]):
                athlete_results_res_cleaned.append(r)
        assert len(athlete_results_res_cleaned) < len(athlete_results_res)
        athlete_results_res = athlete_results_res_cleaned

        if len(athlete_results_res) < min_num_races:
            continue

        last_race_date = None
        for result in athlete_results_res:
            event_date = result["event_date"]
            if last_race_date is None or last_race_date < event_date:
                last_race_date = event_date
        y_last_race = int(last_race_date[:4])
        if y_last_race > year_limit:
            continue

        athlete_file = cache_dir / f"athletes/{athlete_id}.json"
        if athlete_file.exists():
            athlete_info = json_load(athlete_file)
        else:
            url_suffix = f"athletes/{athlete_id}"
            athlete_info = get_request(url_suffix)
            athlete_file.parent.mkdir(parents=True, exist_ok=True)
            json_dump(athlete_info, athlete_file)

        yob = athlete_info["athlete_yob"]  # todo
        age = y_last_race - yob
        athletes_infos.append(
            {
                "age": age,
                "gender": athlete_info["athlete_gender"],
                "first": athlete_info["athlete_first"],
                "last": athlete_info["athlete_last"],
                "id": athlete_id,
                "noc": athlete_info["athlete_noc"],
                "num_races": len(athlete_results_res),
            }
        )
    df = pd.DataFrame(athletes_infos)

    df.sort_values(by="age", inplace=True)

    df["emoji"] = df["noc"].apply(lambda x: country_emojis[x] if x in country_emojis else x)
    df["txt"] = df.apply(lambda x: f"{x['first']} {x['last']} ( {x['emoji']} ): **{x['age']}y**, {x['num_races']} races.", axis=1)

    df_table = df.copy()
    df_table["first_last"] = df_table["first"] + " " + df_table["last"]
    df_table = df_table[["first_last", "emoji", "age", "num_races"]]
    # rename columns
    df_table.rename(columns={
        "first_last": "ATHLETE",
        "emoji": "COUNTRY",
        "age": "AGE OF LAST RACE",
        "num_races": "NUMBER OF RACES",
    }, inplace=True)
    print(df_table.to_markdown(
        index=False,
        colalign=["center"] * len(df_table.columns)
    ))

    # for txt in df["txt"].tolist():
    #     print(f"- {txt}")

    age_min = 25
    print(f"- **`<{age_min}` years**:")
    for txt in df[df["age"] < age_min]["txt"].tolist():
        print(f"  - {txt}")

    age_max = 38
    print(f"- **`>{age_max}` years**:")
    for txt in df[df["age"] > age_max]["txt"].tolist():
        print(f"  - {txt}")

    age_mean = df["age"].mean()
    age_median = df["age"].median()
    age_std = df["age"].std()
    age_mean_male = df[df["gender"] == "male"]["age"].mean()
    age_std_male = df[df["gender"] == "male"]["age"].std()
    age_mean_female = df[df["gender"] == "female"]["age"].mean()
    age_std_female = df[df["gender"] == "female"]["age"].std()
    print(f"Mean = {age_mean:.1f}y")
    print(f"Median = {age_median:.1f}y")
    print(f"Std = {age_std:.1f}y")
    print(f"Male mean = {age_mean_male:.1f}y std = {age_std_male:.1f}y")
    print(f"Female mean = {age_mean_female:.1f}y std = {age_std_female:.1f}y")

    # plot df[age] distribution
    fig = plt.figure(figsize=(10, 10))
    bins = np.arange(int(min(df["age"]))-1, int(max(df["age"]))+1, 1)
    kwargs = {
        "density": True,
        "bins": bins,
    }
    plt.hist(df["age"], color="green", alpha=0.5, label=f"All ({len(df):,}) (avg: {age_mean:.1f}y)", **kwargs)
    plt.hist(df[df["gender"] == "female"]["age"], color="magenta", alpha=0.5, label=f"Women ({len(df[df['gender'] == 'female']):,})  (avg: {age_mean_female:.1f}y)", histtype="step", linewidth=2, **kwargs)
    plt.hist(df[df["gender"] == "male"]["age"], color="mediumblue", alpha=0.5, label=f"Men ({len(df[df['gender'] == 'male']):,}) (avg: {age_mean_male:.1f}y)", histtype="step", linewidth=1, **kwargs)

    plt.axvline(age_mean, color="orange", linestyle="-", linewidth=1, label=f"Mean = {age_mean:.1f}y")
    plt.axvline(age_median, color="orange", linestyle=":", linewidth=1, label=f"Median = {age_median:.1f}y")

    mu, std = norm.fit(df["age"])
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'gray', linewidth=1, linestyle="-", label=f"Normal distribution ($\mu={mu:.1f}$, $\sigma={std:.1f}$)")

    plt.grid()
    plt.legend()
    plt.xlabel("Age")
    plt.xticks(range(min(df["age"]) - 1, max(df["age"]) + 1, 2))
    plt.ylabel("Percentage")
    # format y as percentage
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

    plt.title(f"AGE OF LAST RACE"
              f"\n{len(df)} athletes who:"
              f"\n1) have raced at least {min_num_races} WTCS, world-cups or major games."
              f"\n2) have not raced since {year_limit}.")
    plt.tight_layout()
    add_watermark(fig)
    plt.savefig(res_dir / "ages_of_last_race.png")
    plt.show()


def main():
    # create_id_ranking()

    years_id_rankings = json_load(years_id_rankings_file)

    years_dfs = {}

    years_nocs = {}

    for year in years:
        print(year)

        year_id_ranking = years_id_rankings[str(year)]
        athlete_ids = [a_id for a_id, _, _ in year_id_ranking]

        # athlete_ids2 = []
        # for id_ in athlete_ids:
        #     if id_ in athlete_ids_mapping:
        #         athlete_ids2.append(id_)
        #     else:
        #         print(f"Could not find id for {id_}")
        all_dfs = get_athlete_seasons(athlete_ids)

        for i_df, _df in enumerate(all_dfs):
            try:
                _ = _df.loc[int(year)]
            except Exception as e:
                print(f"{i_df} {year} {year_id_ranking[i_df]}: no race found")
                print(e)
        df_year = pd.DataFrame([_df.loc[int(year)] for _df in all_dfs])
        assert len(df_year) == ranking_len, f"{year} has {len(df_year)} athletes"

        # add columns
        df_year["athlete_id"] = [a_id for a_id, _, _ in year_id_ranking]
        df_year["athlete_first"] = [a_first for _, a_first, _ in year_id_ranking]
        df_year["athlete_last"] = [a_last for _, _, a_last in year_id_ranking]

        # reset index
        # df_year = df_year.reset_index()

        years_dfs[year] = df_year
        # print(df_year)

        years_nocs[year] = get_athlete_nocs(athlete_ids)

    print_nocs(years_nocs)
    plot_athlete_seasons(years_dfs)


if __name__ == '__main__':
    # update_athletes(years_to_update=[2024])
    main()
    # plot_end_of_career()
