import pandas as pd
import argparse

def load_data(filepath: str) -> pd.DataFrame:
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
    return player_df

def calc_role_scores(player_df: pd.DataFrame, role: str, primary_attributes: [str], secondary_attributes: [str], tertiary_attributes: [str]) -> pd.DataFrame:
    """Calculate Player Role scores based on selected attributes.

    Keyword arguments:
    player_df: Dataframe of Players and Attributes
    role: Name of role to be used as additional column in dataframe
    primary_attributes: List of Most important attributes for a role
    secondary_attributes: List of Most secondary attributes for a role
    tertiary_attributes: List of Most tertiary attributes for a role
    """
    player_df = sum_attributes(player_df, role, "primary", primary_attributes)
    player_df = sum_attributes(player_df, role, "secondary", secondary_attributes)
    player_df = sum_attributes(player_df, role, "tertiary", tertiary_attributes)
    divisor = (len(primary_attributes) * 5) + (len(secondary_attributes) * 3) + (len(tertiary_attributes) * 1)
    player_df[f'{role}'] = (((player_df[f'{role}_primary'] * 5) + (player_df[f'{role}_secondary'] * 3) + (player_df[f'{role}_tertiary'] * 1)) / divisor )
    return player_df

def calc_player_scores(player_df: pd.DataFrame):
    # TODO: Create objects for each role that can be used here.
    player_df = calc_role_scores(player_df, "goalkeeper", primary_attributes=["Agi", "Ref"], 
        secondary_attributes=["1v1", "Ant", "Cmd", "Cnt", "Kic", "Pos"], 
        tertiary_attributes=["Acc", "Aer", "Cmp", "Dec", "Fir", "Han", "Pas", "Thr", "Vis"])
    # TODO: Add roles.
    print(player_df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filepath", type=str)
    args = parser.parse_args()
    filepath = args.filepath

    player_df = load_data(filepath)
    calc_player_scores(player_df)
