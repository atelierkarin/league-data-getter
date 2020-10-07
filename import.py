import requests
import urllib.parse as urlparse
from dateutil.parser import parse
from urllib.parse import parse_qs
from bs4 import BeautifulSoup

def get_url(sourcetype, id, id2=None, id3=None):
  if sourcetype == "goalnote":
    return "https://www.goalnote.net/detail-schedule.php?tid={}".format(id)
  elif sourcetype == "hfl":
    return "https://refolm-hfl.appspot.com/game_schedule.jsp?leagueid={}&zengo={}&year={}".format(id, id2, id3)
  elif sourcetype == "jfl":
    return "http://www.jfl.or.jp/jfl-pc/view/s.php?a={}&f={}_spc.html".format(id, id2)
  return None

def is_date(string):
  try:
    parse(string)
    return True
  except ValueError:
    return False

def read_goalnote_matches(tid):

  url = get_url("goalnote", tid)

  res = requests.get(url)
  soup = BeautifulSoup(res.content, "html.parser")

  content = []

  target_area = soup.find(class_="season-select")
  for tr_element in target_area.find_all("tr"):
    result_date_element = [c for c in tr_element.find_all("td", class_="result-date") if c.text and is_date(c.text)]
    home_team_element = tr_element.find("td", class_="team1")
    away_team_element = tr_element.find("td", class_="team2")
    score_element = tr_element.find("td", class_="score")

    if score_element and len(result_date_element) > 0:
      result_date = result_date_element[0].text
      score_link_element = score_element.find("a")

      if score_link_element:
        score_link = score_link_element.get('href')
        if score_link:
          score_link_parsed = urlparse.urlparse(score_link)
          tid = parse_qs(score_link_parsed.query)['tid'][0]
          sid = parse_qs(score_link_parsed.query)['sid'][0]
          if tid and sid:
            content.append({
              'match_date': result_date,
              'tid': tid,
              'sid': sid,
              'source_type': "goalnote"
            })
  return content

def read_hfl_matches(leagueid, zengo, year):

  url = get_url("hfl", leagueid, zengo, year)

  res = requests.get(url)
  soup = BeautifulSoup(res.content, "html.parser")

  content = []

  target_area = soup.find(id="schedule")
  for tr_element in target_area.find_all("tr"):
    td_elements = tr_element.find_all("td")
    if len(td_elements) > 0:
      match_date = td_elements[0].text
      home_team_element = td_elements[4].text
      away_team_element = td_elements[6].text
      score_element = td_elements[5]

      rubbish_word_index = match_date.index('(')
      match_date = str(year) + '/' + match_date[:rubbish_word_index]

      if score_element:
        score_link_element = score_element.find("a")

        if score_link_element:
          score_link = score_link_element.get('href')
          if score_link:
            score_link_parsed = urlparse.urlparse(score_link)
            gameid = parse_qs(score_link_parsed.query)['gameid'][0]
            if gameid:
              content.append({
                'match_date': match_date,
                'gameid': gameid,
                'source_type': "hfl"
              })
  return content

def read_jfl_matches(a, f, year):

  url = get_url("jfl", a, f)

  res = requests.get(url)
  soup = BeautifulSoup(res.content, "html.parser")

  content = []

  target_areas = soup.find_all(class_='table-schedule')
  for target_area in target_areas:
    for tr_element in target_area.find_all("tr"):
      result_date_element = tr_element.find("td", class_="result-date")
      home_team_element = tr_element.find("td", class_="team1")
      away_team_element = tr_element.find("td", class_="team2")
      score_element = tr_element.find("td", class_="score")

      if result_date_element and score_element:

        match_date = result_date_element.text

        rubbish_word_index = match_date.index('(')
        match_date = str(year) + '/' + match_date[:rubbish_word_index].replace('月', '/').replace('日', '')

        score_link_element = score_element.find("a")

        if score_link_element:
          score_link = score_link_element.get('href')
          if score_link:
            score_link_parsed = urlparse.urlparse(score_link)
            aid = parse_qs(score_link_parsed.query)['a'][0]
            fid = parse_qs(score_link_parsed.query)['f'][0]
            if aid and fid:
              content.append({
                'match_date': match_date,
                'a': aid,
                'f': fid.replace('_spc.html', ''),
                'source_type': "jfl"
              })
  return content

print(read_jfl_matches(1542, '2020A001', 2020))