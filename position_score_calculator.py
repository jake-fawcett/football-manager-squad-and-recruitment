import argparse

import pandas as pd


def load_xlsx_data_to_dataframe(filepath: str) -> pd.DataFrame:
    """Read XLSX file into a Dataframe.

    Keyword arguments:
    filepath -- path to xlsx file
    """
    df = pd.read_excel(filepath, engine="openpyxl", nrows=12)
    return df


def load_html_data_to_dataframe(filepath: str) -> pd.DataFrame:
    """Read HTML file exported by FM into a Dataframe.

    Keyword arguments:
    filepath -- path to fm player html file
    """
    df = pd.read_html(filepath, header=0, encoding="utf-8", keep_default_na=False)[0]
    # Clean Dataframe to get rid of unknown values and ability ranges (takes the lowest value)
    # This casts to a string to be able to split, so we have to cast back to an int later.
    df = df.replace("-", 0)
    df = df.map(lambda x: str(x).split("-")[0])
    return df


def export_html_from_dataframe(player_df: pd.DataFrame, filepath: str) -> str:
    """Export Dataframe as html with jQuery Data Tables.

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


def calc_role_scores(player_df: pd.DataFrame, attribute_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Player position scores based on selected attribute weightings.

    Keyword arguments:
    player_df: Dataframe of Players and their Attributes
    attribute_df: Dataframe of Attributes and their Weightings
    """
    for _, weightings in attribute_df.iterrows():
        role = weightings["Ratings Weights"]
        player_df[role] = 0
        for attribute in weightings.index[1:]:
            weighting = weightings[attribute]
            try:
                player_df[role] += round(pd.to_numeric(player_df[attribute]) * weighting / 20, 2)
            except Exception as e:  # Used to Nat being used twice (Nationality and Natural Fitness)
                print(e)
                continue
    return player_df


if __name__ == "__main__":
    # Parse Input args
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-filepath", type=str, help="Path to Input Html file")
    parser.add_argument("-o", "--output-filepath", type=str, help="Path to Export resultant Html file")
    parser.add_argument("-a", "--attribute-filepath", type=str, help="Path to Attribute XLSX file", default="./attribute_ratings.xlsx")
    args = parser.parse_args()
    input_filepath = args.input_filepath
    output_filepath = args.output_filepath
    attribute_filepath = args.attribute_filepath

    # Inport data, calculate scores for role,
    attribute_df = load_xlsx_data_to_dataframe(attribute_filepath)
    player_df = load_html_data_to_dataframe(input_filepath)
    player_df = calc_role_scores(player_df, attribute_df)
    # trim attributes from final output
    player_df = player_df.drop(player_df.columns[15:-11], axis=1)
    # export results as html
    export_html_from_dataframe(player_df, output_filepath)
