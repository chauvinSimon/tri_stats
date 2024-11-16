import json
from pathlib import Path
import yaml


res_dir = Path(__file__).parent.parent / "res"
res_dir.mkdir(exist_ok=True)

cache_dir = Path(__file__).parent.parent / "cache"
cache_dir.mkdir(exist_ok=True)

data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)

ignored_dir = Path(__file__).parent.parent / "ignored"
ignored_dir.mkdir(exist_ok=True)

reference_month_of_birth_path = data_dir / "reference_month_of_birth.json"
reference_month_of_birth_data_path = data_dir / "UNdata_2004_1994.csv"


def add_watermark(fig, x=0.92, y=0.97):
    fig.text(
        x=x,
        y=y,
        s='©SimonCHAUVIN',
        transform=fig.transFigure,
        fontsize=12,
        color='grey',
        ha='center',
        va='center',
        alpha=0.7
    )


def json_dump(
        data,
        p: Path
) -> None:
    with p.open("w") as f:
        json.dump(data, f)


def json_load(
        p: Path
):
    with p.open("r") as f:
        return json.load(f)


def yaml_load(file_path: Path):
    """Load data from a YAML file."""
    with file_path.open('r') as f:
        return yaml.safe_load(f)


def load_config():
    return yaml_load(Path(__file__).parent.parent / "config.yaml")


country_emojis = {
    'AIN': ':white_flag:',
    'ARG': ':argentina:',
    'AUS': ':australia:',
    'AUT': ':austria:',
    'AZE': ':azerbaijan:',
    'BAR': ':barbados:',
    'BEL': ':belgium:',
    'BER': ':bermuda:',
    'BRA': ':brazil:',
    'CAN': ':canada:',
    'CHI': ':chile:',
    'CHN': ':cn:',
    'COL': ':colombia:',
    'CRC': ':costa_rica:',
    'CZE': ':czech_republic:',
    'DEN': ':denmark:',
    'ECU': ':ecuador:',
    'ESP': ':es:',
    'EST': ':estonia:',
    'FRA': ':fr:',
    'GBR': ':gb:',
    'GER': ':de:',
    'HKG': ':hong_kong:',
    'HUN': ':hungary:',
    'IRL': ':ireland:',
    'ISR': ':israel:',
    'ITA': ':it:',
    'JPN': ':jp:',
    'KAZ': ':kazakhstan:',
    'KOR': ':kr:',
    'LUX': ':luxembourg:',
    'MAR': ':morocco:',
    'MEX': ':mexico:',
    'NED': ':netherlands:',
    'NOR': ':norway:',
    'NZL': ':new_zealand:',
    'PER': ':peru:',
    'POR': ':portugal:',
    'POL': ':poland:',
    'PUR': ':puerto_rico:',
    'ROU': ':romania:',
    'RUS': ':ru:',
    'RSA': ':south_africa:',
    'SLO': ':slovenia:',
    'SUI': ':switzerland:',
    'SVK': ':slovakia:',
    'SWE': ':sweden:',
    'TUR': ':tr:',
    'UAE': ':united_arab_emirates:',
    'UKR': ':ukraine:',
    'USA': ':us:',
    'UZB': ':uzbekistan:'
}




import matplotlib.colors as mcolors

def interpolate_colors(color1, color2, values, output_format='hex'):
    """
    Interpolate between two colors based on a list of float values.

    Parameters:
    color1 (str): The starting color in any format understood by matplotlib.
    color2 (str): The ending color in any format understood by matplotlib.
    values (list of float): List of values to interpolate between color1 and color2.
    output_format (str): The format of the output colors. Can be 'hex', 'rgb', or 'rgba'.

    Returns:
    list: List of interpolated colors in the specified format.
    """
    # Normalize the list of floats
    min_val = min(values)
    max_val = max(values)
    normalized_values = [(v - min_val) / (max_val - min_val) for v in values]

    # Convert color1 and color2 to RGB tuples
    color1_rgb = mcolors.to_rgb(color1)
    color2_rgb = mcolors.to_rgb(color2)

    # Interpolate colors
    interpolated_colors = [
        (
            color1_rgb[0] + (color2_rgb[0] - color1_rgb[0]) * v,
            color1_rgb[1] + (color2_rgb[1] - color1_rgb[1]) * v,
            color1_rgb[2] + (color2_rgb[2] - color1_rgb[2]) * v,
        )
        for v in normalized_values
    ]

    if output_format == 'rgb':
        return interpolated_colors
    elif output_format == 'rgba':
        return [(r, g, b, 1.0) for r, g, b in interpolated_colors]
    elif output_format == 'hex':
        return [mcolors.to_hex(c) for c in interpolated_colors]
    else:
        raise ValueError("Invalid output_format. Choose 'hex', 'rgb', or 'rgba'.")

# # Example usage:
# color1 = "#32cd32"  # LimeGreen
# color2 = "#0000ff"  # Blue
# values = [0.1, 0.5, 0.9]
#
# # Get colors in RGB format
# output_colors_rgb = interpolate_colors(color1, color2, values, output_format='rgb')
# print("RGB format:", output_colors_rgb)
#
# # Get colors in RGBA format
# output_colors_rgba = interpolate_colors(color1, color2, values, output_format='rgba')
# print("RGBA format:", output_colors_rgba)
#
# # Get colors in Hex format
# output_colors_hex = interpolate_colors(color1, color2, values, output_format='hex')
# print("Hex format:", output_colors_hex)