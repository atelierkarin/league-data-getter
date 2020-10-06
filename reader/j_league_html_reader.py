import pandas as pd

class JLeagueHtmlReader:

  def __init__(self, match_id):
    self.match_id = match_id
    self.home_team = None
    self.away_team = None
    self.home_goal = 0
    self.away_goal = 0
    self.home_team_full_list = None
    self.away_team_full_list = None

  def get_goal_list(self, goal_info):
      goals = []
      for column_name, item in goal_info.iterrows():
          if item[0][0].isdigit():
            player_name = item[1].replace('\u3000', ' ')
            goals.append(player_name)
          elif item[1][0].isdigit():
            player_name = item[0].replace('\u3000', ' ')
            goals.append(player_name)
      return goals

  def get_team_appearance(self, lineup_info, change_info, sub_info, goal_list):
      appearance = {}

      sub_list = []
      for column_name, item in change_info.iterrows():
          if item[1] == '▲':
            sub_list.append(item[2].replace('\u3000', ' '))

      for column_name, item in lineup_info.iterrows():
          player_name = item[2].replace('\u3000', ' ')
          appearance[int(item[1])] = [player_name, goal_list.count(player_name)]
      for column_name, item in sub_info.iterrows():
          player_name = item[2].replace('\u3000', ' ')
          if player_name in sub_list:
              appearance[int(item[1])] = [player_name, goal_list.count(player_name)]
      return appearance

  def do(self):
    url = "https://data.j-league.or.jp/SFMS02/?match_card_id={}".format(self.match_id)

    dfs = pd.read_html(url)

    # チームのテータ
    team_info = dfs[0]
    self.home_team = team_info[0][0]
    self.away_team = team_info[4][0]
    self.home_goal = int(team_info[1][0])
    self.away_goal = int(team_info[3][0])

    counter = 0
    data_list_counter = 0
    data_list = []
    if self.home_goal > 0:
        data_list.append("HG")
    if self.away_goal > 0:
        data_list.append("AG")
    data_list.append("HT")
    data_list.append("AT")
    data_list.append("HS")
    data_list.append("AS")
    data_list.append("HC")
    data_list.append("AC")

    home_team_goal_info = pd.DataFrame()
    away_team_goal_info = pd.DataFrame()

    home_team_player_info = pd.DataFrame()
    away_team_player_info = pd.DataFrame()

    home_team_sub_info = pd.DataFrame()
    away_team_sub_info = pd.DataFrame()

    home_team_change_info = pd.DataFrame()
    away_team_change_info = pd.DataFrame()

    for df in dfs:
      if counter >= 2 and data_list_counter < len(data_list):
        if (data_list[data_list_counter] == "HG" or data_list[data_list_counter] == "AG") and len(df.columns) == 2:
          if data_list[data_list_counter] == "HG":
            home_team_goal_info = df.copy()
          else:
            away_team_goal_info = df.copy()
          data_list_counter += 1
        elif (data_list[data_list_counter] == "HT" or data_list[data_list_counter] == "AT") and df.shape[0] == 11:
          if data_list[data_list_counter] == "HT":
            # ホームチームスタメン
            home_team_player_info = df.copy()
          elif data_list[data_list_counter] == "AT":
            # アウェイチームスタメン
            away_team_player_info = df.copy()
          data_list_counter += 1
        elif (data_list[data_list_counter] == "HS" or data_list[data_list_counter] == "AS" or data_list[data_list_counter] == "HC" or data_list[data_list_counter] == "AC") and len(df.columns) == 4:
          if data_list[data_list_counter] == "HS":
            home_team_sub_info = df.copy()
          elif data_list[data_list_counter] == "AS":
            away_team_sub_info = df.copy()
          elif data_list[data_list_counter] == "HC":
            home_team_change_info = df.copy()
          else:
            away_team_change_info = df.copy()
          data_list_counter += 1

      counter += 1

    home_team_goals = self.get_goal_list(home_team_goal_info)
    away_team_goals = self.get_goal_list(away_team_goal_info)
    self.home_team_full_list = self.get_team_appearance(
        home_team_player_info, home_team_change_info, home_team_sub_info, home_team_goals)
    self.away_team_full_list = self.get_team_appearance(
        away_team_player_info, away_team_change_info, away_team_sub_info, away_team_goals)
