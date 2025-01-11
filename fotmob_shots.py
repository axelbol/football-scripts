import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch

def fetch_match_data(url):
    """Fetch and parse match data from FotMob."""
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')
    json_data = json.loads(soup.find('script', attrs={'id': '__NEXT_DATA__'}).contents[0])
    return json_data

def process_shots_data(json_fotmob):
    """Extract shot data and team information."""
    df_shots = pd.DataFrame(json_fotmob['props']['pageProps']['content']['shotmap']['shots'])
    df_shots['expectedGoals'] = df_shots['expectedGoals'].fillna(df_shots['expectedGoals'].median())
    local_team_id = json_fotmob['props']['pageProps']['general']['homeTeam']['id']
    leagueName = json_fotmob['props']['pageProps']['general']['leagueName']
    leagueRound = json_fotmob['props']['pageProps']['general']['leagueRoundName']
    local_team_name = json_fotmob['props']['pageProps']['header']['teams'][0]['name']
    away_team_name = json_fotmob['props']['pageProps']['header']['teams'][1]['name']
    local_team_score = json_fotmob['props']['pageProps']['header']['teams'][0]['score']
    away_team_score = json_fotmob['props']['pageProps']['header']['teams'][1]['score']

    return df_shots, local_team_name, away_team_name, local_team_score, away_team_score, leagueName, leagueRound, local_team_id

def plot_shots(df_shots, local_team_name, away_team_name, local_team_score, away_team_score, league_title, local_team_id):
    """Plot the shots on a soccer pitch."""
    plot_title = f"{local_team_name} {local_team_score}-{away_team_score} {away_team_name}"
    shots_local_name = f"{local_team_name.upper()} SHOTS"
    shots_away_name = f"{away_team_name.upper()} SHOTS"

    fig, ax = plt.subplots(figsize=(16, 12))
    pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68, line_color='black', linewidth=1, pitch_color='white', label=False)
    pitch.draw(ax=ax)

    # Plot shots for both teams
    for x in df_shots.to_dict(orient='records'):
        if x['teamId'] == local_team_id:
            # We want to plot the local team on left side of the pitch
            # So we need to mirror both the x and y coordinates
            c_color = (
            'green' if x['eventType'] == 'Goal' and str(x['isOwnGoal']) == 'False'
            else 'red' if x['eventType'] == 'Goal' and str(x['isOwnGoal']) == 'True'
            else 'white'
            ),
            ec_edge_colors = (
                'green' if x['eventType'] == 'Goal' and str(x['isOwnGoal']) == 'False'
                else 'red' if x['eventType'] == 'Goal' and str(x['isOwnGoal']) == 'True'
                else 'purple'
            ),
            m_marker = (
                '*' if x['situation'] == 'Penalty' and x['eventType'] == 'Goal'
                else 'o'
            )
            pitch.scatter(
                x=105-x['x'],
                y=68-x['y'],
                ax=ax,
                s=500*x['expectedGoals'],
                ec=ec_edge_colors,
                c=c_color,
                marker=m_marker,
                # alpha=1 if x['eventType'] == 'Goal' else 0.5,
                zorder=2 if x['eventType'] == 'Goal' else 1
            )
        # right side
        else:
            c_color = (
            'green' if x['eventType'] == 'Goal' and str(x['isOwnGoal']) == 'False'
            else 'red' if x['eventType'] == 'Goal' and str(x['isOwnGoal']) == 'True'
            else 'white'
            ),
            ec_edge_colors = (
                'green' if x['eventType'] == 'Goal' and str(x['isOwnGoal']) == 'False'
                else 'red' if x['eventType'] == 'Goal' and str(x['isOwnGoal']) == 'True'
                else 'purple'
            ),
            m_marker = (
                '*' if x['situation'] == 'Penalty' and x['eventType'] == 'Goal'
                else 'o'
            )
            pitch.scatter(
                x=x['x'],
                y=x['y'],
                ax=ax,
                s=500*x['expectedGoals'],
                ec=ec_edge_colors,
                c=c_color,
                marker=m_marker,
                # alpha=1 if x['eventType'] == 'Goal' else .5,
                zorder=2 if x['eventType'] == 'Goal' else 1
            )

    # Add plot titles
    ax.text(-2, 73, plot_title, ha='left', fontsize=28, fontfamily='serif', fontweight=600, color='black')
    ax.text(-2, 70, league_title, ha='left', fontsize=18, fontfamily='serif', fontweight=100)

    # Add team shot labels
    ax.text(2, 2, shots_local_name, ha='left', fontsize=20, fontweight=500, color='#abb2b9')
    ax.text(103, 2, shots_away_name, ha='right', fontsize=20, fontweight=500, color='#abb2b9')

    # Add legend for shot sizes
    pitch.scatter(49.5, 3, s=500 * 0.05, ec='black', c='white', ax=ax)
    pitch.scatter(52.5, 3, s=500 * 0.15, ec='black', c='white', ax=ax)
    pitch.scatter(55.5, 3, s=500 * 0.3, ec='black', c='white', ax=ax)
    ax.text(52.5, 5, 'Size represents xG', ha='center', fontsize=8, fontfamily='monospace')

    # Add shot types
    # ISOWNGOAL
    if 'True' in str(df_shots['isOwnGoal'].values):
        pitch.scatter(29.3, -2, s=500*.2, ec='red', c='red', ax=ax)
        ax.text(33, -2.4, 'Own Goal', ha='center', fontsize=8, fontfamily='monospace')
    # SHOT
    pitch.scatter(37.2, -2, s=500 * 0.2, ec='purple', c='white', ax=ax)
    ax.text(39.5, -2.4, 'Shot', ha='center', fontsize=8, fontfamily='monospace')
    # GOAL
    pitch.scatter(42.5, -2, s=500 * 0.2, ec='green', c='green', ax=ax)
    ax.text(44.8, -2.4, 'Goal', ha='center', fontsize=8, fontfamily='monospace')
    # PENALTY
    if 'Penalty' in df_shots['situation'].values and 'Goal' in df_shots['eventType'].values:
        pitch.scatter(47.4, -2, s=500*.2, ec='green', c='green', marker='*', ax=ax)
        ax.text(50.5, -2.4, 'Penalty', ha='center', fontsize=8, fontfamily='monospace')

    # Add info and save the plot
    ax.text(60, -2, 'Data via Opta | @axel_bol', ha='left', fontsize=8, fontfamily='monospace')
    plt.savefig('/home/axel/Code/images/image_script.png', dpi=fig.dpi, bbox_inches='tight', pad_inches=0.35)

    # plt.show()

def main():
    url_input = input('Enter URL match: ')
    json_fotmob = fetch_match_data(url_input)

    # Extract relevant data
    df_shots, local_team_name, away_team_name, local_team_score, away_team_score, leagueName, leagueRound, local_team_id = process_shots_data(json_fotmob)
    league_title = leagueName + ' | ' + leagueRound

    # Plot the data
    plot_shots(df_shots, local_team_name, away_team_name, local_team_score, away_team_score, league_title, local_team_id)

    print('Done!')

if __name__ == '__main__':
    main()
