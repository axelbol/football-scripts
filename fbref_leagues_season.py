import os
import pandas as pd
import bs4
import requests
from io import StringIO


def fetch_webpage_content(url):
    """
    Fetch the content of a webpage.

    Args:
        url (str): The URL of the webpage.

    Returns:
        bs4.BeautifulSoup: Parsed HTML content of the webpage.
    """
    try:
        response = requests.get(url)
        # check whether the HTTP request was successful.
        response.raise_for_status()
        return bs4.BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None


def extract_commented_table(soup):
    """
    Extract the first commented-out table from the webpage.

    Args:
        soup (bs4.BeautifulSoup): Parsed HTML content of the webpage.

    Returns:
        pd.DataFrame: DataFrame containing the extracted table.
    """
    comments = soup.find_all(string=lambda text: isinstance(text, bs4.Comment))
    commented_out_tables = [
        bs4.BeautifulSoup(cmt, 'html.parser').find_all('table') for cmt in comments
    ]

    # Filter to keep only single tables
    commented_out_tables = [tab[0] for tab in commented_out_tables if len(tab) == 1]

    if not commented_out_tables:
        raise ValueError("No commented-out tables found.")

    return pd.read_html(StringIO(str(commented_out_tables[0])))[0]


def clean_and_process_table(df, country):
    """
    Clean and process the extracted table.

    Args:
        df (pd.DataFrame): Raw DataFrame extracted from the table.

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    # Join multi-level columns
    df.columns = ['_'.join(col).strip() for col in df.columns.values]

    # Drop unnecessary columns
    columns_to_drop = ['Unnamed: 0_level_0_Rk', 'Unnamed: 24_level_0_Matches']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    # Rename columns
    df.columns = [
        'player', 'nation', 'pos', 'squad', 'age', 'born', 'mp', 'starts', 'min', '90s', 'goals', 'ast', 'g+a', 'g-pk', 'pk', 'pkatt', 'crdy', 'crdr', 'per_gls', 'per_ast', 'per_g+a', 'per_g-pk', 'per_g+a-pk'
    ]

    # Remove header rows from the data
    df = df[df['player'] != 'Player']

    # Add the 'country' column
    df['country'] = country

    return df


def save_to_csv(df, file_path):
    """
    Save the DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to save.
        file_path (str): Path to the output CSV file.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)
        print(f"File saved to {file_path}")
    except Exception as e:
        print(f"Error saving the file: {e}")


def main():
    """
    Main function to execute the script.
    """
    url = input("Enter the URL of the webpage: ").strip()

    # code for file output written
    # output_file = '/home/axel/Code/Python/axel/football_analysis/csv/liga_par_script.csv'

    # code to enter the name of the file
    file_name = input("Enter the output file name (without extension): ").strip()
    file_name = f"{file_name}.csv"
    # Set the directory for saving the file
    output_directory = '/home/axel/Code/Python/axel/football_analysis/csv/'
    output_file = os.path.join(output_directory, file_name)

    # Prompt for country name
    country = input("Enter the country name to add to the 'country' column: ").strip()

    soup = fetch_webpage_content(url)
    if not soup:
        return

    try:
        df = extract_commented_table(soup)
        df_cleaned = clean_and_process_table(df, country)
        save_to_csv(df_cleaned, output_file)
    except ValueError as e:
        print(f"Error processing the table: {e}")


if __name__ == "__main__":
    main()
