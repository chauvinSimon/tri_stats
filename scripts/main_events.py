from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd
import seaborn as sns

from scripts.utils_events import get_events_df

from scripts.utils_events import drop_outliers, seconds_to_h_min_sec
from utils import data_dir, json_load, res_dir, country_emojis, add_watermark, load_config, ignored_dir


def process_results_wetsuit(
        df,
        swim_diff_percent_max: float,
        distance_categories,
        sport_outliers
):
    # ? ignore World Cups
    # df = df[df["event_category"] != "world-cup"]

    # remove outliers?
    outliers = df[df["swim_diff_percent"] >= swim_diff_percent_max]
    print(f"{len(outliers)} swim outliers:")
    print(list(outliers["event_listing"]))
    print(list(outliers["event_title"]))
    print(outliers["swim_diff_percent"])
    df = df[df["swim_diff_percent"] < swim_diff_percent_max]

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
    for ax in axes.flat:
        ax.xaxis.set_major_formatter(PercentFormatter(1))
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
    for row in swim_diff_percent_women_fast.itertuples():
        print(f"{row.event_venue} ( {country_emojis[row.event_country_noc] if row.event_country_noc in country_emojis else row.event_country_noc} ) ({row.event_year}): {row.swim_diff_percent:.1%} {row.event_listing}")
    print(swim_diff_percent_women_fast.event_venue.tolist())
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

    # remove Sydney 2012 outlier
    swim_diff_percent_women_fast = swim_diff_percent_women_fast[swim_diff_percent_women_fast["event_id"] != 54370]
    # remove Haeundae 2021 outlier
    swim_diff_percent_women_fast = swim_diff_percent_women_fast[swim_diff_percent_women_fast["event_id"] != 154591]

    # ? ignore World Cups for women_fast
    swim_diff_percent_women_fast = swim_diff_percent_women_fast[
        swim_diff_percent_women_fast["event_category"] != "world-cup"]

    if len(swim_diff_percent_women_fast) == 0:
        print("no data where [women with wetsuit] and [men without wetsuit]")

    else:

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
            drop_outliers(df[df['prog_distance_category'] == distance_category], i_sport=0, sport_outliers=sport_outliers)[f"swim_mean_m"].max(),
            drop_outliers(df[df['prog_distance_category'] == distance_category], i_sport=0, sport_outliers=sport_outliers)[f"swim_mean_w"].max()
        ) + 10

        x_min = min(
            drop_outliers(df[df['prog_distance_category'] == distance_category], i_sport=0, sport_outliers=sport_outliers)[f"swim_mean_m"].min(),
            drop_outliers(df[df['prog_distance_category'] == distance_category], i_sport=0, sport_outliers=sport_outliers)[f"swim_mean_w"].min()
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
            print(f"\timprove_percent = {improve_percent :.2%}")
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


def process_sports(df, distance_categories, sports, sport_outliers):
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(16, 16))

    fig.suptitle(
        f"TIMES AND PACES\n({len(df)} events)\n 5th-9th IN EACH LEG",
        # f"TIMES AND PACES\n({len(df)} events)\nTOP-3 IN EACH LEG",
        # f"TIMES AND PACES\n({len(df)} events)\nTOP-10 IN EACH LEG",
        fontsize=20
    )

    for i_distance_category, distance_category in enumerate(distance_categories):
        for i_sport, sport in enumerate(sports):

            x_max = max(
                drop_outliers(df[df['prog_distance_category'] == distance_category], i_sport=i_sport, sport_outliers=sport_outliers)[f"{sport}_mean_m"].max(),
                drop_outliers(df[df['prog_distance_category'] == distance_category], i_sport=i_sport, sport_outliers=sport_outliers)[f"{sport}_mean_w"].max()
            ) + 10

            x_min = min(
                drop_outliers(df[df['prog_distance_category'] == distance_category], i_sport=i_sport, sport_outliers=sport_outliers)[f"{sport}_mean_m"].min(),
                drop_outliers(df[df['prog_distance_category'] == distance_category], i_sport=i_sport, sport_outliers=sport_outliers)[f"{sport}_mean_w"].min()
            ) - 10

            for i_suffix, suffix in enumerate(["w", "m"]):
                colours = {
                    "w": "pink",
                    "m": "deepskyblue"
                }
                data = df[df['prog_distance_category'] == distance_category]
                data = drop_outliers(data, i_sport, sport_outliers=sport_outliers)
                data = data[f"{sport}_mean_{suffix}"]
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
    # plt.savefig(str(res_dir / "sports_paces_top3.png"), dpi=300)
    # plt.savefig(str(res_dir / "sports_paces_top10.png"), dpi=300)

    plt.show()


def process_results_w_vs_m(
        df,
        swim_diff_percent_max: float,
        sports,
        distance_categories
):
    # max_diff_percent = max(df[f"{sport}_diff_percent"].max() for sport in sports)
    max_diff_percent = 0.21
    max_diff_percent += 0.01

    # compute number of days since date, formatter as a string: YYYY-MM-DD
    first_year = int(min(df["event_date_m"].apply(lambda x: int(x[:4]))))

    df[f"event_date_since_{first_year}"] = df["event_date_m"].apply(
        lambda x: (datetime(int(x[:4]), int(x[5:7]), int(x[8:10])) - datetime(first_year, 1, 1)).days
    )

    for use_world_cup in [True, False]:
        df_2 = df.copy()
        if not use_world_cup:
            df_2 = df_2[df_2["event_category"] != "world-cup"]

        fig, axes = plt.subplots(nrows=len(sports), ncols=2, figsize=(16, 16))
        for i_distance_category, distance_category in enumerate(distance_categories):
            print(distance_category)
            for i_sport, sport in enumerate(sports):
                data = df_2[df_2['prog_distance_category'] == distance_category]

                if i_sport == 0:
                    print(df_2[(df_2['prog_distance_category'] == distance_category) & (df_2[f"{sport}_diff_percent"] > 0.22)])
                    # fair to consider same swim equipment
                    data = df_2[
                        (df_2['prog_distance_category'] == distance_category) &
                        (df_2[f"{sport}_diff_percent"] < swim_diff_percent_max) &
                        (df_2["wetsuit_m"] == df_2["wetsuit_w"])
                        ]

                if not use_world_cup:
                    data = data[data["event_category"] != "world-cup"]

                data_x = data[f"event_date_since_{first_year}"]
                data_y = data[f"{sport}_diff_percent"]
                axes[i_sport, i_distance_category].scatter(
                    data_x,
                    data_y,
                    alpha=0.5
                )
                mean_y = data_y.mean()
                std_y = data_y.std()
                axes[i_sport, i_distance_category].axhline(
                    mean_y,
                    color="gray",
                    linestyle='--',
                    linewidth=1,
                    alpha=0.5,
                    label=f"avg: {mean_y:.1%} ± {std_y:.1%}"
                )
                m, b = np.polyfit(data_x, data_y, 1)

                reg_colour = "deepskyblue" if m > 0 else "violet"
                sns.regplot(
                    x=data_x,
                    y=data_y,
                    color="gray",
                    line_kws={"color": reg_colour, "linewidth": 2, "alpha": 0.5, "linestyle": "--"},
                    ax=axes[i_sport, i_distance_category],
                    # robust=True,
                    # label=f"sns.regplot"
                )

                m_per_year = m * 365
                axes[i_sport, i_distance_category].plot(data_x, m * data_x + b, color=reg_colour, linewidth=1, label=f'm = {m_per_year:.2%} / year')

                axes[i_sport, i_distance_category].tick_params(axis='x', labelsize=12)
                axes[i_sport, i_distance_category].set_ylabel("")
                axes[i_sport, i_distance_category].legend(loc="upper right", fontsize=14)

        max_year = max(df_2["event_date_m"].apply(lambda x: int(x[:4])))
        additional_title = "" if use_world_cup else "\nONLY WTCS AND GAMES-RELATED EVENTS"
        fig.suptitle(f"WOMEN vs MEN (%)\n{first_year} - {max_year}\n({len(df_2)} events){additional_title}", fontsize=20)

        cols = [f"{cat} ({len(df_2[df_2.prog_distance_category == cat])})" for cat in distance_categories]
        rows = sports
        for ax, col in zip(axes[0], cols):
            ax.set_title(col.replace("standard", "olympic").upper(), fontsize=16)
        for ax, row in zip(axes[:, 0], rows):
            ax.set_ylabel(row.upper(), fontsize=16)

        for ax in axes.flat:
            ax.set_xlabel("")
            x_ticks = []
            for year in range(2009, max_year + 1):
                x_ticks.append((datetime(year, 1, 1) - datetime(2009, 1, 1)).days)
            ax.set_xticks(x_ticks)
            ax.set_xticklabels([str(year) for year in range(2009, max_year + 1)], fontsize=10, rotation=90)

        # use same percent y range for all subplots
        for ax in axes.flat:
            ax.set_ylim(0, max_diff_percent)
            ax.yaxis.set_major_formatter(PercentFormatter(1))
            ax.grid()

        plt.tight_layout()
        add_watermark(fig)
        saving_name = f"wm_over_years" if use_world_cup else f"wm_over_years_no_world_cup"
        plt.savefig(str(res_dir / saving_name), dpi=300)
        plt.show()

    # histograms

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


def process_results_repeated_events(
        df,
        distance_categories,
        sports,
        sport_outliers,
        n_repetitions_min
):

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
                data = drop_outliers(data, i_sport, sport_outliers=sport_outliers)

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
                        # cat_stds = year_group[f"{sport}_mean_{suffix}"].std()
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

                _ = axes[i_sport].bar(x - width, world_cup_values, color=world_cup_color, label='World Cup',
                                      **bar_kwargs)
                bars2 = axes[i_sport].bar(x, games_values, color=games_color, label='Games', **bar_kwargs)
                _ = axes[i_sport].bar(x + width, wcs_values, color=wcs_color, label='WCS', **bar_kwargs)

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
                f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'} - 5th-9th IN EACH LEG",
                # f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'} - TOP-3 IN EACH LEG",
                # f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'} - TOP-10 IN EACH LEG",
                fontsize=20
            )
            plt.tight_layout()
            add_watermark(fig)
            plt.savefig(str(res_dir / f"repeated_events_{distance_category}_{suffix}.png"), dpi=300)
            # plt.savefig(str(res_dir / f"repeated_events_{distance_category}_{suffix}_top3.png"), dpi=300)
            # plt.savefig(str(res_dir / f"repeated_events_{distance_category}_{suffix}_top10.png"), dpi=300)
            plt.show()


def process_sprint_finish(
        df,
        distance_categories
):
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
            n, bins, _patches = axes[i_distance_category, i_suffix].hist(
                df2[f"second_delay_{suffix}"],
                bins=range(0, max(df2[f"second_delay_{suffix}"]) + binwidth, binwidth),
                **kwargs
            )
            _patches[0].set_fc('r')
            _patches[1].set_fc('orange')

            # set the y-axis ticks:  normalize such that the total area of the histogram equals 1!!!
            axes[i_distance_category, i_suffix].set_yticklabels(map(
                lambda x: f"{binwidth * x:.0%}",
                axes[i_distance_category, i_suffix].get_yticks()
            ), fontsize=16)

            # set x ticks from 0 to current max
            axes[i_distance_category, i_suffix].set_xticks(
                range(0, max(df2[f"second_delay_{suffix}"]) + binwidth, binwidth))

            gap_max = df2[f"second_delay_{suffix}"].max()

            # rotate x ticks by 90
            axes[i_distance_category, i_suffix].set_xticklabels(
                axes[i_distance_category, i_suffix].get_xticks(),
                rotation=90,
                fontsize=15 if gap_max < 80 else 11
            )

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
                        splits = row[f'winner_{suffix}'].split(" ")
                        winner_str = splits[0] + " " + " ".join(splits[1:]).upper()
                        event_venue = row['event_venue'].replace("Cannigione, Arzachena", "Arzachena")
                        txt += f"[{winner_str} ({row['event_year']} {event_venue})]  "
                if txt:
                    txt = txt[:-2]
                    axes[i_distance_category, i_suffix].text(
                        delay_min + 1 if delay_min != largest_delay else delay_min - 1,  # some handle for last bin
                        0.0,
                        txt,
                        fontsize=10 if len(txt) < 90 else 9,
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
                median_delay_s - 2 if gap_max > 80 else median_delay_s - 1.5,
                max(n),
                f"median = {median_delay_s:.0f}s",
                fontsize=16,
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
                mean_delay_s + 2 if gap_max > 80 else mean_delay_s + 1.5,
                max(n),
                f"mean = {mean_delay_s:.0f}s",
                fontsize=16,
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
            axes[i_distance_category, i_suffix].tick_params(axis="y", labelsize=15)

            gap_max = df3[f"second_delay_mean"].max()
            if gap_max > 50:
                print(gap_max)
                # todo: use "broken axis"
                axes[i_distance_category, i_suffix].set_ylim(0, 53)

            # add text on the bars
            for _x, second_delays in zip(df3.index, df3[f"second_delays"]):
                axes[i_distance_category, i_suffix].text(
                    _x,
                    0.5,
                    " ".join(map(str, sorted(second_delays))),
                    ha="center",
                    rotation=90,
                    fontsize=14,
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
            axes[i_distance_category, i_suffix].set_xticklabels(df3.index, rotation=90, fontsize=15)

            # set y name
            axes[i_distance_category, i_suffix].set_ylabel("FIRST <-> SECOND (s)", fontsize=16)
            # get rid of decimals in y labels
            axes[i_distance_category, i_suffix].set_yticklabels([int(x) if x.is_integer() else x for x in axes[i_distance_category, i_suffix].get_yticks()])

            if i_suffix == 1:
                ax2.set_ylabel(
                    f"SPRINT FINISH\n(DIFFERENCE < {sprint_gap_max_s}s)\n(at least {min_n_data} events per year)",
                    fontsize=14
                )

            ax2.yaxis.label.set_color("red")
            ax2.yaxis.set_major_formatter(PercentFormatter(1))
            # color the yaxis tick labels
            ax2.tick_params(axis="y", colors="red", labelsize=15)

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


def process_scenarios(
        df,
        distance_categories
):
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20))

    df = df[df["event_category"] != "world-cup"]
    # df = df[df["event_category"] == "world-cup"]

    pack_size_max = max(df["pack_size_w"].max(), df["pack_size_m"].max())

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
            # values, bins, bars =
            axes[i_distance_category, i_suffix].hist(
                df2[f"pack_size_{suffix}"],
                bins=range(0, max(df2[f"pack_size_{suffix}"]) + binwidth, binwidth),
                **kwargs
            )
            # axes[i_distance_category, i_suffix].bar_label(bars, fontsize=20, color='navy',  # todo: not for density
            #                                               # fmt='%.2f%%'
            #                                               )

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

            # add avg. num_finishers
            n_finishers_mean = df2[f'n_finishers_{suffix}'].mean()
            n_finishers_std = df2[f'n_finishers_{suffix}'].std()
            axes[i_distance_category, i_suffix].axvline(
                x=n_finishers_mean,
                linestyle="--",
                color="k",
                # color="mediumvioletred" if suffix == "w" else "mediumturquoise",
                label=f"{n_finishers_mean:.0f} ±{n_finishers_std:.0f} finishers\n(mean ±std)"
            )
            axes[i_distance_category, i_suffix].set_xlim(0, max(pack_size_max, n_finishers_mean) + 10)
            # axes[i_distance_category, i_suffix].set_ylim(0, 0.4 / binwidth)
            axes[i_distance_category, i_suffix].legend(loc='upper right', fontsize=15)
            axes[i_distance_category, i_suffix].set_xlabel("size of front pack".upper(), fontsize=14)

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
        df_tmp = df.copy()
        df_tmp.sort_values(
            by=[
                f"pack_size_{suffix}",
                f"event_year"
            ],
            ascending=False,
            inplace=True
        )
        for i_row, row in df_tmp.head(10).iterrows():
            winner_name = row[f'winner_{suffix}']
            table_info.append({
                "**pack_size**": "**" + str(row[f"pack_size_{suffix}"]) + "**",
                "year": row["event_year"],
                "winner": f"{winner_name} ( {country_emojis[row[f'winner_country_{suffix}']] if row[f'winner_country_{suffix}'] in country_emojis else row['winner_country_noc']} )",
                "distance": row["prog_distance_category"].replace("standard", "olympic").upper(),
                "cat": row["event_category"].upper().replace("WCS", "WTCS"),
                "event": f"[{row['event_title']} ( {country_emojis[row['event_country_noc']] if row['event_country_noc'] in country_emojis else row['event_country_noc']} )]({row['event_listing']})",
            })
        table_info.append({
            "**pack_size**": "*...*",
            "year": "...",
            "winner": "...",
            "distance": "...",
            "cat": "...",
            "event": "...",
        })
    df_table = pd.DataFrame(table_info)
    # upper the columns
    df_table.columns = df_table.columns.str.upper()
    print(df_table.to_markdown(
        index=False,
        colalign=["center"] * len(df_table.columns)
    ))

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
                "**pack_size**": "**" + str(row[f"pack_size_{suffix}"]) + "**",
                "year": row["event_year"],
                "winner": f"{winner_name} ( {country_emojis[row[f'winner_country_{suffix}']] if row[f'winner_country_{suffix}'] in country_emojis else row['winner_country_noc']} )",
                "distance": row["prog_distance_category"].replace("standard", "olympic").upper(),
                "cat": row["event_category"].upper().replace("WCS", "WTCS"),
                "event": f"[{row['event_title']} ( {country_emojis[row['event_country_noc']] if row['event_country_noc'] in country_emojis else row['event_country_noc']} )]({row['event_listing']})",
            })

        table_info.append({
            "**pack_size**": "...",
            "year": "...",
            "winner": "...",
            "distance": "...",
            "cat": "...",
            "event": "...",
        })

    # print markdown
    df_table = pd.DataFrame(table_info)
    df_table.columns = df_table.columns.str.upper()
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
                    fontsize=14
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
            axes[i_distance_category, i_suffix].set_xticklabels(df3.index, rotation=90, fontsize=16)

            # set size of y labels
            axes[i_distance_category, i_suffix].tick_params(axis='y', labelsize=16)

            # set y name
            if i_suffix == 0:
                axes[i_distance_category, i_suffix].set_ylabel("front pack size".upper(), fontsize=16)

            # ax3.yaxis.set_ticklabels([])
            if i_suffix == 1:
                ax2.set_ylabel("winner in front pack (%)".upper(), fontsize=16)
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
                linestyle="--",
                linewidth=1,
                alpha=1,
                color="black",
                label=f"Average: {mean:.1%}"
            )
            axes[i_distance_category, i_suffix].legend(fontsize=15)

            # set subtitle
            axes[i_distance_category, i_suffix].set_ylabel("best runner wins (%)".upper(), fontsize=16)

            axes[i_distance_category, i_suffix].tick_params(axis='y', labelsize=16)

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
            ], rotation=90, fontsize=16)

            axes[i_distance_category, i_suffix].grid(axis="y", alpha=0.5)

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


def process_temperatures(df, distance_categories):

    # assert that consistency wetsuit / temperature
    # assert len(df[(df["wetsuit_w"]) & (df["water_temperature_w"] >= 20.0)]) == 0
    # assert len(df[(df["wetsuit_m"]) & (df["water_temperature_m"] >= 20.0)]) == 0
    # assert len(df[(~df["wetsuit_w"]) & (df["water_temperature_w"] < 20.0)]) == 0
    # assert len(df[(~df["wetsuit_m"]) & (df["water_temperature_m"] < 20.0)]) == 0

    # plot df[temperature] distribution
    measure_min = min(
        min(df[f"water_temperature_m"].min(), df[f"water_temperature_w"].min()),
        min(df[f"air_temperature_m"].min(), df[f"air_temperature_w"].min()),
    )
    measure_max = max(
        max(df[f"water_temperature_m"].max(), df[f"water_temperature_w"].max()),
        max(df[f"air_temperature_m"].max(), df[f"air_temperature_w"].max()),
    )

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(20, 20))
    for i_measure, (measure, sport) in enumerate([("air", "run"), ("water", "swim")]):
        data = np.concatenate([
            df[f"{measure}_temperature_m"].values,
            df[f"{measure}_temperature_w"].values
        ])
        # drop nan
        data = data[~np.isnan(data)]
        bins = np.arange(int(min(data))-1, int(max(data))+1, 1)
        kwargs = {
            "density": True,
            "bins": bins,
        }
        mean = data.mean()
        sd = data.std()

        axes[i_measure].hist(
            data,
            color="deepskyblue" if sport == "swim" else "gold",
            # alpha=0.5,
            edgecolor='black',
            # label=f"{measure.upper()}",
            **kwargs
        )

        if sport == "swim":
            axes[i_measure].axvline(
                20,
                color='red',
                linestyle="-",
                linewidth=3,
                label=f"20°C wetsuit limit"
            )

        axes[i_measure].axvline(
            mean,
            color='black',
            linestyle="--",
            linewidth=2,
            label=r"Average = ${:.1f}\,\mathrm{{^\circ C}}$".format(mean)
        )
        # write text close to this line
        # axes[i_measure].text(
        #     mean+0.15,
        #     0.03,
        #     r"$\mu$ = ${:.1f}\,\mathrm{{^\circ C}}$".format(mean),
        #     fontsize=15,
        #     color="black",
        #     rotation=90
        # )

        q_10, q_90 = np.percentile(data, [10, 90])
        print(f"80% of {measure} temperatures are between {q_10:.1f} and {q_90:.1f} °C (Mean: {mean:.1f} °C, SD: {sd:.1f} °C, Min: {data.min():.1f} °C, Max: {data.max():.1f} °C)")
        axes[i_measure].axvline(
            q_10,
            color='black',
            linestyle="-.",
            linewidth=1,
            label=r"$10\%$ percentile = ${:.1f}\,\mathrm{{^\circ C}}$".format(q_10)
        )
        axes[i_measure].axvline(
            q_90,
            color='black',
            linestyle="-.",
            linewidth=1,
            label=r"$90\%$ percentile = ${:.1f}\,\mathrm{{^\circ C}}$".format(q_90)
        )

        from scipy.stats import norm
        mu, std = norm.fit(data)
        x = np.linspace(measure_min-5, measure_max+5, 100)
        p = norm.pdf(x, mu, std)
        axes[i_measure].plot(
            x,
            p,
            'gray',
            linewidth=1,
            linestyle="-",
            alpha=0.5,
            label=f"Normal distribution ($\mu={mu:.1f}\,\mathrm{{^\circ C}}$, $\sigma={std:.1f}\,\mathrm{{^\circ C}}$)"
        )

        axes[i_measure].grid()
        axes[i_measure].set_xlim(measure_min - 1, measure_max + 2)
        axes[i_measure].set_xticks(range(int(measure_min) - 1, int(measure_max) + 2, 1))
        axes[i_measure].tick_params(axis='x', which='major', labelsize=14)
        axes[i_measure].legend(fontsize=15)
        axes[i_measure].set_title(f"{measure.upper()}\n{len(data)} races", fontsize=15)
        axes[i_measure].set_xlabel("TEMPERATURE °C", fontsize=12)
        axes[i_measure].set_ylabel("Percentage".upper(), fontsize=12)
        # format y as percentage
        axes[i_measure].yaxis.set_major_formatter(PercentFormatter(1))

    fig.suptitle(
        f"WATER AND AIR TEMPERATURES\n",
        fontsize=20
    )
    plt.tight_layout()
    add_watermark(fig)
    plt.savefig(res_dir / "temperatures.png")
    # plt.show()

    for measure, sport in [("air", "run"), ("water", "swim")]:
        measure_min = min(df[f"{measure}_temperature_m"].min(), df[f"{measure}_temperature_w"].min())
        measure_max = max(df[f"{measure}_temperature_m"].max(), df[f"{measure}_temperature_w"].max())

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20))

        # df = df[df["event_category"] != "world-cup"]
        # df = df[df["event_category"] == "world-cup"]

        for i_distance_category, distance_category in enumerate(distance_categories):
            for i_suffix, suffix in enumerate(["w", "m"]):
                df2 = df[df["prog_distance_category"] == distance_category]
                df2 = df2.dropna(subset=[f"{measure}_temperature_{suffix}"])
                df2.sort_values([f"{measure}_temperature_{suffix}"], inplace=True)

                if sport == "swim":
                    # ignore races with hot-wetsuit or cold-swimsuit
                    conditions_logs_path = ignored_dir / "conditions_inconsistencies.json"
                    conditions_logs = []
                    if conditions_logs_path.exists():
                        conditions_logs = json_load(conditions_logs_path)

                    hot_wetsuit_filter = (df2[f"wetsuit_{suffix}"]) & (df2[f"water_temperature_{suffix}"] >= 20.0)
                    df_hot_wetsuit = df2[hot_wetsuit_filter]
                    cold_swimsuit_filter = (~df2[f"wetsuit_{suffix}"]) & (df2[f"water_temperature_{suffix}"] < 20.0)
                    df_cold_swimsuit = df2[cold_swimsuit_filter]

                    if len(df_hot_wetsuit) > 0:
                        print(f"\n[{len(df_hot_wetsuit)}] WETSUIT ({distance_category}_{suffix}) despite WATER TEMPERATURE >= 20°C:")
                        for row in df_hot_wetsuit.itertuples(index=False):
                            water_temperature = row.water_temperature_w if suffix == "w" else row.water_temperature_m
                            air_temperature = row.air_temperature_w if suffix == "w" else row.air_temperature_m
                            msg = f"{row.event_id} ({suffix}): {water_temperature} °C (air at {air_temperature} °C) for {row.event_year} {row.event_venue} - {row.event_title}\n\t{row.event_listing}"
                            print(f"\t{msg}")
                            found = False
                            for condition_log in conditions_logs:
                                if condition_log["event_id"] == row.event_id:
                                    if ((condition_log["prog_name"] == "Elite Men") and (suffix == "m")) or ((condition_log["prog_name"] == "Elite Women") and (suffix == "w")):
                                        for issue in condition_log["issues"]:
                                            if "wetsuit" in issue:
                                                found = True
                                                continue
                            if not found:
                                raise Exception(f"Hot wetsuit: not found in {conditions_logs_path.absolute()}:\n{msg}")

                    if len(df_cold_swimsuit) > 0:
                        print(f"\n[{len(df_cold_swimsuit)}] NO-WETSUIT ({distance_category}_{suffix}) despite WATER TEMPERATURE < 20°C:")
                        for row in df_cold_swimsuit.itertuples(index=False):
                            water_temperature = row.water_temperature_w if suffix == "w" else row.water_temperature_m
                            air_temperature = row.air_temperature_w if suffix == "w" else row.air_temperature_m
                            msg = f"{row.event_id} ({suffix}): {water_temperature} °C (air at {air_temperature} °C) for {row.event_year} {row.event_venue} - {row.event_title}\n\t{row.event_listing}"
                            print(f"\t{msg}")
                            found = False
                            for condition_log in conditions_logs:
                                if condition_log["event_id"] == row.event_id:
                                    if ((condition_log["prog_name"] == "Elite Men") and (suffix == "m")) or ((condition_log["prog_name"] == "Elite Women") and (suffix == "w")):
                                        for issue in condition_log["issues"]:
                                            if "wetsuit" in issue:
                                                found = True
                                                continue
                            if not found:
                                raise Exception(f"Cold swimsuit: not found in {conditions_logs_path.absolute()}:\n{msg}")

                    df2 = df2[~hot_wetsuit_filter]
                    df2 = df2[~cold_swimsuit_filter]

                    colours = ["navy" if t >= 20 else "dodgerblue" for t in df2[f"{measure}_temperature_{suffix}"]]
                    kwargs = dict(
                        color=colours,
                        edgecolor='black',
                        s=100,
                        marker="x"
                    )

                    # reg_colour = "deepskyblue"
                    # df_no_wetsuit = df2[df2[f"{measure}_temperature_{suffix}"] >= 20.0]
                    # df_wetsuit = df2[df2[f"{measure}_temperature_{suffix}"] < 20.0]
                    # sns.regplot(
                    #     x=df_no_wetsuit[f"{measure}_temperature_{suffix}"],
                    #     y=df_no_wetsuit[f"{sport}_mean_{suffix}"],
                    #     scatter=False,
                    #     line_kws={"color": reg_colour, "linewidth": 1, "alpha": 0.1, "linestyle": "-"},
                    #     ax=axes[i_distance_category, i_suffix],
                    #     order=2
                    # )
                    # sns.regplot(
                    #     x=df_wetsuit[f"{measure}_temperature_{suffix}"],
                    #     y=df_wetsuit[f"{sport}_mean_{suffix}"],
                    #     scatter=False,
                    #     line_kws={"color": reg_colour, "linewidth": 1, "alpha": 0.1, "linestyle": "-"},
                    #     ax=axes[i_distance_category, i_suffix],
                    #     order=2
                    # )

                elif sport == "run":
                    # drop event_id 109660 because too long run! (top women at 3:57/km!)
                    df2 = df2[df2["event_id"] != 109660]

                    kwargs = dict(
                        cmap='autumn_r',
                        c=df2[f"{measure}_temperature_{suffix}"],
                        edgecolor='black',
                        s=100,
                        marker="P"
                    )

                    reg_colour = "deepskyblue"
                    sns.regplot(
                        x=df2[f"{measure}_temperature_{suffix}"],
                        y=df2[f"{sport}_mean_{suffix}"],
                        scatter=False,
                        line_kws={"color": reg_colour, "linewidth": 1, "alpha": 0.2, "linestyle": "-"},
                        ax=axes[i_distance_category, i_suffix],
                        order=2
                    )

                    coefficients = np.polyfit(
                        df2[f"{measure}_temperature_{suffix}"],
                        df2[f"{sport}_mean_{suffix}"],
                        2
                    )
                    axes[i_distance_category, i_suffix].plot(
                        df2[f"{measure}_temperature_{suffix}"],
                        # np.poly1d(p)(df2[f"{measure}_temperature_{suffix}"]),
                        np.polyval(coefficients, df2[f"{measure}_temperature_{suffix}"]),
                        color='dodgerblue',
                        linewidth=2,
                        linestyle='-',
                        alpha=0.6,
                        label='Best fit (2nd degree)'
                    )

                    a, b, c = coefficients
                    optimal_t = -b / (2 * a)
                    axes[i_distance_category, i_suffix].axvline(
                        optimal_t,
                        linestyle="-.",
                        linewidth=2,
                        alpha=0.6,
                        color="dodgerblue",
                        label=f"Optimal: {optimal_t:.1f}°C"
                    )
                else:
                    raise NotImplementedError(f"Sport {sport} not implemented")

                axes[i_distance_category, i_suffix].scatter(
                    df2[f"{measure}_temperature_{suffix}"],
                    df2[f"{sport}_mean_{suffix}"],
                    **kwargs
                )

                # set title
                axes[i_distance_category, i_suffix].set_title(
                    f"\n{distance_category.replace('standard', 'olympic').upper()} - {'WOMEN' if suffix == 'w' else 'MEN'}\n({len(df2)} events)",
                    fontsize=20
                )

                axes[i_distance_category, i_suffix].grid()

                locs = axes[i_distance_category, i_suffix].get_yticks()

                def format_label(_x):
                    splits = seconds_to_h_min_sec(_x, use_hours=True, sport=sport, use_units=True).split(" (")
                    return f"{splits[0]}\n({splits[1]}"

                labels = map(format_label, locs)
                axes[i_distance_category, i_suffix].set_yticks(locs)
                axes[i_distance_category, i_suffix].set_yticklabels(labels)

                # set tick font size
                axes[i_distance_category, i_suffix].yaxis.set_tick_params(labelsize=13)
                axes[i_distance_category, i_suffix].set_ylabel(f"{sport} time".upper(), fontsize=15)

                axes[i_distance_category, i_suffix].set_xlabel(f"{measure} temperature (°C)".upper(), fontsize=15)
                axes[i_distance_category, i_suffix].xaxis.set_tick_params(labelsize=13)

                # set x min max
                axes[i_distance_category, i_suffix].set_xlim(measure_min - 1, measure_max + 1)

                if sport == "swim":
                    axes[i_distance_category, i_suffix].axvline(
                        20,
                        linestyle="-.",
                        linewidth=2,
                        color="black",
                        label="20°C"
                    )

                    # get current x and y min/max of the ax
                    x_min = axes[i_distance_category, i_suffix].get_xlim()[0]
                    x_max = axes[i_distance_category, i_suffix].get_xlim()[1]
                    y_min = axes[i_distance_category, i_suffix].get_ylim()[0]
                    y_max = axes[i_distance_category, i_suffix].get_ylim()[1]

                    # Create the rectangle
                    rect = patches.Rectangle(
                        (x_min, y_min),
                        20 - x_min,
                        y_max - y_min,
                        facecolor='silver',
                        alpha=0.2,
                        label="wetsuit"
                    )

                    # Add the rectangle to the plot
                    axes[i_distance_category, i_suffix].add_patch(rect)

                    rect = patches.Rectangle(
                        (20, y_min),
                        x_max - 20,
                        y_max - y_min,
                        facecolor='lightskyblue',
                        alpha=0.2,
                        label="no wetsuit"
                    )

                    # Add the rectangle to the plot
                    axes[i_distance_category, i_suffix].add_patch(rect)

                axes[i_distance_category, i_suffix].legend(fontsize=15)

        # create markdown table
        df = df.dropna(subset=[f"{measure}_temperature_w", f"{measure}_temperature_m"])
        df[f"{measure}_temperature_min"] = df[[f"{measure}_temperature_w", f"{measure}_temperature_m"]].min(axis=1)
        df[f"{measure}_temperature_max"] = df[[f"{measure}_temperature_w", f"{measure}_temperature_m"]].max(axis=1)

        all_rows = []
        for suf in ["min", "max"]:
            # create markdown table
            df_table = df[
                ["event_year", "event_country_noc", "event_listing", "event_venue", "prog_distance_category",
                 f"{measure}_temperature_{suf}", "event_category"]]
            # in prog_distance_category, change "standard" to "olympic"
            df_table["prog_distance_category"] = df_table["prog_distance_category"].apply(
                lambda _x: _x.replace("standard", "olympic")
            )
            # merge "event_country_noc" and "event_venue"
            df_table["event"] = df_table[["event_country_noc", "event_listing", "event_venue"]].apply(
                lambda
                    _x: f"[{_x.event_venue}]({_x.event_listing}) ( {country_emojis[_x.event_country_noc] if _x.event_country_noc in country_emojis else _x.event_country_noc} )",
                axis=1
            )
            if suf == "min":
                df_table.sort_values([f"{measure}_temperature_min"], inplace=True)
            else:
                df_table.sort_values([f"{measure}_temperature_max"], inplace=True, ascending=False)

            df_table = df_table.head(10)
            if suf == "max":
                df_table.sort_values([f"{measure}_temperature_max"], inplace=True)

            df_table = df_table[
                ["event_year", "event", f"{measure}_temperature_{suf}", "prog_distance_category", "event_category"]]
            df_table["event_category"] = df_table["event_category"].apply(lambda _x: _x.replace("wcs", "WTCS").upper())
            df_table[f"{measure}_temperature_{suf}"] = df_table[f"{measure}_temperature_{suf}"].apply(lambda _x: f"{_x:.1f} :{'hot_face' if suf == 'max' else 'cold_face'}:")
            df_table.columns = ["YEAR", "EVENT", f"{measure.upper()} TEMPERATURE", "DISTANCE", "EVENT CATEGORY"]
            all_rows.extend(df_table.to_dict('records'))

            all_rows.append({k: "..." for k in df_table.columns})

        df_table = pd.DataFrame(all_rows)
        print(df_table.to_markdown(
            index=False,
            colalign=["center"] * len(df_table.columns)
        ))

        fig.suptitle(
            f"{measure.upper()} TEMPERATURES AND {sport.upper()} TIMES"
            f"\n(from {measure_min:.1f} to {measure_max:.1f}°C)",
            fontsize=20
        )

        fig.tight_layout()

        add_watermark(fig)
        plt.savefig(str(res_dir / f"temperatures_{measure}.png"), dpi=300)
        plt.show()


def process_sport_proportion(df, distance_categories):
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
                    "DISTANCE": ".",
                })

            table_info.append({
                "t_time": "...",
                "EVENT": "...",
                "DISTANCE": "...",
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


def process_swim_gaps(df, distance_categories):
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

    for ax, row in zip(axes[1, :], rows):
        ax.set_xlabel("gap [s]", size='large')

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
            res_str = ', '.join([f"{k} ({v})" for k, v in venue_dict.items()])
            res_str.replace("Cannigione, Arzachena", "Arzachena")
            return res_str

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
        durations = {k: v for k, v in durations.items() if k <= 2024}

        pre_covid_keys = [y for y in durations.keys() if y < 2020]
        pre_covid_vals = [durations[k] for k in pre_covid_keys]
        post_covid_keys = [y for y in durations.keys() if y >= 2022]
        post_covid_vals = [durations[k] for k in post_covid_keys]
        during_covid_keys = [2019, 2020, 2021, 2022, 2023, 2024]
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
        athlete_season_durations = json_load(data_dir / f"athlete_season_durations_{suffix}.json")
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

def process_wetsuit_from_repeated_events(
        df,
        swim_diff_percent_max: float,
        distance_categories,
        sport_outliers,
        max_year_gap,
        min_wet_gain_percent,
        max_wet_gain_percent,
):
    # remove outliers?
    outliers = df[df["swim_diff_percent"] >= swim_diff_percent_max]
    print(f"{len(outliers)} swim outliers:")
    print(list(outliers["event_listing"]))
    print(list(outliers["event_title"]))
    print(outliers["swim_diff_percent"])
    df = df[df["swim_diff_percent"] < swim_diff_percent_max]

    df = drop_outliers(df, i_sport=0, sport_outliers=sport_outliers)

    # rows with no wetsuit info have already been dropped

    swim_time_infos = []
    groups = df.groupby(["event_venue"])
    for suffix in ["w", "m"]:
        for group in groups:
            df_group = group[1]
            event_venue = group[0][0]
            # print(f"{len(df_group)} event(s) at {event_venue}")
            wetsuit_dict = df_group[f"wetsuit_{suffix}"].value_counts().to_dict()
            if len(wetsuit_dict) > 1:
                # print(f"\t{wetsuit_dict}")
                df_wet = df_group[df_group[f"wetsuit_{suffix}"].astype(bool)]
                df_no_wet = df_group[~df_group[f"wetsuit_{suffix}"].astype(bool)]
                for row_no_wet in df_no_wet.itertuples(index=False):
                    for row_wet in df_wet.itertuples(index=False):
                        # if row_no_wet.event_year >= row_wet.event_year:
                        #     continue
                        if row_no_wet.prog_distance_category != row_wet.prog_distance_category:
                            continue
                        prog_distance_category = row_no_wet.prog_distance_category
                        assert prog_distance_category in distance_categories, prog_distance_category
                        if abs(row_no_wet.event_year - row_wet.event_year) <= max_year_gap:
                            if suffix == "w":
                                wet_swim = row_wet.swim_mean_w
                                no_wet_swim = row_no_wet.swim_mean_w
                            else:
                                wet_swim = row_wet.swim_mean_m
                                no_wet_swim = row_no_wet.swim_mean_m

                            wet_gain_percent = 100 * (no_wet_swim - wet_swim) / no_wet_swim
                            swim_time_infos.append({
                                "prog_distance_category": prog_distance_category,
                                "wet_swim": wet_swim,
                                "no_wet_swim": no_wet_swim,
                                "wet_gain_percent": wet_gain_percent,
                                "event_venue": event_venue,
                                "wet_year": row_wet.event_year,
                                "no_wet_year": row_no_wet.event_year,
                                "event_country_noc": row_no_wet.event_country_noc,
                                "event_listing": row_no_wet.event_listing,
                                "suffix": suffix,
                                "event_category": row_no_wet.event_category,
                            })

    df_wet_gain = pd.DataFrame(swim_time_infos)
    df_wet_gain.sort_values("wet_gain_percent", inplace=True)
    df_wet_gain = df_wet_gain[df_wet_gain["wet_gain_percent"] > min_wet_gain_percent]
    df_wet_gain = df_wet_gain[df_wet_gain["wet_gain_percent"] < max_wet_gain_percent]

    df_table = df_wet_gain
    df_table["EVENT"] = df_table[["event_country_noc", "event_listing", "event_venue"]].apply(
        lambda
            x: f"[{x.event_venue}]({x.event_listing}) ( {country_emojis[x.event_country_noc] if x.event_country_noc in country_emojis else x.event_country_noc} )",
        axis=1
    )
    df_table["swim_wet"] = df_table[["wet_year", "wet_swim"]].apply(
        lambda x: f"{seconds_to_h_min_sec(round(x.wet_swim), use_hours=False, sport='swim', use_units=True)} ({x.wet_year:.0f})",
        axis=1
    )
    df_table["swim_no_wet"] = df_table[["no_wet_year", "no_wet_swim"]].apply(
        lambda x: f"{seconds_to_h_min_sec(round(x.no_wet_swim), use_hours=False, sport='swim', use_units=True)} ({x.no_wet_year:.0f})",
        axis=1
    )
    df_table["wet_gain_str"] = df_table[["wet_gain_percent"]].apply(
        lambda x: f"**{x.wet_gain_percent/100:.1%}**",
        axis=1
    )
    df_table["GENDER"] = df_table[["suffix"]].apply(
        lambda x: "M" if x.suffix == "m" else "W",
        axis=1
    )
    df_table["FORMAT"] = df_table[["prog_distance_category"]].apply(
        lambda x: "SPRINT" if x.prog_distance_category == "sprint" else "OLYMPIC",
        axis=1
    )
    df_table = df_table[["EVENT", "FORMAT", "GENDER", "swim_wet", "swim_no_wet", "wet_gain_str"]]

    df_table = df_table.rename(columns={
        "swim_wet": "Swim with wetsuit".upper(),
        "swim_no_wet": "Swim without wetsuit".upper(),
        "wet_gain_str": "**Wetsuit gain".upper() + " (%)**",
    })

    print("Distributions:")
    d = df_wet_gain["event_category"].value_counts()
    d_normed = df_wet_gain["event_category"].value_counts(normalize=True)
    print("- Event category:")
    for k in ["wcs", "world-cup", "games"]:
        if k in d:
            print(f"\t- {k.title().replace('Wcs', 'WTCS'):<10}: {d_normed[k]:.0%} ({d[k]})")
    d = df_wet_gain["prog_distance_category"].value_counts()
    d_normed = df_wet_gain["prog_distance_category"].value_counts(normalize=True)
    print("- Distance category:")
    for k in ["standard", "sprint"]:
        if k in d:
            print(f"\t- {k.replace('standard', 'olympic').title():<10}: {d_normed[k]:.0%} ({d[k]})")

    print("\n**Venues of the comparisons:**")
    df_wet_gain["event_venue_with_flag"] = df_wet_gain[["event_country_noc", "event_venue"]].apply(
        lambda x: f"{x.event_venue} ( {country_emojis[x.event_country_noc] if x.event_country_noc in country_emojis else x.event_country_noc} )",
        axis=1
    )
    for venue, venue_count in df_wet_gain["event_venue_with_flag"].value_counts().to_dict().items():
        print(f"- {venue_count:>2} ({venue_count / len(df_wet_gain):>5.1%}): {venue}")
    print()

    print(df_table.to_markdown(
        index=False,
        colalign=["center"] * len(df_table.columns)
    ))

    print(df_wet_gain["wet_gain_percent"].describe())
    print("answer 1:")
    print(f'{df_wet_gain["wet_gain_percent"].mean():.2f} mean')
    print(f'{df_wet_gain["wet_gain_percent"].median():.2f} median')
    for suffix in ["w", "m"]:
        print(f"\t{suffix.upper()}:")
        print(f'\t\t{df_wet_gain[df_wet_gain["suffix"] == suffix]["wet_gain_percent"].mean():.2f} mean')
        print(f'\t\t{df_wet_gain[df_wet_gain["suffix"] == suffix]["wet_gain_percent"].median():.2f} median')

    fig, ax = plt.subplots(figsize=(16, 16))

    data_min = min(df_wet_gain["wet_gain_percent"])
    data_max = max(df_wet_gain["wet_gain_percent"])
    bins = np.arange(int(data_min) - 1, int(data_max) + 1, 1)
    kwargs_hist = {
        "density": True,
        "bins": bins,
    }

    print("w vs m:")
    mean_all = df_wet_gain["wet_gain_percent"].mean()
    median_all = df_wet_gain["wet_gain_percent"].median()
    std_all = df_wet_gain["wet_gain_percent"].std()

    mean_w = df_wet_gain[df_wet_gain["suffix"] == "w"]["wet_gain_percent"].mean()
    mean_m = df_wet_gain[df_wet_gain["suffix"] == "m"]["wet_gain_percent"].mean()
    median_w = df_wet_gain[df_wet_gain["suffix"] == "w"]["wet_gain_percent"].median()
    median_m = df_wet_gain[df_wet_gain["suffix"] == "m"]["wet_gain_percent"].median()
    std_w = df_wet_gain[df_wet_gain["suffix"] == "w"]["wet_gain_percent"].std()
    std_m = df_wet_gain[df_wet_gain["suffix"] == "m"]["wet_gain_percent"].std()

    print(f"Results from **{len(df_wet_gain)} comparisons**:")
    print(f'- **`improve_percent`**:')
    print(f'\t- Women+Men  : **`mean = {mean_all:.1f}%`**, **`median = {median_all:.1f}%`**. (`std = {std_all:.1f}`)')
    print(f'\t- Women only : `mean = {mean_w:.1f}%`, `median = {median_w:.1f}%`. (`std = {std_w:.1f}`)')
    print(f'\t- Men only   : `mean = {mean_m:.1f}%`, `median = {median_m:.1f}%`. (`std = {std_m:.1f}`)')
    print(f'- **Women vs Men: `{mean_w - mean_m:.1f}%` (with means) or `{median_w - median_m:.1f}%` (with medians)**.')

    ax.hist(
        df_wet_gain["wet_gain_percent"],
        label=r"all  : [: = median = ${:.1f}$] [-- = mean = ${:.1f}$]".format(median_all, mean_all),
        alpha=0.2,
        color="gray",
        **kwargs_hist
    )
    kwargs_axv_all = {
        "color": "black",
        "linewidth": 3,
        "alpha": 1
    }
    ax.axvline(
        mean_all,
        linestyle="-",
        **kwargs_axv_all
    )
    ax.axvline(
        median_all,
        linestyle=":",
        **kwargs_axv_all
    )

    for suffix in ["w", "m"]:
        color = "magenta" if suffix == "w" else "mediumblue"
        label = r"women: [: = median = ${:.1f}$] [-- = mean = ${:.1f}$]".format(median_w, mean_w) if suffix == "w" else r"men  : [: = median = ${:.1f}$] [-- = mean = ${:.1f}$]".format(median_m, mean_m)
        ax.hist(
            df_wet_gain[df_wet_gain["suffix"] == suffix]["wet_gain_percent"],
            label=label,
            alpha=0.5 if suffix == "w" else 0.4,
            color=color,
            histtype="step",
            linewidth=4 if suffix == "w" else 2,
            **kwargs_hist
        )

        kwargs_axv = {
            "color": color,
            "linewidth": 2,
            "alpha": 0.5
        }
        ax.axvline(
            mean_w if suffix == "w" else mean_m,
            linestyle="-",
            **kwargs_axv
        )
        ax.axvline(
            median_w if suffix == "w" else median_m,
            linestyle=":",
            **kwargs_axv
        )

    from scipy.stats import norm
    mu, std = norm.fit(df_wet_gain["wet_gain_percent"])
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'gray', linewidth=1, linestyle="-", label=f"Normal distribution ($\mu={mu:.1f}$, $\sigma={std:.1f}$)")

    ax.set_ylabel("Percentage".upper(), fontsize=16)
    ax.set_xlabel("GAIN OFFERED BY THE WETSUIT (%)", fontsize=16)

    ax.tick_params(axis='both', which='major', labelsize=14)

    ax.grid()
    ax.set_xlim(int(data_min) - 2, int(data_max) + 2)
    ax.set_xticks(range(int(data_min) - 1, int(data_max) + 2, 1))
    ax.legend(loc='upper right', fontsize=15)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    fig.suptitle(
        f"WETSUIT IMPACT DURING THE SWIM\nusing {len(df_wet_gain)} year-to-year comparisons",
        fontsize=18
    )
    plt.tight_layout()
    add_watermark(fig, y=0.92, x=0.12)
    plt.savefig(str(res_dir / "wetsuit_in_swim_year_to_year.png"), dpi=300)
    plt.show()




def process_level(df):
    for suffix in ["w", "m"]:
        print(f"\n### LEVEL {suffix.upper()}\n")
        df.sort_values(by=f"level_{suffix}", inplace=True)
        df.reset_index(drop=True)
        table_info = []
        for index, row in df.iterrows():
            table_info.append({
                "EVENT": f"[{row.event_year} {row.event_venue} ( {country_emojis[row.event_country_noc] if row.event_country_noc in country_emojis else row.event_country_noc} )]({row.event_listing})".replace("Cannigione, Arzachena", "Arzachena"),
                "CAT": row.event_category,
                "LEVEL_M": round(row.level_m, 2),
                "LEVEL_W": round(row.level_w, 2)
            })
        df_table = pd.DataFrame(table_info)
        df_table.columns = df_table.columns.str.upper()
        print(df_table.to_markdown(
            index=False,
            colalign=["center"] * len(df_table.columns)
        ))



def main():
    ###
    config = load_config()
    events_config = config["events"]

    distance_categories = events_config["distance_categories"]
    sports = events_config["sports"]
    n_repetitions_min = events_config["n_repetitions_min"]
    wetsuit_benefit_from_recurring_events=events_config["wetsuit_benefit_from_recurring_events"]
    swim_diff_percent_max = events_config["cleaning"]["swim_diff_percent_max"]
    sport_outliers = events_config["cleaning"]["sport_outliers"]
    ###

    df = get_events_df(events_config=events_config)

    # df = df[df["event_category"] != "world-cup"]
    # df = df[df["prog_distance_category"] != "sprint"]
    # df = df[df["event_venue"].isin(["Yokohama", "Edmonton", "Cagliari", "Stockholm"])]

    process_sports(df.copy(), distance_categories=distance_categories, sports=sports, sport_outliers=sport_outliers)
    process_results_wetsuit(df.copy(), swim_diff_percent_max=swim_diff_percent_max, distance_categories=distance_categories, sport_outliers=sport_outliers)
    process_wetsuit_from_repeated_events(df.copy(), swim_diff_percent_max=swim_diff_percent_max, distance_categories=distance_categories, sport_outliers=sport_outliers, **wetsuit_benefit_from_recurring_events)
    process_results_w_vs_m(df.copy(), swim_diff_percent_max=swim_diff_percent_max, distance_categories=distance_categories, sports=sports)
    process_results_repeated_events(df.copy(), distance_categories=distance_categories, sports=sports, sport_outliers=sport_outliers, n_repetitions_min=n_repetitions_min)
    process_scenarios(df.copy(), distance_categories=distance_categories)
    process_sprint_finish(df.copy(), distance_categories=distance_categories)
    process_ages(df.copy())
    process_sport_proportion(df.copy(), distance_categories=distance_categories)
    process_swim_gaps(df.copy(), distance_categories=distance_categories)
    process_event_country(df.copy())
    process_temperatures(df.copy(), distance_categories=distance_categories)
    # process_event_dates(df.copy())  # make sure to reduce the min-participants: n_results_min
    process_level(df.copy())


if __name__ == '__main__':
    main()
