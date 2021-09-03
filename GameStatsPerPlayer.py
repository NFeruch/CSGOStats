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

name = 'TIER 5 POKIMANE SUB'
team_a = first_game_df
team_b = first_game_df.iloc[6:, :]
team_a_score = int(first_game_df.loc[5, 'Player Name'].replace(' ', '').split(':')[0])
team_b_score = int(first_game_df.loc[5, 'Player Name'].replace(' ', '').split(':')[1])
team_a_roster = team_a['Player Name'].tolist()
team_b_roster = team_b['Player Name'].tolist()

print(first_info_df)

game_id_list = first_info_df.loc[1, 0].replace(':', '').replace('-', '').split()
first_game_df['Game ID'] = str(game_id_list[0]) + str(game_id_list[1])

move = first_game_df['Game ID']
del first_game_df['Game ID']
first_game_df.insert(0, 'Game ID', move)


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
first_game_df['KDR'] = first_game_df['K'].astype(float) / first_game_df['D'].astype(float)
first_game_df['KDR'] = first_game_df['KDR'].apply(lambda x: '%.2f' % (float(x)))
first_game_df['KDAR'] = (first_game_df['K'].astype(float) + first_game_df['A'].astype(float)) / first_game_df[
    'D'].astype(float)
first_game_df['KDAR'] = first_game_df['KDAR'].apply(lambda x: '%.2f' % (float(x)))
first_game_df['★'] = first_game_df['★'].replace(np.nan, 0)
first_game_df['HSP'] = first_game_df['HSP'].apply(lambda x: '%.0f' % float(str(x)[:2]))
first_game_df.insert(1, 'Team', ['A' for i in range(5)] + ['B' for i in range(5)])
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
dtypes = {'Ping': int, 'K': int, 'A': int, 'D': int, '★': int, 'HSP': float, 'Score': int, 'KDR': float, 'KDAR': float}
first_game_df = first_game_df.astype(dtypes)

first_game_df['KP'] = 0
first_game_df['KP'].iloc[:5] = (first_game_df['K'].iloc[:5] + first_game_df['A'].iloc[:5]) / \
                               first_game_df.groupby('Team').sum().loc['A', 'K']
first_game_df['KP'].iloc[5:] = (first_game_df['K'].iloc[5:] + first_game_df['A'].iloc[5:]) / \
                               first_game_df.groupby('Team').sum().loc['B', 'K']
first_game_df['KP'] = first_game_df['KP'].apply(lambda x: '%.2f' % (x * 100))

# grand_totals = [np.nan, np.nan, np.nan, first_game_df['K'].sum(), first_game_df['A'].sum(), first_game_df['D'].sum(),
#                 first_game_df['★'].sum(), np.nan, first_game_df['Score'].sum(), np.nan, np.nan]
# team_a_totals = [np.nan, np.nan, np.nan, first_game_df.iloc[:5, :]['K'].sum(), first_game_df.iloc[:5, :]['A'].sum(), first_game_df.iloc[:5, :]['D'].sum(),
#                 first_game_df.iloc[:5, :]['★'].sum(), np.nan, first_game_df.iloc[:5, :]['Score'].sum(), np.nan, np.nan]
# team_b_totals = [np.nan, np.nan, np.nan, first_game_df.iloc[5:, :]['K'].sum(), first_game_df.iloc[5:, :]['A'].sum(), first_game_df.iloc[5:, :]['D'].sum(),
#                 first_game_df.iloc[5:, :]['★'].sum(), np.nan, first_game_df.iloc[5:, :]['Score'].sum(), np.nan, np.nan]
#
# row_map = {}
# for total, col in zip(grand_totals, first_game_df.columns):
#     row_map[col] = total
# grand_totals_row = pd.DataFrame(row_map, index=[0])
#
# row_map = {}
# for total, col in zip(team_a_totals, first_game_df.columns):
#     row_map[col] = total
# team_a_totals_row = pd.DataFrame(row_map, index=[0])
#
# row_map = {}
# for total, col in zip(team_b_totals, first_game_df.columns):
#     row_map[col] = total
# team_b_totals_row = pd.DataFrame(row_map, index=[0])
#
# first_game_df = pd.concat([first_game_df.iloc[:5, :], team_a_totals_row, first_game_df.iloc[5:, :], team_b_totals_row, grand_totals_row])

# first_game_df['Outcome'] = 'Loss'
# if outcome() == 'Win':
#     first_game_df['Outcome'] = 'Win'

main_game_df = first_game_df.copy()

skip = 1
for game_table, info_table in zip(soup.find_all('table', {'class': 'csgo_scoreboard_inner_right'}),
                                  soup.find_all('table', {'class': 'csgo_scoreboard_inner_left'})):
    if skip == 1:
        skip += 1
        continue

    temp_info_df = pd.read_html(str(info_table))[0]
    temp_game_df = pd.read_html(str(game_table))[0]

    name = 'TIER 5 POKIMANE SUB'
    team_a = temp_game_df.iloc[:5, :]
    team_b = temp_game_df.iloc[6:, :]
    team_a_score = int(temp_game_df.loc[5, 'Player Name'].replace(' ', '').split(':')[0])
    team_b_score = int(temp_game_df.loc[5, 'Player Name'].replace(' ', '').split(':')[1])
    team_a_roster = team_a['Player Name'].tolist()
    team_b_roster = team_b['Player Name'].tolist()

    game_id_list = temp_info_df.loc[1, 0].replace(':', '').replace('-', '').split()
    temp_game_df['Game ID'] = str(game_id_list[0]) + str(game_id_list[1])

    move = temp_game_df['Game ID']
    del temp_game_df['Game ID']
    temp_game_df.insert(0, 'Game ID', move.astype(np.int64))


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
    temp_game_df['KDR'] = temp_game_df['K'].astype(float) / temp_game_df['D'].astype(float)
    temp_game_df['KDR'] = temp_game_df['KDR'].apply(lambda x: '%.2f' % (float(x)))
    temp_game_df['KDAR'] = (temp_game_df['K'].astype(float) + temp_game_df['A'].astype(float)) / temp_game_df[
        'D'].astype(float)
    temp_game_df['KDAR'] = temp_game_df['KDAR'].apply(lambda x: '%.2f' % (float(x)))
    temp_game_df['★'] = temp_game_df['★'].replace(np.nan, 0)
    temp_game_df['HSP'] = temp_game_df['HSP'].apply(
        lambda x: '%.0f' % float(str(x)[:len(x) - 1]) if x is not np.nan else x)
    temp_game_df.insert(1, 'Team', ['A' for i in range(5)] + ['B' for i in range(5)])
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
    dtypes = {'Ping': int, 'K': int, 'A': int, 'D': int, '★': int, 'HSP': float, 'Score': int, 'KDR': float,
              'KDAR': float}
    temp_game_df = temp_game_df.astype(dtypes)

    temp_game_df['KP'] = 0
    temp_game_df['KP'].iloc[:5] = (temp_game_df['K'].iloc[:5] + temp_game_df['A'].iloc[:5]) / \
                                  temp_game_df.groupby('Team').sum().loc['A', 'K']
    temp_game_df['KP'].iloc[5:] = (temp_game_df['K'].iloc[5:] + temp_game_df['A'].iloc[5:]) / \
                                  temp_game_df.groupby('Team').sum().loc['B', 'K']
    temp_game_df['KP'] = temp_game_df['KP'].apply(lambda x: '%.2f' % (x * 100))

    main_game_df = main_game_df.append(temp_game_df)

main_game_df = main_game_df.reset_index(drop=True).rename(columns={'★': 'Star'})
main_game_df['Game ID'] = (main_game_df['Game ID'].astype(np.int64) // (10 * 10 ^ 2000)).astype(np.int64)

print(main_game_df.to_string())
main_game_df.to_csv('data/PlayerStats.csv', index=False)
print(main_game_df.groupby('Game ID')['Team'].count().sort_values())
# print(main_game_df[main_game_df['Player Name'] == 'TIER 5 POKIMANE SUB'].sort_values('K'))
