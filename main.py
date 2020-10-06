from reader.jfl_league_html_reader import JflLeagueHtmlReader

reader = JflLeagueHtmlReader(1576, '2020A0011618')
reader.do()

print(reader.home_team_full_list)
print(reader.away_team_full_list)