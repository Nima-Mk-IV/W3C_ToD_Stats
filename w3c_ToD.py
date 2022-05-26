from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
import time

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
villian_team = [matchup[4:] for matchup in v4_matchups]

#As we only care about the total number of each race we can combine all the games
flat_tod = [item for sublist in tod_team for item in sublist]
flat_villian = [item for sublist in villian_team for item in sublist]

#Count the number of each race on each team
tod_counts = [(x, flat_tod.count(x)) for x in set(flat_tod)]
villian_counts = [(x, flat_villian.count(x)) for x in set(flat_villian)]

#Print all relative statistics


    
    