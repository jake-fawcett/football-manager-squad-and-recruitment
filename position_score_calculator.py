import pandas as pd
import argparse

# Define Player attributes
# TODO: Add roles.
goalkeeper = {
    "role_name": "goalkeeper",
    "primary_multiplier": 5,
    "primary_attributes": ["Agi", "Ref"],
    "secondary_multiplier": 3,
    "secondary_attributes": ["1v1", "Ant", "Cmd", "Cnt", "Kic", "Pos"],
    "tertiary_multiplier": 1,
    "tertiary_attributes": ["Acc", "Aer", "Cmp", "Dec", "Fir", "Han", "Pas", "Thr", "Vis"]
}

fullback = {
    "role_name": "fullback",
    "primary_multiplier": 5,
    "primary_attributes": ["Wor", "Acc", "Pac", "Sta"],
    "secondary_multiplier": 3,
    "secondary_attributes": ["Cro", "Dri", "Mar", "OtB", "Tck", "Tea"],
    "tertiary_multiplier": 1,
    "tertiary_attributes": ["Agi", "Ant", "Cnt", "Dec", "Fir", "Pas", "Pos", "Tec"]
}

def load_html_data_to_dataframe(filepath: str) -> pd.DataFrame:
    """Read HTML file exported by FM into a Dataframe

    Keyword arguments:
    filepath -- path to fm player html file
    """
    player_df = pd.read_html(filepath, header=0, encoding="utf-8", keep_default_na=False)[0]
    # Clean Dataframe to get rid of unknown values and ability ranges (takes the lowest value)
    # This casts to a string to be able to split, so we have to cast back to an int later.
    player_df = player_df.replace("-", 0)
    player_df = player_df.map(lambda x: str(x).split("-")[0])
    return player_df

def export_html_from_dataframe(player_df: pd.DataFrame, filepath: str) -> str:
    """Export Dataframe as html with jQuery Data Tables
    Taken from: https://www.thepythoncode.com/article/convert-pandas-dataframe-to-html-table-python.

    Keyword arguments:
    filepath -- path to fm player html file
    """
    table_html = player_df.to_html(table_id="table", index=False)
    html = f"""
    <html>
    <header>
        <link href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css" rel="stylesheet">
    </header>
    <body>
    {table_html}
    <script src="https://code.jquery.com/jquery-3.6.0.slim.min.js" integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready( function () {{
            $('#table').DataTable({{
                paging: false,
                order: [[12, 'desc']],
                // scrollY: 400,
            }});
        }});
    </script>
    </body>
    </html>
    """
    open(filepath, "w", encoding="utf-8").write(html)

# TODO: Do I even want this?
def calc_composite_scores(player_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Speed, Workrate and Set Piece scores

    Keyword arguments:
    player_df: Dataframe of Players and Attributes
    """
    player_df['Spd'] = ( player_df['Pac'] + player_df['Acc'] ) / 2
    player_df['Work'] = ( player_df['Wor'] + player_df['Sta'] ) / 2
    player_df['SetP'] = ( player_df['Jum'] + player_df['Bra'] ) / 2
    return player_df

def sum_attributes(player_df: pd.DataFrame, role: str, attribute_type: str, attributes: [str]) -> pd.DataFrame:
    """Create a new Column containing the sum of provided attribute columns

    Keyword arguments:
    player_df: Dataframe of Players and Attributes
    role: Name of role to be used as additional column in dataframe
    attribute_type: Type of Attribute [Primary, Secondary, Tertiary]
    attributes: List of Attributes to Sum
    """
    player_df[f'{role}_{attribute_type}'] = 0
    for attribute in attributes:
        player_df[f'{role}_{attribute_type}'] += pd.to_numeric(player_df[attribute])
    player_df[f'{role}_{attribute_type}'] = round(player_df[f'{role}_{attribute_type}'] / len(attributes), 2)
    return player_df

def calc_role_scores(player_df: pd.DataFrame, role: dict) -> pd.DataFrame:
    """Calculate Player Role scores based on selected attributes.

    Keyword arguments:
    player_df: Dataframe of Players and Attributes
    role: Dictionary containing role name, role attributes and role attribute weightings
    """
    player_df = sum_attributes(player_df, role["role_name"], "primary", role["primary_attributes"])
    player_df = sum_attributes(player_df, role["role_name"], "secondary", role["secondary_attributes"])
    player_df = sum_attributes(player_df, role["role_name"], "tertiary", role["tertiary_attributes"])
    divisor = role["primary_multiplier"] + role["secondary_multiplier"] + role["tertiary_multiplier"]
    player_df[f'{role["role_name"]}'] = round((((player_df[f'{role["role_name"]}_primary'] * 5) + (player_df[f'{role["role_name"]}_secondary'] * 3) + (player_df[f'{role["role_name"]}_tertiary'] * 1)) / divisor ), 2)
    return player_df

def calc_role_scores_for_tactic_roles(player_df: pd.DataFrame, tactic_roles: [dict]):
    for role in tactic_roles:
        player_df = calc_role_scores(player_df, role)
    return player_df

if __name__ == "__main__":
    # Parse Input args
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-filepath", type=str, help="Path to Input Html file")
    parser.add_argument("-o", "--output-filepath", type=str, help="Path to Export resultant Html file")
    parser.add_argument("-r", "--roles", nargs='+', type=str, help="Space seperated list of roles for Evaluation")
    args = parser.parse_args()
    input_filepath = args.input_filepath
    output_filepath = args.output_filepath
    roles = args.roles

    # Take Role arg and convert to list of role dictionaries
    tactic_roles = []
    for role in roles:
        tactic_roles.append(globals()[role])

    # Inport data, calculate scores for role, export results as html
    player_df = load_html_data_to_dataframe(input_filepath)
    player_df = calc_role_scores_for_tactic_roles(player_df, tactic_roles)
    export_html_from_dataframe(player_df, output_filepath)
