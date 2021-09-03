import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

with open(r'data/csgo_gamedata.html', encoding='utf-8') as file:
    html = file.read()

soup = BeautifulSoup(html, 'html.parser')

first_game_table = soup.find_all('table', {'class': 'csgo_scoreboard_inner_right'})[1]
first_info_table = soup.find_all('table', {'class': 'csgo_scoreboard_inner_left'})[0]
first_game_df = pd.read_html(str(first_game_table))[0]
first_info_df = pd.read_html(str(first_info_table))[0]
master_game_df = pd.DataFrame()

line = {}
name = 'TIER 5 POKIMANE SUB'
team_a = first_game_df.iloc[:5, :]
team_b = first_game_df.iloc[6:, :]
team_a_score = int(first_game_df.loc[5, 'Player Name'].replace(' ', '').split(':')[0])
team_b_score = int(first_game_df.loc[5, 'Player Name'].replace(' ', '').split(':')[1])
team_a_roster = team_a['Player Name'].tolist()
team_b_roster = team_b['Player Name'].tolist()

game_id_list = first_info_df.loc[1, 0].replace(':', '').replace('-', '').split()
game_id = str(game_id_list[0]) + str(game_id_list[1])


def outcome(name=name, team_a_roster=team_a_roster, team_b_roster=team_b_roster, team_a_score=team_a_score,
            team_b_score=team_b_score):
    status = None
    if name in team_a_roster and (team_a_score > team_b_score):
        status = 'Win'
    elif name in team_b_roster and (team_b_score > team_a_score):
        status = 'Win'
    else:
        status = 'Loss'
    return status


first_game_df = first_game_df.drop(5)
first_game_df['★'] = first_game_df['★'].replace(np.nan, 0)

star_list = list(first_game_df['★'])
for i in range(len(star_list)):
    current_val = str(star_list[i])
    if '★' in current_val:
        star_count = list(current_val)
        if len(star_count) == 1:
            star_list[i] = 1
        else:
            star_list[i] = int(star_count[-1])

first_game_df['★'] = star_list

dtypes = {'Ping': int, 'K': int, 'A': int, 'D': int, '★': int, 'Score': int}
first_game_df = first_game_df.astype(dtypes)

totals = []
for col in first_game_df.columns:
    if first_game_df[col].dtype == object:
        del first_game_df[col]

grand_totals = [first_game_df['Ping'].mean(), first_game_df['K'].sum(), first_game_df['A'].sum(),
                first_game_df['D'].sum(),
                first_game_df['★'].sum(), first_game_df['Score'].sum()]

team_a_totals = [first_game_df.iloc[:5, :]['A'].sum(), first_game_df.iloc[:5, :]['D'].sum(),
                 first_game_df.iloc[:5, :]['★'].sum(), first_game_df.iloc[:5, :]['Score'].sum()]

team_b_totals = [first_game_df.iloc[5:, :]['K'].sum(),
                 first_game_df.iloc[5:, :]['A'].sum(), first_game_df.iloc[5:, :]['D'].sum(),
                 first_game_df.iloc[5:, :]['★'].sum(), first_game_df.iloc[5:, :]['Score'].sum()]

line['Date'] = first_info_df.loc[1, 0].split(' ')[0]
line['Game ID'] = game_id
line['Map'] = first_info_df.loc[0, 0][len('Competitive '):]
line['Duration'] = int(first_info_df.loc[4, 0].split(':', 1)[1].split(':')[0]) * 60 + int(
    first_info_df.loc[4, 0].split(':', 1)[1].split(':')[1])
line['On Team'] = 'B'
if name in team_a_roster:
    line['On Team'] = 'A'
line['Outcome'] = outcome()
line['Team A Points'] = team_a_score
line['Team A Mean Ping'] = first_game_df.iloc[:5, :]['Ping'].mean()
line['Team A Total Kills'] = first_game_df.iloc[:5, :]['K'].sum()
line['Team A Mean Kills'] = first_game_df.iloc[:5, :]['K'].mean()
line['Team A Total Assists'] = first_game_df.iloc[:5, :]['A'].sum()
line['Team A Mean Assists'] = first_game_df.iloc[:5, :]['A'].mean()
line['Team A Total Deaths'] = first_game_df.iloc[:5, :]['D'].sum()
line['Team A Mean Deaths'] = first_game_df.iloc[:5, :]['D'].mean()
line['Team A Total MVP'] = first_game_df.iloc[:5, :]['★'].sum()
line['Team A Mean MVP'] = first_game_df.iloc[:5, :]['★'].mean()
line['Team A Total Score'] = first_game_df.iloc[:5, :]['Score'].sum()
line['Team A Mean Score'] = first_game_df.iloc[:5, :]['Score'].mean()

line['Team B Points'] = team_b_score
line['Team B Mean Ping'] = first_game_df.iloc[5:, :]['Ping'].mean()
line['Team B Total Kills'] = first_game_df.iloc[5:, :]['K'].sum()
line['Team B Mean Kills'] = first_game_df.iloc[5:, :]['K'].mean()
line['Team B Total Assists'] = first_game_df.iloc[5:, :]['A'].sum()
line['Team B Mean Assists'] = first_game_df.iloc[5:, :]['A'].mean()
line['Team B Total Deaths'] = first_game_df.iloc[5:, :]['D'].sum()
line['Team B Mean Deaths'] = first_game_df.iloc[5:, :]['D'].mean()
line['Team B Total MVP'] = first_game_df.iloc[5:, :]['★'].sum()
line['Team B Mean MVP'] = first_game_df.iloc[5:, :]['★'].mean()
line['Team B Total Score'] = first_game_df.iloc[5:, :]['Score'].sum()
line['Team B Mean Score'] = first_game_df.iloc[5:, :]['Score'].mean()

columns = list(line.keys())

master_game_df = master_game_df.append(line, ignore_index=True)
master_game_df = master_game_df[columns]

skip = 1
for game_table, info_table in zip(soup.find_all('table', {'class': 'csgo_scoreboard_inner_right'}),
                                  soup.find_all('table', {'class': 'csgo_scoreboard_inner_left'})):
    if skip == 1:
        skip += 1
        continue

    temp_game_df = pd.read_html(str(game_table))[0]
    temp_info_df = pd.read_html(str(info_table))[0]

    line = {}
    name = 'TIER 5 POKIMANE SUB'
    team_a = temp_game_df.iloc[:5, :]
    team_b = temp_game_df.iloc[6:, :]
    team_a_score = int(temp_game_df.loc[5, 'Player Name'].replace(' ', '').split(':')[0])
    team_b_score = int(temp_game_df.loc[5, 'Player Name'].replace(' ', '').split(':')[1])
    team_a_roster = team_a['Player Name'].tolist()
    team_b_roster = team_b['Player Name'].tolist()

    game_id_list = temp_info_df.loc[1, 0].replace(':', '').replace('-', '').split()
    game_id = str(game_id_list[0]) + str(game_id_list[1])


    def outcome(name=name, team_a_roster=team_a_roster, team_b_roster=team_b_roster, team_a_score=team_a_score,
                team_b_score=team_b_score):
        status = None
        if name in team_a_roster and (team_a_score > team_b_score):
            status = 'Win'
        elif name in team_b_roster and (team_b_score > team_a_score):
            status = 'Win'
        else:
            status = 'Loss'
        return status


    temp_game_df = temp_game_df.drop(5)
    temp_game_df['★'] = temp_game_df['★'].replace(np.nan, 0)

    star_list = list(temp_game_df['★'])
    for i in range(len(star_list)):
        current_val = str(star_list[i])
        if '★' in current_val:
            star_count = list(current_val)
            if len(star_count) == 1:
                star_list[i] = 1
            else:
                star_list[i] = int(star_count[-1])

    temp_game_df['★'] = star_list

    dtypes = {'Ping': int, 'K': int, 'A': int, 'D': int, '★': int, 'Score': int}
    temp_game_df = temp_game_df.astype(dtypes)

    totals = []
    for col in temp_game_df.columns:
        if temp_game_df[col].dtype == object:
            del temp_game_df[col]
            # pass

    grand_totals = [temp_game_df['Ping'].mean(), temp_game_df['K'].sum(), temp_game_df['A'].sum(),
                    temp_game_df['D'].sum(),
                    temp_game_df['★'].sum(), temp_game_df['Score'].sum()]

    team_a_totals = [temp_game_df.iloc[:5, :]['A'].sum(), temp_game_df.iloc[:5, :]['D'].sum(),
                     temp_game_df.iloc[:5, :]['★'].sum(), temp_game_df.iloc[:5, :]['Score'].sum()]

    team_b_totals = [temp_game_df.iloc[5:, :]['K'].sum(),
                     temp_game_df.iloc[5:, :]['A'].sum(), temp_game_df.iloc[5:, :]['D'].sum(),
                     temp_game_df.iloc[5:, :]['★'].sum(), temp_game_df.iloc[5:, :]['Score'].sum()]

    line['Date'] = temp_info_df.loc[1, 0].split(' ')[0]
    line['Game ID'] = game_id
    line['Map'] = temp_info_df.loc[0, 0][len('Competitive '):]
    line['Duration'] = int(temp_info_df.loc[4, 0].split(':', 1)[1].split(':')[0]) * 60 + int(
        temp_info_df.loc[4, 0].split(':', 1)[1].split(':')[1])
    line['On Team'] = 'B'
    if name in team_a_roster:
        line['On Team'] = 'A'
    line['Outcome'] = outcome()
    line['Team A Points'] = team_a_score
    line['Team A Mean Ping'] = temp_game_df.iloc[:5, :]['Ping'].mean()
    line['Team A Total Kills'] = temp_game_df.iloc[:5, :]['K'].sum()
    line['Team A Mean Kills'] = temp_game_df.iloc[:5, :]['K'].mean()
    line['Team A Total Assists'] = temp_game_df.iloc[:5, :]['A'].sum()
    line['Team A Mean Assists'] = temp_game_df.iloc[:5, :]['A'].mean()
    line['Team A Total Deaths'] = temp_game_df.iloc[:5, :]['D'].sum()
    line['Team A Mean Deaths'] = temp_game_df.iloc[:5, :]['D'].mean()
    line['Team A Total MVP'] = temp_game_df.iloc[:5, :]['★'].sum()
    line['Team A Mean MVP'] = temp_game_df.iloc[:5, :]['★'].mean()
    line['Team A Total Score'] = temp_game_df.iloc[:5, :]['Score'].sum()
    line['Team A Mean Score'] = temp_game_df.iloc[:5, :]['Score'].mean()

    line['Team B Points'] = team_b_score
    line['Team B Mean Ping'] = temp_game_df.iloc[5:, :]['Ping'].mean()
    line['Team B Total Kills'] = temp_game_df.iloc[5:, :]['K'].sum()
    line['Team B Mean Kills'] = temp_game_df.iloc[5:, :]['K'].mean()
    line['Team B Total Assists'] = temp_game_df.iloc[5:, :]['A'].sum()
    line['Team B Mean Assists'] = temp_game_df.iloc[5:, :]['A'].mean()
    line['Team B Total Deaths'] = temp_game_df.iloc[5:, :]['D'].sum()
    line['Team B Mean Deaths'] = temp_game_df.iloc[5:, :]['D'].mean()
    line['Team B Total MVP'] = temp_game_df.iloc[5:, :]['★'].sum()
    line['Team B Mean MVP'] = temp_game_df.iloc[5:, :]['★'].mean()
    line['Team B Total Score'] = temp_game_df.iloc[5:, :]['Score'].sum()
    line['Team B Mean Score'] = temp_game_df.iloc[5:, :]['Score'].mean()

    print(line)

    master_game_df = master_game_df.append(line, ignore_index=True)

master_game_df['Duration'] = master_game_df['Duration'].astype(int)
master_game_df['Game ID'] = master_game_df['Game ID'].astype(np.int64) // (10 * 10^2000)
columns = list(line.keys())
master_game_df = master_game_df[columns]
master_game_df.to_csv('data/GameStats.csv', index=False)
