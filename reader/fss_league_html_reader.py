import pandas as pd
import re
import requests

class FssLeagueHtmlReader:

  def __init__(self, taikai_hold_id, fed_id, game_id):
        self.taikai_hold_id = taikai_hold_id
        self.fed_id = fed_id
        self.game_id = game_id
        self.home_team = None
        self.away_team = None
        self.home_goal = 0
        self.away_goal = 0
        self.home_team_full_list = None
        self.away_team_full_list = None

  def do(self):
        url = "http://football-system.jp/fss/pubGameResultConf.php"
        payload = {
          'taikai_hold_id': self.taikai_hold_id,
          'fed_id': self.fed_id,
          'game_id': self.game_id
        }
        s = requests.Session()
        res = s.post(url, data=payload)
        res.raise_for_status()
        dfs = pd.read_html(res.text)

        team_info = {}

        # Get Tables
        table_team_info = dfs[1]
        table_sub_and_goals_info = dfs[6]
        table_home_members = dfs[11]
        table_away_members = dfs[13]

        # Team Info
        self.home_team = table_team_info[0][0].replace('\u3000', ' ').split('  キックオフ', 1)[0]
        self.away_team = table_team_info[2][0].replace('\u3000', ' ').split('  キックオフ', 1)[0]

        self.home_team_full_list = {}
        self.away_team_full_list = {}

        # Sub and Goal Info
        home_sub_list_raw = table_sub_and_goals_info[0][0]
        away_sub_list_raw = table_sub_and_goals_info[2][0]
        home_sub_list = []
        away_sub_list = []

        home_goal_list_raw = table_sub_and_goals_info[0][2]
        away_goal_list_raw = table_sub_and_goals_info[2][2]
        home_goal_list = []
        away_goal_list = []

        # Check nan
        if not type(home_sub_list_raw) == str: home_sub_list_raw = ''
        if not type(away_sub_list_raw) == str: away_sub_list_raw = ''
        if not type(home_goal_list_raw) == str: home_goal_list_raw = ''
        if not type(away_goal_list_raw) == str: away_goal_list_raw = ''

        # Subs
        home_sub_list_raw = re.split('  ', home_sub_list_raw)
        away_sub_list_raw = re.split('  ', away_sub_list_raw)

        for item in home_sub_list_raw:
          if '[in]' in item:
            home_sub_list.append(item.replace('[in]', '').replace(' ', '').replace('\u3000', ' '))
        for item in away_sub_list_raw:
          if '[in]' in item:
            away_sub_list.append(item.replace('[in]', '').replace(' ', '').replace('\u3000', ' '))

        # Goals
        home_goal_list_raw = re.split('\d+  分  ', home_goal_list_raw.replace('  ＋', ''))
        away_goal_list_raw = re.split('\d+  分  ', away_goal_list_raw.replace('  ＋', ''))
        for item in home_goal_list_raw:
          if len(item) > 0 and not item[0].isdigit():
            home_goal_list.append(item.split('（', 1)[0].replace(' ', '').replace('\u3000', ' '))
        for item in away_goal_list_raw:
          if len(item) > 0 and not item[0].isdigit():
            away_goal_list.append(item.split('（', 1)[0].replace(' ', '').replace('\u3000', ' '))

        # Home Members
        is_sub = False
        for column_name, item in table_home_members.iterrows():
          if item[0] == "SUB":
            is_sub = True
          if len(item) > 7 and type(item[7]) == str and item[7].isdigit():
            player_name = item[6].split('  （', 1)[0].replace(' ', '').replace('[Cap]', '').replace('\u3000', ' ')
            app = 0
            if not is_sub:
              app = 1
            elif player_name in home_sub_list:
              app = 1

            if app == 1:
              self.home_team_full_list[int(item[7])] = [player_name, home_goal_list.count(player_name)]

        # Away Memebers
        is_sub = False
        for column_name, item in table_away_members.iterrows():
          if item[0] == "SUB":
            is_sub = True
          if type(item[1]) == str and item[1].isdigit():
            player_name = item[2].split('  （', 1)[0].replace(' ', '').replace('[Cap]', '').replace('\u3000', ' ')

            app = 0
            if not is_sub:
              app = 1
            elif player_name in away_sub_list:
              app = 1

            if app == 1:
              self.away_team_full_list[int(item[1])] = [player_name, away_goal_list.count(player_name)]