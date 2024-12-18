"""
this script applies two methods to estimate:
    "how longer gets T1 with the wetsuit?"
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

from scripts.utils import load_config, ignored_dir, country_emojis, res_dir, add_watermark
from scripts.utils_events import get_events_df

config = load_config()
events_config = config["events"]
t1_config = events_config["t1_with_wetsuit"]


def get_df(use_cache: bool = False):
    tmp_results_file_path = ignored_dir / "tmp_results.csv"
    if use_cache and tmp_results_file_path.exists():
        df = pd.read_csv(str(tmp_results_file_path))
    else:
        # set larger window for mean
        events_config["mean_computation"]["i_first"] = t1_config["i_first"]
        events_config["mean_computation"]["i_last"] = t1_config["i_last"]

        df = get_events_df(events_config=events_config)
        df.to_csv(str(tmp_results_file_path), index=False)

    # df = df[df["event_category"] == "world-cup"]
    # df = df[df["event_category"] == "wcs"]

    return df


### ### ### ###
### METHOD 1/2
### ### ### ###

def method_events(df):
    """
    use events in same locations with different wetsuit
        compare T1 times with and without wetsuit -> compute the difference

    works well only if
        timing mats are consistent! Probably changing over years. Therefore, applying a maximum year gap parameter
    """

    # params
    max_year_gap = t1_config["events"]["max_year_gap"]
    min_t1_delta = t1_config["events"]["min_t1_delta"]
    max_t1_delta = t1_config["events"]["max_t1_delta"]

    wet_time_infos = []
    groups = df.groupby(["event_venue"])
    for suffix in ["w", "m"]:
        for group in groups:
            df_group = group[1]
            event_venue = group[0][0]
            # print(f"{len(df_group)} event(s) at {event_venue}")
            wetsuit_dict = df_group[f"wetsuit_{suffix}"].value_counts().to_dict()
            if len(wetsuit_dict) > 1:
                # print(f"\t{wetsuit_dict}")
                df_wet = df_group[df_group[f"wetsuit_{suffix}"]]
                df_no_wet = df_group[~df_group[f"wetsuit_{suffix}"]]
                for row_no_wet in df_no_wet.itertuples(index=False):
                    for row_wet in df_wet.itertuples(index=False):
                        if abs(row_no_wet.event_year - row_wet.event_year) <= max_year_gap:
                            if suffix == "w":
                                wet_t1 = row_wet.t1_mean_w
                                no_wet_t1 = row_no_wet.t1_mean_w
                            else:
                                wet_t1 = row_wet.t1_mean_m
                                no_wet_t1 = row_no_wet.t1_mean_m
                            wet_time = wet_t1 - no_wet_t1
                            # print(f"\t\tno-wet in {row_no_wet.event_year} -> wet in {row_wet.event_year}: {wet_time = :.2f}")
                            wet_time_infos.append({
                                "wet_t1": wet_t1,
                                "no_wet_t1": no_wet_t1,
                                "wet_time": wet_time,
                                "event_venue": event_venue,
                                "wet_year": row_wet.event_year,
                                "no_wet_year": row_no_wet.event_year,
                                "event_country_noc": row_no_wet.event_country_noc,
                                "event_listing": row_no_wet.event_listing,
                                "suffix": suffix,
                                "prog_distance_category": row_no_wet.prog_distance_category,
                                "event_category": row_no_wet.event_category,
                            })

    df_wet_times = pd.DataFrame(wet_time_infos)
    df_wet_times.sort_values("wet_time", inplace=True)
    df_wet_times = df_wet_times[df_wet_times["wet_time"] > min_t1_delta]
    df_wet_times = df_wet_times[df_wet_times["wet_time"] < max_t1_delta]

    print("**Distributions:**")
    d = df_wet_times["event_category"].value_counts()
    d_normed = df_wet_times["event_category"].value_counts(normalize=True)
    print("- Event category:")
    for k in ["wcs", "world-cup", "games"]:
        if k in d:
            print(f"\t- {k.title().replace('Wcs', 'WTCS'):<10}: {d_normed[k]:.0%} ({d[k]})")
    d = df_wet_times["prog_distance_category"].value_counts()
    d_normed = df_wet_times["prog_distance_category"].value_counts(normalize=True)
    print("- Distance category:")
    for k in ["standard", "sprint"]:
        if k in d:
            print(f"\t- {k.replace('standard', 'olympic').title():<10}: {d_normed[k]:.0%} ({d[k]})")

    print("\n**Venues of the comparisons:**")
    df_wet_times["event_venue_with_flag"] = df_wet_times[["event_country_noc", "event_venue"]].apply(
        lambda x: f"{x.event_venue} ( {country_emojis[x.event_country_noc] if x.event_country_noc in country_emojis else x.event_country_noc} )",
        axis=1
    )
    for venue, venue_count in df_wet_times["event_venue_with_flag"].value_counts().to_dict().items():
        print(f"- {venue_count:>2} ({venue_count/len(df_wet_times):>5.1%}): {venue}")
    print()

    df_table = df_wet_times
    df_table["EVENT"] = df_table[["event_country_noc", "event_listing", "event_venue", "suffix"]].apply(
        lambda
            x: f"[{x.event_venue}]({x.event_listing}) ( {country_emojis[x.event_country_noc] if x.event_country_noc in country_emojis else x.event_country_noc} )",
        axis=1
    )
    df_table["t1_wet"] = df_table[["wet_year", "wet_t1"]].apply(
        lambda x: f"{x.wet_t1:.1f} ({x.wet_year:.0f})",
        axis=1
    )
    df_table["t1_no_wet"] = df_table[["no_wet_year", "no_wet_t1"]].apply(
        lambda x: f"{x.no_wet_t1:.1f} ({x.no_wet_year:.0f})",
        axis=1
    )
    df_table["wet_time_str"] = df_table[["wet_time"]].apply(
        lambda x: f"**{x.wet_time:.1f}**",
        axis=1
    )
    df_table["GENDER"] = df_table[["suffix"]].apply(
        lambda x: "M" if x.suffix == "m" else "W",
        axis=1
    )
    df_table = df_table[["EVENT", "GENDER", "t1_wet", "t1_no_wet", "wet_time_str"]]

    df_table = df_table.rename(columns={
        "t1_wet": "T1 with wetsuit".upper() + " (s)",
        "t1_no_wet": "T1 without wetsuit".upper() + " (s)",
        "wet_time_str": "**Extra time for wetsuit".upper() + " (s)**",
    })

    print(df_table.to_markdown(
        index=False,
        colalign=["center"] * len(df_table.columns)
    ))

    print(df_wet_times["wet_time"].describe())
    print("answer 1:")
    print(f'{df_wet_times["wet_time"].mean():.2f} mean')
    print(f'{df_wet_times["wet_time"].median():.2f} median')
    for suffix in ["w", "m"]:
        print(f"\t{suffix.upper()}:")
        print(f'\t\t{df_wet_times[df_wet_times["suffix"] == suffix]["wet_time"].mean():.2f} mean')
        print(f'\t\t{df_wet_times[df_wet_times["suffix"] == suffix]["wet_time"].median():.2f} median')

    fig, ax = plt.subplots(figsize=(16, 16))

    data_min = min(df_wet_times["wet_time"])
    data_max = max(df_wet_times["wet_time"])
    bins = np.arange(int(data_min) - 1, int(data_max) + 1, 1)
    kwargs_hist = {
        "density": True,
        "bins": bins,
    }

    print("w vs m:")
    mean_all = df_wet_times["wet_time"].mean()
    median_all = df_wet_times["wet_time"].median()
    std_all = df_wet_times["wet_time"].std()

    mean_w = df_wet_times[df_wet_times["suffix"] == "w"]["wet_time"].mean()
    mean_m = df_wet_times[df_wet_times["suffix"] == "m"]["wet_time"].mean()
    median_w = df_wet_times[df_wet_times["suffix"] == "w"]["wet_time"].median()
    median_m = df_wet_times[df_wet_times["suffix"] == "m"]["wet_time"].median()
    std_w = df_wet_times[df_wet_times["suffix"] == "w"]["wet_time"].std()
    std_m = df_wet_times[df_wet_times["suffix"] == "m"]["wet_time"].std()

    print(f"Results from **{len(df_wet_times)} comparisons**:")
    print(f'- The wetsuit **adds `{mean_all:.1f}` (mean) or `{median_all:.1f}` (median) seconds in T1**. (`std = {std_all:.1f}`)')
    print(f'- **Women are `{mean_w - mean_m:.1f}` (with means) or `{median_w - median_m:.1f}` (with medians) seconds slower** than men.')
    print(f'\t- Women only: `mean = {mean_w:.1f}`, `median = {median_w:.1f}`. (`std = {std_w:.1f}`)')
    print(f'\t- Men only: `mean = {mean_m:.1f}`, `median = {median_m:.1f}`. (`std = {std_m:.1f}`)')

    ax.hist(
        df_wet_times["wet_time"],
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
            df_wet_times[df_wet_times["suffix"] == suffix]["wet_time"],
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
    mu, std = norm.fit(df_wet_times["wet_time"])
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'gray', linewidth=1, linestyle="-", label=f"Normal distribution ($\mu={mu:.1f}$, $\sigma={std:.1f}$)")

    ax.set_ylabel("Percentage".upper(), fontsize=16)
    ax.set_xlabel("EXTRA TIME (s) ADDED BY WETSUIT DURING T1", fontsize=16)

    ax.tick_params(axis='both', which='major', labelsize=14)

    ax.grid()
    ax.set_xlim(int(data_min) - 2, int(data_max) + 2)
    ax.set_xticks(range(int(data_min) - 1, int(data_max) + 2, 1))
    ax.legend(loc='upper right', fontsize=15)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    fig.suptitle(
        f"WETSUIT IMPACT DURING T1\nusing {len(df_wet_times)} year-to-year comparisons",
        fontsize=18
    )
    plt.tight_layout()
    add_watermark(fig, y=0.92, x=0.12)
    plt.savefig(str(res_dir / "t1_with_wetsuit.png"), dpi=300)
    plt.show()


### ### ### ###
### METHOD 2/2
### ### ### ###

class Model:
    def __init__(self):
        pass

    def fit(self, df):
        raise NotImplementedError

    def infer(self, t1_men) -> float:
        raise NotImplementedError

    @staticmethod
    def clean_up_df(df):
        df = df[~df["wetsuit_m"]]
        df = df[~df["wetsuit_w"]]
        df = df[df["t1_mean_m"] > t1_config["wm"]["min_t1"]]
        df = df[df["t1_mean_w"] > t1_config["wm"]["min_t1"]]

        print(f"using {len(df)} events: women and men without wetsuit (after filtering)")
        return df


class Model1d(Model):
    def __init__(self):
        super().__init__()
        self.wm_diff = 0

    def fit(self, df):
        df = self.clean_up_df(df)
        df[f"t1_diff"] = df[f"t1_mean_w"] - df[f"t1_mean_m"]
        df[f"t1_diff_percent"] = df[f"t1_diff"] / df[f"t1_mean_m"]
        self.wm_diff = df[f"t1_diff_percent"].mean()

    def infer(self, t1_men):
        return t1_men * (1 + self.wm_diff)


class Model1p5d(Model):
    def __init__(self):
        super().__init__()
        self.wm_diff_run = 0
        self.helmet = t1_config["wm"]["helmet"]

    def fit(self, df):
        df = self.clean_up_df(df)
        df["t1_diff"] = df["t1_mean_w"] - df["t1_mean_m"]  # the two helmet terms cancel
        df["t1_diff_percent"] = df["t1_diff"] / (df["t1_mean_m"] - self.helmet)

        # remove outliers
        diff_min = 0
        diff_max = 0.3
        df = df[df["t1_diff_percent"]>diff_min]
        df = df[df["t1_diff_percent"]<diff_max]

        mean = df['t1_diff_percent'].mean()
        median = df['t1_diff_percent'].median()
        std = df['t1_diff_percent'].std()
        self.wm_diff_run = mean

        # plot distribution
        fig, ax = plt.subplots(figsize=(16, 16))
        data_min = df["t1_diff_percent"].min()
        data_max = df["t1_diff_percent"].max()
        bins = np.arange(int(data_min) - 1, int(data_max) + 1, 0.01)
        kwargs_hist = {
            "density": True,
            "bins": bins,
        }
        ax.set_xlim(data_min - 0.05, data_max + 0.05)
        ax.xaxis.set_major_formatter(PercentFormatter(1))
        ax.axvline(
            mean,
            linestyle="-",
            color="red",
            label=f"{mean = :.1%}"
        )
        ax.axvline(
            median,
            color="k",
            linestyle="--",
            label=f"{median = :.1%}"
        )
        ax.legend()
        ax.grid()
        ax.set_xlabel("wm_diff_run")
        ax.set_ylabel("percentage")

        plt.hist(df["t1_diff_percent"], **kwargs_hist)
        title = (
            f"w/m difference at running during T1: {self.wm_diff_run = :.2%}"
            f"\nmedian = {median:.2%}"
            f"\nstd = {std:.2%}"
        )
        plt.title(title)
        print(title)

        from scipy.stats import norm
        mu, std = norm.fit(df["t1_diff_percent"])
        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mu, std)
        plt.plot(x, p, 'gray', linewidth=1, linestyle="-",
                 label=f"Normal distribution ($\mu={mu:.1f}$, $\sigma={std:.1f}$)")

        plt.savefig(res_dir / "wm_diff_run_t1.png")
        plt.show()

    def infer(self, t1_men):
        """
        x_run = (w-m)/m
        x_run*m = w-m
        w = x_run*m + m
        w_run = m_run * (1 + x_run)
        """
        return (t1_men - self.helmet) * (1 + self.wm_diff_run) + self.helmet


class Model2d(Model):
    def __init__(self):
        super().__init__()
        self.helmet = 0
        self.wm_diff = 0

    def fit(self, df):
        df = self.clean_up_df(df)


        """
        model: without wetsuit
            t1_m = run_m + helmet
            t1_w = run_w + helmet
            run_w = run_m * (1 + wm_diff/100)

            wm_diff = (run_w - run_m) / run_m  # i.e. how much slower do women run?

        hence:
            t1_w = (t1_m - helmet) * (1 + wm_diff/100) + helmet

        two unknowns:
            helmet
            wm_diff

        constraints:
            helmet in [1, 4]
            wm_diff in [1, 20]
        """

        helmet_min = 1.1
        helmet_max = 4
        wm_diff_min = 0
        wm_diff_max = 20
        n_per_variable = 101

        all_helmets = np.linspace(helmet_min, helmet_max, n_per_variable)
        all_wm_diff = np.linspace(wm_diff_min, wm_diff_max, n_per_variable)

        heat_map = np.zeros((n_per_variable, n_per_variable))
        for i_helmet, helmet in enumerate(all_helmets):
            for i_wm_diff, wm_diff in enumerate(all_wm_diff):
                # print(f"{helmet = }, {wm_diff = }")
                t1_w_estimated = (df["t1_mean_m"] - helmet) * (1 + wm_diff / 100) + helmet
                cost = (t1_w_estimated - df["t1_mean_w"]) ** 2
                heat_map[i_helmet, i_wm_diff] = np.mean(cost)

        plt.imshow(heat_map)
        # set x and y ticks and labels
        plt.xticks(np.arange(n_per_variable), all_wm_diff)
        plt.yticks(np.arange(n_per_variable), all_helmets)

        # set x and y titles
        plt.xlabel("wm_diff")
        plt.ylabel("helmet", rotation=90)

        # show minimum value
        i_optimum_helmet, i_optimum_wm_diff = np.unravel_index(heat_map.argmin(), heat_map.shape)
        optimum_wm_diff = all_wm_diff[i_optimum_wm_diff]
        optimum_helmet = all_helmets[i_optimum_helmet]

        title_txt = f"At T1 with no wetsuit:\nwomen run {optimum_wm_diff:.2f} % slower\nhelmet time = {optimum_helmet:.2f} s"
        print(title_txt)
        plt.title(title_txt)

        plt.text(i_optimum_wm_diff, i_optimum_helmet, np.min(heat_map), ha='left', va='bottom', fontsize=8)

        # plt.show()

        self.helmet = optimum_helmet
        self.wm_diff = optimum_wm_diff

    def infer(self, t1_men) -> float:
        return (t1_men - self.helmet) * (1 + self.wm_diff / 100) + self.helmet


def method_wm(df):
    """
    derive a function f:
        input: t1 duration for men, without wetsuit
        output: t1 duration for women, without wetsuit, on the same course

    then use the ~10 events where women had the wetsuit, and men did not:
        first, use f to estimate duration for `women-no-wetsuit` (hypothetical)
        compare `women-no-wetsuit` and `women-with-wetsuit`
        conclude about the time required to remove the wetsuit, for women

    advantage: women and men run the exact same course
    drawbacks: no estimation for men, and f is tricky to derive

    what model for f?
        linear?
        affine?
        neural network? how many params?
    """
    if t1_config["wm"]["model"] == "1d":
        model = Model1d()
    elif t1_config["wm"]["model"] == "1.5d":
        model = Model1p5d()
    elif t1_config["wm"]["model"] == "2d":
        model = Model2d()
    else:
        raise ValueError(f"no model in config: {t1_config['wm']}")

    model.fit(df.copy())

    ### ### ### ### ### ### ### ### ### ### ###
    # use the learnt model to make prediction
    ### ### ### ### ### ### ### ### ### ### ###

    df2 = df.copy()
    df2 = df2[df2["wetsuit_m"] != df2["wetsuit_w"]]
    df2 = df2[df2["wetsuit_w"]]
    df2["t1_w_pred"] = df2[["t1_mean_m"]].apply(
        lambda x: model.infer(x.t1_mean_m),
        axis=1
    )

    df2["wet_time_w"] = df2["t1_mean_w"] - df2["t1_w_pred"]

    # create markdown table
    df_table = df2.copy()
    # merge "event_country_noc" and "event_venue"
    df_table["event"] = df_table[["event_country_noc", "event_listing", "event_venue"]].apply(
        lambda
            x: f"[{x.event_venue}]({x.event_listing}) ( {country_emojis[x.event_country_noc] if x.event_country_noc in country_emojis else x.event_country_noc} )",
        axis=1
    )
    df_table.sort_values(["wet_time_w"], inplace=True)

    df_table = df_table[["event_year", "event", "wet_time_w", "event_category"]]
    df_table["wet_time_w"] = df_table["wet_time_w"].apply(lambda x: f"**{x:.1f}**")
    df_table["event_category"] = df_table["event_category"].apply(lambda x: x.replace("wcs", "WTCS").upper())
    df_table.columns = ["YEAR", "EVENT", "**EXTRA TIME FOR WETSUIT** (women) (s)", "EVENT CATEGORY"]
    print(df_table.to_markdown(
        index=False,
        colalign=["center"] * len(df_table.columns)
    ))

    print(df2["wet_time_w"].describe())
    print("answer 2:")
    print(f'{df2["wet_time_w"].mean():.2f} mean')
    print(f'{df2["wet_time_w"].median():.2f} median')
    print(f"{len(df2)} events")




def main():
    df = get_df(
        use_cache=False
    )

    method_events(df.copy())

    print("### \n" * 3)
    method_wm(df.copy())


if __name__ == '__main__':
    main()
