from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
import time
from tabulate import tabulate
from collections import Counter
import numpy as np

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

#Player information
player_name = "ToD"
player_num = "232792"

URL = "https://w3champions.com/player/{}%{}/matches".format(player_name, player_num)

driver.get(URL)

#Hacky way to wait for the javascript to finish executing
time.sleep(3)


#First page: get the soup
html = driver.page_source
soups=[BeautifulSoup(html, features="lxml")]
next_page=True
#loop through all other pages and get the soup
while next_page:
    time.sleep(3)
    next_button = driver.find_element(by=By.XPATH, value=r'//*[@id="app"]/div/main/div/div/div/div/div/div[4]/div[2]/div[2]/nav/ul/li[7]/button/i')
    try:
        next_button.click()
    except ElementClickInterceptedException:
        break
    time.sleep(1)
    html = driver.page_source
    soups+=[BeautifulSoup(html, features="lxml")]
    next_page = next_button.get_attribute("disabled") == None



def get_table(soup):
    """
    Gets the table of games from the soup of W3C webpage.
    Parses out the specific races and outputs them as a list of lists
    """
    table = soup.find(lambda tag: tag.name=='table') 
    rows = table.findAll(lambda tag: tag.name=='tr')
    text=[]
    races=[]
    for row in rows[1:]:
        text+=[row.text]
        races+=[row.find_all('span', attrs={"class":"race-icon"})]
    
    processed_races=[]
    for game in races:
        game_races=[]
        for player in game:
            game_races+=[str(player).split("race-icon-",1)[1].split(" ",1)[0] ]
        processed_races+=[game_races]
    return text, processed_races
    

#Take only the races we don't care who is playing
matchups = []
matchups+=[get_table(soup)[1] for soup in soups]

#Combine all pages to a single list
flat_matchups = [item for sublist in matchups for item in sublist]
#Only take games which have 8 players (i.e 4v4 games)
v4_matchups = [matchup for matchup in flat_matchups if len(matchup)==8] 

#Save the number of 4v4 matches that ToD has played
num_games = len(v4_matchups)

#ToD's team is always the first 4 players so split the list in half to get the two teams
tod_team = [matchup[:4] for matchup in v4_matchups]
enemy_team = [matchup[4:] for matchup in v4_matchups]

#As we only care about the total number of each race we can combine all the games
flat_tod = [item for sublist in tod_team for item in sublist]
flat_enemy = [item for sublist in enemy_team for item in sublist]

#Count the number of each race on each team
tod_counts = [(x, flat_tod.count(x)) for x in set(flat_tod)]
enemy_counts = [(x, flat_enemy.count(x)) for x in set(flat_enemy)]

  
#Get stats of number of humans on each team
#Not including randoms
tods_humans = np.array([game.count('HUMAN') for game in tod_team])
enemy_humans = np.array([game.count('HUMAN') for game in enemy_team])
tods_human_counts = Counter(tods_humans)
enemy_human_counts = Counter(enemy_humans)

tod_more_humans = sum(tods_humans>enemy_humans)
#Including humans that queued as random
tods_humans_rand = np.array([game.count('HUMAN') + game.count('RANDOM_HUMAN') for game in tod_team])
enemy_humans_rand = np.array([game.count('HUMAN') + game.count('RANDOM_HUMAN') for game in enemy_team])
tods_human_counts_rand = Counter(tods_humans_rand)
enemy_human_counts_rand = Counter(enemy_humans_rand)

tod_more_humans_rand = sum(tods_humans_rand>enemy_humans_rand)

#Print all relative statistics
print("Race distribution over {} games:".format(num_games))
print("ToD's Team: (Including ToD)")
print(tabulate(tod_counts, headers=['Race', 'Number'], tablefmt="github"))
print()
print("Enemy's Team:")
print(tabulate(enemy_counts, headers=['Race', 'Number'], tablefmt="github"))
print()
print("Total number of humans including randoms (including ToD):")
print("ToD's team: {}".format(sum([x[1] for x in tod_counts if x[0] == 'HUMAN' or x[0] == 'RANDOM_HUMAN'])))
print("Enemy's team: {}".format(sum([x[1] for x in enemy_counts if x[0] == 'HUMAN' or x[0] == 'RANDOM_HUMAN'])))
print()
print("Distribution of number of humans not including those who queued as random:")
print("ToD's team:")
print(tabulate(sorted(tods_human_counts.items()), headers=['# HUMANS', 'Number of games'], tablefmt="github"))
print("Enemy's team:")
print(tabulate(sorted(enemy_human_counts.items()), headers=['# HUMANS', 'Number of games'], tablefmt="github"))
print()
print("The number of games where there are more humans on ToD's team was {}".format(tod_more_humans))
print()
print("Distribution of number of humans including those who queued as random:")
print("ToD's team:")
print(tabulate(sorted(tods_human_counts_rand.items()), headers=['# HUMANS', 'Number of games'], tablefmt="github"))
print("Enemy's team:")
print(tabulate(sorted(enemy_human_counts_rand.items()), headers=['# HUMANS', 'Number of games'], tablefmt="github"))
print()
print("The number of games where there are more humans on ToD's team was {}".format(tod_more_humans_rand))

