import re

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from utils import cache_dir, res_dir, add_watermark
from utils_itu import get_athlete_info, get_request

# todo: is it the correct way to set the math fonts?
plt.rcParams["font.family"] = "monospace"  # todo: set in global config
plt.rcParams['mathtext.default'] = 'rm'
plt.rcParams['mathtext.fontset'] = 'cm'  # "stix


def get_rankings(ranking_id: int):
    saving_path = cache_dir / "rankings" / f"rankings_{ranking_id}.csv"
    saving_path.parent.mkdir(parents=True, exist_ok=True)
    # check if ranking_id has already been retrieved and saved
    if saving_path.exists():
        df = pd.read_csv(saving_path)
        return df

    url_suffix = f"rankings/{ranking_id}"
    res = get_request(url_suffix=url_suffix)
    df = pd.DataFrame(res["rankings"])
    df.to_csv(saving_path)
    return df


def main():
    df = None

    ranking_ids = list(range(11, 28))
    ranking_ids.extend(list(range(35, 44)))

    # ranking_ids = [15, 16]  # World Triathlon

    for ranking_id in ranking_ids:
        df_tmp = get_rankings(ranking_id=ranking_id)
        # print(df_tmp.head(5))

        # n_athletes = 10
        # for athlete in df_tmp[:n_athletes].itertuples():
        #     print(f"{athlete.rank:<3} {athlete.athlete_id:<7.0f} ({athlete.athlete_noc}) "
        #           f"({athlete.athlete_age:.0f}) ({athlete.dob}) {athlete.athlete_title}")

        if df is None:
            df = df_tmp
        else:
            df = pd.concat([df, df_tmp])

    print(f"len before cleaning: {len(df):,}")

    # remove duplicates based on athlete_id
    df = df.drop_duplicates(subset="athlete_id")
    print(f"len after drop_duplicates: {len(df):,}")

    # drop NaN as athlete_id
    df = df.dropna(subset="athlete_id")
    print(f"len after dropna on athlete_id: {len(df):,}")

    df.athlete_id = df.athlete_id.astype(int)
    print(df.athlete_id)

    infos = []

    for athlete_id in df.athlete_id:
        print(athlete_id)
        res = get_athlete_info(athlete_id=athlete_id)
        if res is None:
            print(f"ERROR: no data found for {athlete_id = }")
            continue
        infos.append(res)
        print(res["athlete_first"])
        print(res["athlete_last"])
        print(res["weight"])
        print(res["height"])
        print("---")
        # url = "https://api.triathlon.org/v1/athletes/athlete_id/stats"
        # url_suffix = f"athletes/{athlete_id}"
        # res = get_request(url_suffix=url_suffix)
        # print(res)

    df_infos = pd.DataFrame(infos)
    print(df_infos.columns)
    print(df_infos.weight)

    # consider only weight, height
    df_infos = df_infos[["athlete_id", "weight", "height", "athlete_gender", "athlete_age"]]
    print(df_infos.columns)
    print(f"len(df_infos): {len(df_infos):,}")

    # drop NaN
    df_infos = df_infos.dropna()

    # Function to clean weight strings
    def clean_float(x):
        cleaned = re.findall(r'\d+\.?\'?\d*', x)
        cleaned = ''.join(cleaned)
        return cleaned

    def clean_weight(w):
        w = clean_float(w)
        if not w:
            return None
        w = float(w)
        if w > 100:
            w = w / 2.205
        if w > 110:
            return None
        return w

    def clean_height(h):
        h = clean_float(h)
        if not h:
            return None
        h = h.replace("'", ".")
        h = float(h)
        if 1.3 < h < 2.1:
            h = h * 100
        if h < 10:
            h = h * 30.48
        if h > 210:
            return None
        if h < 130:
            return None
        return h

    # apply cleaning function to weight and height columns
    df_infos["cleaned_weight"] = df_infos["weight"].apply(clean_weight)
    df_infos["cleaned_height"] = df_infos["height"].apply(clean_height)

    # only consider the not NaN for cleaned_height and cleaned_weight
    df_infos = df_infos.dropna(subset=["cleaned_height", "cleaned_weight"])
    # compute the BMI
    df_infos["bmi"] = df_infos["cleaned_weight"] / (df_infos["cleaned_height"] / 100) ** 2

    # remove athletes with BMI > 100
    df_infos = df_infos[df_infos.bmi <= 25]

    print(f"{len(df_infos)} / {len(df)} = {len(df_infos) / len(df):.2%} of the athletes have a BMI info.")
    print(f"avg. age: {df_infos['athlete_age'].mean():.1f} (from {df_infos['athlete_age'].min()} to {df_infos['athlete_age'].max()})")

    # plot two histograms depending on athlete_gender
    kwargs = {
        "bins": "auto",
        "alpha": 0.5,
        "rwidth": 0.9,
        "density": True,
    }

    df_men = df_infos[df_infos.athlete_gender == "male"]
    df_women = df_infos[df_infos.athlete_gender == "female"]

    weight_men_mean = df_men['cleaned_weight'].mean()
    height_men_mean = df_men['cleaned_height'].mean()
    weight_women_mean = df_women['cleaned_weight'].mean()
    height_women_mean = df_women['cleaned_height'].mean()

    mean_men = df_men['bmi'].mean()
    std_men = df_men['bmi'].std()
    mean_women = df_women['bmi'].mean()
    std_women = df_women['bmi'].std()

    fig = plt.figure(figsize=(12, 12))

    plt.hist(df_women.bmi, color="violet", label=f"WOMEN ({len(df_women)})", **kwargs)
    plt.axvline(mean_women, color="violet", linestyle='-.', linewidth=2,
                label=f"mean women: {mean_women:.1f} ± {std_women:.1f}")

    plt.hist(df_men.bmi, color="deepskyblue", label=f"MEN ({len(df_men)})", **kwargs)
    plt.axvline(mean_men, color="deepskyblue", linestyle='-.', linewidth=2,
                label=f"mean men: {mean_men:.1f} ± {std_men:.1f}")

    plt.xticks(np.arange(int(min(df_infos.bmi)) - 1, int(max(df_infos.bmi)) + 1, 1))
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('$BMI = [mass (kg)] / [height (m)]^2$', fontsize=18)
    # plt.ylabel('%')
    # remove y labels
    plt.yticks([])
    plt.grid()
    plt.legend()

    plt.title(
        'BODY MASS INDEX'
        f"\n{len(df_infos):,} athletes"
        f"\n(Avg. women: {weight_women_mean:.1f}kg {height_women_mean:.1f}cm)"
        f"\n(Avg. men:   {weight_men_mean:.1f}kg {height_men_mean:.1f}cm)",
        fontsize=15
    )
    plt.tight_layout()
    add_watermark(fig, y=0.96)
    plt.savefig(str(res_dir / "bmi.png"), dpi=300)
    plt.show()

    # plot weights and heights for men and women
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    axes[0].hist(df_women.cleaned_weight, color="violet", label=f"WOMEN ({len(df_women)})", **kwargs)
    axes[0].axvline(weight_women_mean, color="violet", linestyle='-.', linewidth=2,
                label=f"mean women: {weight_women_mean:.1f}kg")

    axes[0].hist(df_men.cleaned_weight, color="deepskyblue", label=f"MEN ({len(df_men)})", **kwargs)
    axes[0].axvline(weight_men_mean, color="deepskyblue", linestyle='-.', linewidth=2,
                label=f"mean men: {weight_men_mean:.1f}kg")

    axes[0].set_xticks(np.arange(int(min(df_infos.cleaned_weight)) - 1, int(max(df_infos.cleaned_weight)) + 1, 2))
    axes[0].grid(axis='y', alpha=0.75)
    axes[0].set_xlabel('WEIGHT (kg)', fontsize=18)
    axes[0].set_yticks([])
    axes[0].grid()
    axes[0].legend()

    axes[1].hist(df_women.cleaned_height, color="violet", label=f"WOMEN ({len(df_women)})", **kwargs)
    axes[1].axvline(height_women_mean, color="violet", linestyle='-.', linewidth=2,
                label=f"mean women: {height_women_mean:.1f}cm")

    axes[1].hist(df_men.cleaned_height, color="deepskyblue", label=f"MEN ({len(df_men)})", **kwargs)
    axes[1].axvline(height_men_mean, color="deepskyblue", linestyle='-.', linewidth=2,
                label=f"mean men: {height_men_mean:.1f}cm")

    axes[1].set_xticks(np.arange(int(min(df_infos.cleaned_height)) - 1, int(max(df_infos.cleaned_height)) + 1, 2))
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=90)
    axes[1].grid(axis='y', alpha=0.75)
    axes[1].set_xlabel('HEIGHT (cm)', fontsize=18)
    axes[1].set_yticks([])
    axes[1].grid()
    axes[1].legend()

    fig.suptitle(
        'WEIGHTS AND HEIGHTS'
        f"\n{len(df_infos):,} athletes",
        fontsize=15
    )

    plt.tight_layout()
    add_watermark(fig, y=0.95)
    plt.savefig(str(res_dir / "weight_height.png"), dpi=300)
    plt.show()


if __name__ == '__main__':
    main()
