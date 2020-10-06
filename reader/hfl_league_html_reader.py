import pandas as pd

class HflLeagueHtmlReader:

  def __init__(self, match_id):
    self.match_id = match_id
    self.home_team = None
    self.away_team = None
    self.home_goal = 0
    self.away_goal = 0
    self.home_team_full_list = None
    self.away_team_full_list = None

  def get_goal_list(self, goal_info):
    home_goals = []
    away_goals = []
    for column_name, item in goal_info.iterrows():
      if item[1] == self.home_team:
        player_name = item[10].replace('\u3000', ' ')
        home_goals.append(player_name)
      elif item[1] == self.away_team:
        player_name = item[10].replace('\u3000', ' ')
        away_goals.append(player_name)
    return home_goals, away_goals

  def get_team_appearance(self, lineup_info, goal_list):
    appearance = {}

    for column_name, item in lineup_info.iterrows():
      column_id = int(column_name)
      if (column_id < 11 or (column_id > 11 and str(item[0]).isdigit())):
        player_name = item[2].replace('\u3000', ' ')
        appearance[int(item[1])] = [player_name, goal_list.count(player_name)]
    return appearance

  def do(self):
    url = "https://refolm-hfl.appspot.com/koushiki_kiroku.jsp?gameid={}".format(self.match_id)

    dfs = pd.read_html(url)

    # チームのテータ
    team_info = dfs[2]
    self.home_team = team_info[0][0].replace("Kick off", "").strip()
    self.away_team = team_info[4][0].replace("Kick off", "").strip()
    self.home_goal = int(team_info[1][0])
    self.away_goal = int(team_info[3][0])

    # ゴールデータ
    goal_info = dfs[7]
    goal_info.columns = range(goal_info.shape[1])
    home_team_goals, away_team_goals = self.get_goal_list(goal_info)

    match_info = dfs[3]
    match_info.columns = range(match_info.shape[1])

    home_team_info = match_info[[0, 15, 14]].copy()
    home_team_info.columns = range(home_team_info.shape[1])
    away_team_info = match_info[[33, 18, 19]].copy()
    away_team_info.columns = range(away_team_info.shape[1])

    self.home_team_full_list = self.get_team_appearance(home_team_info, home_team_goals)
    self.away_team_full_list = self.get_team_appearance(away_team_info, away_team_goals)