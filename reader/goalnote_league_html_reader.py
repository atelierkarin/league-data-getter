import pandas as pd


class GoalnoteLeagueHtmlReader:

    def __init__(self, tid, sid):
        self.tid = tid
        self.sid = sid
        self.home_team = None
        self.away_team = None
        self.home_goal = 0
        self.away_goal = 0
        self.home_team_full_list = None
        self.away_team_full_list = None

    def get_goal_list(self, goal_info):
        goals = []
        for column_name, item in goal_info.iterrows():
            if type(item[0]) == str and item[0].isdigit():
                player_name = item[1].split(' (', 1)[0]
                goals.append({int(item[0]): player_name})
        return goals

    def get_team_appearance(self, lineup_info, subs_info):
        appearance = {}
        for column_name, item in lineup_info.iterrows():
            player_name = item[2].split(' (', 1)[0]
            appearance[int(item[0])] = [player_name, 0]
        for column_name, item in subs_info.iterrows():
            if item[0].isdigit():
                appearance[int(item[3])] = [item[4], 0]
        return appearance

    def get_full_list(self, appearance, goal_list):
        full_list = appearance.copy()
        for g in goal_list:
            for squad_no in g.keys():
                try:
                    full_list[squad_no][1] += 1
                except:
                    print("ERROR WHEN ADDING GOAL DATA ON = {}".format(g))
        return full_list

    def do(self):
        url = "https://www.goalnote.net/detail-schedule-game.php?tid={}&sid={}".format(
            self.tid, self.sid)
        dfs = pd.read_html(url)

        # チームのテータ
        team_info = dfs[0]
        self.home_team = team_info[0][0].split(' KICK OFF', 1)[0]
        self.away_team = team_info[6][0].split(' KICK OFF', 1)[0]
        self.home_goal = int(team_info[1][0])
        self.away_goal = int(team_info[5][0])

        counter = 0
        data_list_counter = 0
        data_list = []
        if self.home_goal > 0:
            data_list.append("HG")
        if self.away_goal > 0:
            data_list.append("AG")
        data_list.append("HT")
        data_list.append("AT")
        data_list.append("HC")
        data_list.append("AC")

        home_team_goal_info = pd.DataFrame()
        away_team_goal_info = pd.DataFrame()
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
                elif (data_list[data_list_counter] == "HT" or data_list[data_list_counter] == "AT") and (len(df.columns) == 3 or len(df.columns) == 4):

                    if len(df.columns) == 3:
                        # 普通のフォーマット
                        if data_list[data_list_counter] == "HT":
                            # ホームチームスタメン
                            home_team_player_info = df.copy()
                        elif data_list[data_list_counter] == "AT":
                            # アウェイチームスタメン
                            away_team_player_info = df.copy()
                        data_list_counter += 1
                    else:
                        # 別のフォーマット
                        if df[2].str.contains("○").any():
                            real_team_info = df.loc[df[2] == "○"][[0, 1, 3]]
                            if data_list[data_list_counter] == "HT":
                                # ホームチームスタメン
                                home_team_player_info = pd.DataFrame(
                                    real_team_info.copy().values)
                            elif data_list[data_list_counter] == "AT":
                                # アウェイチームスタメン
                                away_team_player_info = pd.DataFrame(
                                    real_team_info.copy().values)
                            data_list_counter += 1

                elif (data_list[data_list_counter] == "HC" or data_list[data_list_counter] == "AC") and len(df.columns) == 5:
                    if data_list[data_list_counter] == "HC":
                        # ホームチーム交代
                        home_team_change_info = df.copy()
                    else:
                        # アウェイチーム交代
                        away_team_change_info = df.copy()
                    data_list_counter += 1
            counter += 1

        # ゴールの情報
        home_team_goals = self.get_goal_list(home_team_goal_info)
        away_team_goals = self.get_goal_list(away_team_goal_info)
        home_team_appearance = self.get_team_appearance(
            home_team_player_info, home_team_change_info)
        away_team_appearance = self.get_team_appearance(
            away_team_player_info, away_team_change_info)
        self.home_team_full_list = self.get_full_list(
            home_team_appearance, home_team_goals)
        self.away_team_full_list = self.get_full_list(
            away_team_appearance, away_team_goals)