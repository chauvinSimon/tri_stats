"""
https://data.un.org/Data.aspx?d=POP&f=tableCode%3A55
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from utils_countries import convert_country_alpha2_to_country_name, convert_country_name_to_country_alpha2, \
    convert_country_alpha2_to_continent
from utils import json_dump, reference_month_of_birth_path, reference_month_of_birth_data_path, res_dir, add_watermark

plt.rcParams["font.family"] = "monospace"  # todo: set in global config
plt.rcParams['mathtext.default'] = 'rm'
plt.rcParams['mathtext.fontset'] = 'cm'  # "stix

EXPECTED_N_ENTRIES = 230_254_524



def get_month_distribution(df):
    # drop "Total"
    df = df[df["Month"] != "Total"]
    # drop "Month" that contain a dash symbol
    df = df[~df["Month"].str.contains("-")]
    # drop "Month" that is Unknown
    df = df[df["Month"] != "Unknown"]

    total_births = df["Value"].sum()
    n_unique_countries = df["country"].nunique()
    unique_years = [int(y) for y in df["Year"].unique()]
    info = f"{total_births:,.0f} births\n{n_unique_countries} countries\n{max(unique_years) - min(unique_years) + 1} years ({min(unique_years)} - {max(unique_years)})"

    # convert Month to int: using the index: January = 1, February = 2 ...
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                   'November', 'December']
    assert set(df["Month"].unique()) == set(month_names), df["Month"].unique()
    df["Month"] = df["Month"].apply(lambda x: month_names.index(x) + 1)

    df["Value"] = df["Value"].astype(int)
    df["Month"] = df["Month"].astype(int)

    plot_continents(df)

    # group by Month and only keep Value, as int
    df = df[["Month", "Value"]]
    df = df.groupby("Month").sum()

    # plot not the absolute values, but the percentage
    df["Value"] = df["Value"] / df["Value"].sum() * 100

    json_dump(data=df.Value.to_list(), p=reference_month_of_birth_path)

    fig, ax = plt.subplots(figsize=(16, 16))

    df.plot.bar(
        y="Value",
        label="data: UN",
        ax=ax,
        color="dodgerblue",
        edgecolor="black",
    )

    # todo: deactivate legend of the bar plot

    # add values on the top of each bar
    for index, row in df.iterrows():
        plt.text(
            index - 1,
            row["Value"] + 0.1,
            f"{row['Value']:.2f}%",
            ha="center",
            fontsize=15
        )

    plt.xticks(rotation=0, fontsize=15)
    plt.yticks(range(0, int(max(df["Value"].max(), 10)) + 1), fontsize=15)
    plt.grid(axis="y", alpha=0.5)

    plt.ylabel("PERCENT", fontsize=20)
    plt.xlabel("")

    plt.title(f"MONTH-OF-BIRTH DISTRIBUTION\ndata.UN.org\n{info}", fontsize=20)
    plt.axhline(100 / 12, linestyle="-.", alpha=0.5, color="darkblue", label=f"uniform: {100 / 12:.1f}%")
    plt.legend(fontsize=15)
    plt.tight_layout()
    add_watermark(fig, y=0.95)
    plt.savefig(str(res_dir / "birth_months_un.png"), dpi=300)

    plt.show()


def plot_continents(df):
    def convert_country_name_to_country_alpha2_with_correction(country_name: str) -> str:
        correction = {
            "Republic of Korea": "KR",  # 255
            "Saint Helena ex. dep.": "SH",  # 146
            "China, Hong Kong SAR": "HK",  # 145
            "United Kingdom of Great Britain and Northern Ireland": "GB",  # 144
            "China, Macao SAR": "CN",  # 143
            "Czechia": "CZ",  # 143
            "Netherlands (Kingdom of the)": "NL",  # 130
            "Republic of Moldova": "MD",  # 117
            "Venezuela (Bolivarian Republic of)": "VE",  # 117
            "North Macedonia": "MK",  # 104
            "Iran (Islamic Republic of)": "IR",  # 78
            "Reunion": "RE",  # 78
            "Türkiye": "TR",  # 52
        }
        if country_name in correction:
            return correction[country_name]
        else:
            assert convert_country_name_to_country_alpha2(country_name) is not None, country_name
            return convert_country_name_to_country_alpha2(country_name)

    df["country_alpha2"] = df["country"].apply(convert_country_name_to_country_alpha2_with_correction)

    # ###

    fig = plt.figure(figsize=(12, 12))

    df["continent"] = df["country_alpha2"].apply(lambda x: convert_country_alpha2_to_continent(x))

    missing_countries = dict(df[df["continent"].isna()][["country", "country_alpha2"]].value_counts("country"))
    for k, v in missing_countries.items():
        print(f"{k}: {v}")

    # sum all values of df
    assert EXPECTED_N_ENTRIES == df["Value"].sum(), df["Value"].sum()

    continent_value_counts = df[["continent", "Value"]].groupby("continent").sum("Value")
    n_entries = continent_value_counts["Value"].sum()
    assert EXPECTED_N_ENTRIES == n_entries, n_entries

    continent_value_counts = continent_value_counts["Value"].sort_values(ascending=False)
    continent_value_counts.plot.bar(color="deepskyblue", edgecolor="black")

    plt.xticks(rotation=45, ha="right", fontsize=12)

    plt.ylabel("count".upper(), fontsize=15)
    plt.xlabel("")

    for index, (continent, value) in enumerate(continent_value_counts.items()):
        countries_counts = df[df["continent"] == continent].groupby("country_alpha2").sum("Value")
        countries_counts = countries_counts["Value"].sort_values(ascending=False).head(5)

        country_names_counts = {
            convert_country_alpha2_to_country_name(k): v
            for k, v in dict(countries_counts).items()
        }
        print(f"{continent}: {country_names_counts}")

        txt = "\n".join(f"{k}: {v:,.0f}" for k, v in country_names_counts.items())
        txt += "\n..."
        plt.text(
            index,
            continent_value_counts[continent] + 1 * 1_000_000,
            txt,
            ha="center",
            fontsize=8,
        )

        plt.text(
            index,
            value - 2 * 1_000_000,
            f"{value / n_entries * 100:.1f}%",
            ha="center",
            fontsize=10,
        )

    plt.ylim(0, max(continent_value_counts) * 1.1)

    plt.title(f'CONTINENT DISTRIBUTION\ndata.UN.org\n({n_entries:,} entries)', fontsize=20)

    plt.tight_layout()
    add_watermark(fig, y=0.95)
    plt.savefig(str(res_dir / "birth_continents_un.png"), dpi=300)

    plt.show()

    # ### plot continent/month distribution

    assert EXPECTED_N_ENTRIES == df["Value"].sum(), df["Value"].sum()
    continent_months_abs = df[["continent", "Month", "Value"]].groupby(["continent", "Month"]).sum("Value")

    n_continents = len(continent_months_abs.groupby("continent"))
    bar_width = 1 / (1 + n_continents)
    offsets = np.arange(0, len(continent_months_abs) * bar_width, bar_width)
    offsets = offsets - 0.4

    fig = plt.figure(figsize=(12, 12))
    plt.title(f"QUARTER-OF-BIRTH DISTRIBUTION\nBY CONTINENT\ndata.UN.org\n({n_entries:,} entries)", fontsize=18)
    # group the 12 values in 4 groups of 3: (1,2,3) (4,5,6) (7,8,9) (10,11,12)
    df['quarter'] = ((df.Month - 1) // 3) + 1
    df['quarter'] = df['quarter'].apply(lambda _x: 'Q' + str(_x))
    df2 = df[["continent", "Value", "quarter"]].groupby(["continent", "quarter"]).sum("Value")
    df2.reset_index(inplace=True)
    df2.pivot(index='continent', columns='quarter', values='Value').plot(
        kind="bar",
        edgecolor="black",
        ax=plt.gca(),
    )
    plt.legend(fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=14)
    plt.xlabel("CONTINENT", fontsize=15)
    plt.ylabel("COUNT", fontsize=15)
    plt.tight_layout()
    add_watermark(fig, y=0.96)
    plt.savefig(str(res_dir / "continent_quarters_un.png"), dpi=300)
    plt.show()

    dfs = []
    for continent, df_continent in df2.groupby("continent"):
        total = df_continent["Value"].sum()
        df_continent["ValueNormalized"] = 100 * df_continent["Value"] / total
        dfs.append(df_continent)
        print()
    df3 = pd.concat(dfs)

    # ###

    fig = plt.figure(figsize=(12, 12))
    plt.title(f"QUARTER-OF-BIRTH DISTRIBUTION\nBY CONTINENT\n(NORMALIZED)\ndata.UN.org\n({n_entries:,} entries)", fontsize=18)
    df5 = df3.pivot(index='continent', columns='quarter', values='ValueNormalized')
    p5 = df5.plot(
        kind="bar",
        edgecolor="black",
        ax=plt.gca(),
    )
    for p in p5.containers:
        labels = [f'{v.get_height():0.1f}%' for v in p]
        p5.bar_label(p, labels=labels, label_type='edge', fontsize=9, rotation=90, padding=5)
    p5.margins(y=0.2)
    plt.axhline(
        100 / 4,
        linestyle="-.",
        linewidth=1,
        alpha=0.5,
        color="black",
        label=f"uniform: {100 / 12:.1f}%"
    )
    plt.legend(ncol=n_continents + 1, fontsize=12)
    plt.ylabel("percentage".upper(), fontsize=15)
    plt.xlabel("CONTINENT", fontsize=15)
    plt.grid(axis="y", alpha=0.5)
    plt.xticks(rotation=45, ha="right", fontsize=12)
    plt.yticks(fontsize=15)
    plt.tight_layout()
    add_watermark(fig, y=0.95)
    plt.savefig(str(res_dir / "quarter_by_continent_un_normalized.png"), dpi=300)
    plt.show()

    # ###

    fig = plt.figure(figsize=(12, 12))
    plt.title(f"QUARTER-OF-BIRTH DISTRIBUTIONS\nBY CONTINENT\n(NORMALIZED)\n({n_entries:,} entries)", fontsize=18)
    df4 = df3.pivot(index='quarter', columns='continent', values='ValueNormalized')
    p4 = df4.plot(
        kind="bar",
        edgecolor="black",
        ax=plt.gca(),
    )

    for p in p4.containers:
        labels = [f'{v.get_height():0.1f}%' for v in p]
        p4.bar_label(p, labels=labels, label_type='edge', fontsize=9, rotation=90, padding=5)
    p4.margins(y=0.2)
    plt.axhline(
        100 / 4,
        linestyle="-.",
        linewidth=1,
        alpha=0.5,
        color="black",
        label=f"uniform: {100 / 12:.1f}%"
    )
    plt.legend(ncol=n_continents + 1, fontsize=10)
    plt.ylabel("percentage".upper(), fontsize=15)
    plt.grid(axis="y", alpha=0.5)
    plt.xlabel("quarter".upper(), fontsize=15)
    # rotate x tick labels
    plt.xticks(rotation=0, ha="right", fontsize=15)

    plt.yticks(fontsize=15)
    plt.tight_layout()
    add_watermark(fig, y=0.96)
    plt.savefig(str(res_dir / "quarter_by_continent_un_normalized_2.png"), dpi=300)
    plt.show()

    # ###

    for title_suffix, use_norm in [("ABSOLUTE", False), ("NORMALIZED", True)]:
        fig = plt.figure(figsize=(12, 12))
        plt.title(f"MONTH-OF-BIRTH DISTRIBUTION\nBY CONTINENT\n({title_suffix})\ndata.UN.org\n({n_entries:,} entries)", fontsize=18)
        ax = plt.gca()

        if use_norm:
            plt.axhline(
                100 / 12,
                linestyle="-.",
                linewidth=1,
                alpha=0.5,
                color="black",
                label=f"uniform: {100 / 12:.1f}%"
            )
            plt.ylabel("percentage".upper(), fontsize=15)
            plt.grid(axis="y", alpha=0.5)
        else:
            plt.ylabel("count".upper(), fontsize=15)

        for i_group, group in enumerate(continent_months_abs.groupby("continent")):
            y = list(group[1].values.reshape(-1))
            if use_norm:
                y = [100 * e / sum(y) for e in y]
            y = np.array(y)
            x = np.arange(1, 13) + offsets[i_group]
            ax.bar(
                x,
                height=y,
                label=group[0],
                width=bar_width,
                edgecolor="black",
            )
            if use_norm:
                for _x, _y in zip(x, y):
                    plt.text(
                        _x + 0.025,
                        _y + 0.15,
                        f"{_y:.1f}",
                        ha="center",
                        rotation=90,
                        fontsize=8
                    )

        plt.legend()
        plt.xticks(np.arange(1, 13), np.arange(1, 13), fontsize=15)
        plt.yticks(fontsize=15)
        plt.xlabel("")
        plt.tight_layout()
        add_watermark(fig, y=0.95)
        plt.savefig(str(res_dir / f"birth_month_by_continents_un_{title_suffix.lower()}.png"), dpi=300)
        plt.show()

    # ### cumulative

    fig = plt.figure(figsize=(12, 12))
    plt.title(f"MONTH-OF-BIRTH DISTRIBUTION\nCUMULATIVE BY CONTINENT\ndata.UN.org\n({n_entries:,} entries)", fontsize=18)
    ax = plt.gca()

    so_far_plotted = np.zeros((12,))
    for i_group, group in enumerate(continent_months_abs.groupby("continent")):
        y = np.array(list(group[1].values.reshape(-1)))
        ax.bar(
            np.arange(1, 13),
            height=y,
            label=group[0],
            width=0.9,
            bottom=so_far_plotted,
            edgecolor="black",
        )
        so_far_plotted += y

    plt.axhline(n_entries / 12, linestyle="-.", alpha=0.5, color="darkblue", label=f"uniform: {100 / 12:.2f}%")

    for index, val in enumerate(so_far_plotted):
        plt.text(
            index + 1,
            val + 0.4 * 1_000_000,
            f"{val / n_entries * 100:.2f}%",
            ha="center",
            fontsize=15
        )

    plt.legend()
    plt.xticks(np.arange(1, 13), np.arange(1, 13), fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel("count".upper(), fontsize=15)
    plt.xlabel("")
    plt.tight_layout()
    add_watermark(fig, y=0.96)
    plt.savefig(str(res_dir / "birth_continents_un_cumulative.png"), dpi=300)
    plt.show()

    # ### check results of month distribution, independent of continent

    assert EXPECTED_N_ENTRIES == continent_months_abs["Value"].sum()
    all_per_month = {
        k: 0
        for k in np.arange(1, 13)
    }
    for k, v in dict(continent_months_abs.Value).items():
        all_per_month[k[1]] += v

    assert EXPECTED_N_ENTRIES == sum(all_per_month.values())
    assert so_far_plotted.tolist() == list(all_per_month.values())

    for k, v in all_per_month.items():
        all_per_month[k] = v / EXPECTED_N_ENTRIES * 100
        print(f"{k}: {all_per_month[k]:.1f}%")


def main():
    df = pd.read_csv(str(reference_month_of_birth_data_path))
    print(df.columns)

    # rename "Country or Area" to "country"
    df = df.rename(columns={"Country or Area": "country"})

    # drop rows that contain numbers as "country"
    df = df[~df["country"].str.isnumeric()]

    # drop rows "footnoteSeqID" as "country"
    df = df[~df["country"].str.contains("footnoteSeqID")]

    # for country in df["country"].unique():
    #     print(country)

    get_month_distribution(df)


if __name__ == '__main__':
    main()
