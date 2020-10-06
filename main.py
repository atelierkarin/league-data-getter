from reader.hfl_league_html_reader import HflLeagueHtmlReader

reader = HflLeagueHtmlReader(1705)
reader.do()

print(reader.home_team_full_list)
print(reader.away_team_full_list)