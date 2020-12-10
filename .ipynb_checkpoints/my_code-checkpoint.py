##### Importing libraries #####
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import sqlite3
from collections import Counter
import sqlite3
import copy
import requests
import bs4


###############################
##### FIFA Data Functions #####
###############################

savedir = 'results'
def save_fig_as_png(figtitle):
    image_path = savedir + '/' + figtitle + '.png'
    plt.gcf().savefig(image_path, bbox_inches= 'tight',\
                      transparent = False, pad_inches = 0)


def import_csv(file_path):
    '''
    Reads csv file into Pandas dataframe
    '''
    return pd.read_csv(file_path)


def single_team(data, team_name):
    '''
    Returns a Pandas dataframe containing players from a single team,
    team name input is a string
    '''
    return data.loc[data['club'] == team_name]
    
    
def top_n_countries(fifa_data, n):
    '''
    Creates a list of tuples of the n top countries with most soccer players
    in the dataset, along with the number of players for each
    '''
    country_list = fifa_data["nationality"].tolist()
    tuple_list = Counter(country_list).most_common(n)
    return tuple_list

def average_age(df):
    '''
    Finds the average age of all players in a certain dataframe
    '''
    return df["age"].mean()


def average_salary(df):
    '''
    Calculates the average salary of all players in a dataframe
    '''
    return df["wage_eur"].mean()

    
def country_histogram(tuple_list):
    '''
    Plots a histogram displaying how many players are from each of the top
    countries for the n countries with most players from top_countries function
    '''
    plt.bar(range(len(tuple_list)), [val[1] for val in tuple_list])
    plt.xticks(range(len(tuple_list)), [val[0] for val in tuple_list])
    plt.xticks(rotation = 90)
    plt.xlabel('Country')
    plt.ylabel('Number of Players')
    plt.suptitle('Number of Players from each Country')

    
def wage_age_scatter(df, plot_title = 'Wage vs. Age'):
    '''
    Plots age vs FIFA salary for each player in a dataframe with a linear
    line of best fit
    '''
    ages = np.asarray(df['age'].tolist())
    wages = np.asarray(df['wage_eur'].tolist())
    plt.scatter(ages, wages)
    plt.xlabel('Age')
    plt.ylabel('Wage (euros)')
    plt.suptitle(plot_title)
    # Line of best fit
    m, b = np.polyfit(ages, wages, 1)
    print('Best fit line: ', 'wage = {} * age + {}'.format(m, b))
    plt.plot(ages, m * ages + b, 'r')
    

def average_ages(fifa_data, teamlist):
    '''
    Returns a list of average age for each team in corresponding index position
    from the team list, also mean and standard deviation of the entire set.
    '''
    average_age_list = []
    for team in teamlist:
        average_age_list.append(average_age(single_team(fifa_data, team)))
    mean = sum(average_age_list) / len(average_age_list)
    stdev = (sum([((x - mean) ** 2) for x in average_age_list]) / len(average_age_list))**0.5
    return average_age_list, mean, stdev

def average_ages_barchart(average_age_list, teamlist):
    '''
    Plots average ages from function above on a bar chart
    '''
    mean = sum(average_age_list) / len(average_age_list)
    plt.bar(range(len(average_age_list)), average_age_list)
    plt.plot(range(len(average_age_list)), [mean] * len(average_age_list), 'r--')
    plt.xticks(range(len(average_age_list)), teamlist)
    plt.xticks(rotation = 90)
    plt.xlabel('Team')
    plt.ylabel('Average Age')
    plt.suptitle('Average Ages of PL Teams')

    
def ranking_v_average_age(average_age_list):
    rankings = range(len(average_age_list),0,-1)
    plt.scatter(average_age_list, rankings)
    plt.xlabel('Average Age')
    plt.ylabel('# Teams - Ranking')
    plt.suptitle('Team Rankings vs. Average Age')
    

def goals_scored_ranking_scatter(df, teamlist, name_id_dict):
    '''
    Takes dataframe of match data, ranked teamlist, and dict of rankings
    to create a scatterplot of goals scored vs. ranking
    '''
    goals_scored = []
    rankings = list(range(1,21))
    for team in teamlist:
        goals_scored.append(scored_and_conceded(df, team, name_id_dict)[0])
    plt.scatter(rankings, goals_scored)
    plt.xlabel('Team Ranking')
    plt.ylabel('Goals Scored')
    plt.suptitle('Goals Scored vs. Team Ranking')
    # Line of best fit
    m, b = np.polyfit(rankings, goals_scored, 1)
    print('Best fit line: ', 'goals = {} * rank + {}'.format(m, b))
    plt.plot(rankings, m * np.asarray(rankings) + b, 'r')


def goals_conceded_ranking_scatter(df, teamlist, name_id_dict):
    '''
    Takes dataframe of match data, ranked teamlist, and dict of rankings
    to create a scatterplot of goals conceded vs. ranking
    '''
    goals_conceded = []
    rankings = list(range(1,21))
    for team in teamlist:
        goals_conceded.append(scored_and_conceded(df, team, name_id_dict)[1])
    plt.scatter(rankings, goals_conceded)
    plt.xlabel('Team Ranking')
    plt.ylabel('Goals Conceded')
    plt.suptitle('Goals Conceded vs. Team Ranking')
    # Line of best fit
    m, b = np.polyfit(rankings, goals_conceded, 1)
    print('Best fit line: ', 'goals = {} * rank + {}'.format(m, b))
    plt.plot(rankings, m * np.asarray(rankings) + b, 'r')

    
def goals_scored_v_conceded(df, teamlist, name_id_dict):
    '''
    Takes dataframe of match data, ranked teamlist, and dict of rankings
    to create a scatterplot of goals scored vs. goals conceded with
    a line of best fit
    '''
    goals_scored = []
    goals_conceded = []
    for team in teamlist:
        goals_scored.append(scored_and_conceded(df, team, name_id_dict)[0])
        goals_conceded.append(scored_and_conceded(df, team, name_id_dict)[1])
    plt.scatter(goals_conceded, goals_scored)
    plt.xlabel('Goals Conceded')
    plt.ylabel('Goals Scored')
    plt.suptitle('Goals Scored vs. Goals Conceded')
    # Line of best fit
    m, b = np.polyfit(goals_conceded, goals_scored, 1)
    print('Best fit line: ', 'goals scored = {} * goals conceded + {}'.format(m, b))
    plt.plot(goals_conceded, m * np.asarray(goals_conceded) + b, 'r')
    
    
def goals_v_team_height(matches_df, teamlist, name_id_dict, fifa_data):
    '''
    Creates scatterplot of goals scored in a season vs. average height for
    each team in teamlist
    '''
    goals_scored = []
    mean_height = []
    for team in teamlist:
        goals_scored.append(scored_and_conceded(matches_df, team, name_id_dict)[0])
        mean_height.append(fifa_data.loc[fifa_data['club'] == team]['height_cm'].mean())
    plt.scatter(mean_height, goals_scored)
    plt.xlabel('Mean Height (cm)')
    plt.ylabel('Goals Scored')
    plt.suptitle('Goals Scored vs. Mean Height')
    
    
def goals_v_goalie_height(matches_df, teamlist, name_id_dict, fifa_data):
    '''
    Creates scatterplot of goals conceded in a season vs. average GK height for
    each team in teamlist
    '''
    goals_conceded = []
    mean_gk_height = []
    for team in teamlist:
        goals_conceded.append(scored_and_conceded(matches_df, team, name_id_dict)[1])
        mean_gk_height.append(fifa_data.loc[fifa_data['club'] == team]['height_cm'].mean())
    plt.scatter(mean_gk_height, goals_conceded)
    plt.xlabel('Mean Goalkeeper Height (cm)')
    plt.ylabel('Goals Conceded')
    plt.suptitle('Goals Conceded vs. Mean GK Height')


###########################
##### Misc. Functions #####
###########################

def team_rankings():
    '''
    Returns a dictionary mapping team name keys to rank in the 2015-16 season,
    web scraping didn't work b/c team names don't exactly match the FIFA dataset.
    '''
    rankings = {
        'Leicester City': 1,
        'Arsenal': 2,
        'Tottenham Hotspur': 3,
        'Manchester City': 4,
        'Manchester United': 5,
        'Southampton': 6,
        'West Ham United': 7,
        'Liverpool': 8,
        'Stoke City': 9,
        'Chelsea': 10,
        'Everton': 11,
        'Swansea City': 12,
        'Watford': 13,
        'West Bromwich Albion': 14,
        'Crystal Palace': 15,
        'Bournemouth': 16,
        'Sunderland': 17,
        'Newcastle United': 18,
        'Norwich City': 19,
        'Aston Villa': 20
    }
    return rankings


def scrape_team_rankings():
    '''
    NOT USED
    Scrapes Wikipedia table for team rankings from the 2016 season
    https://medium.com/analytics-vidhya/web-scraping-wiki-tables-using-beautifulsoup-and-python-6b9ea26d8722
    '''
    website_url = requests.get('https://en.wikipedia.org/wiki/2015%E2%80%9316_Premier_League').text
    soup = bs4.BeautifulSoup(website_url, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    links = table.findAll('a')
    Teams = []
    for link in links:
        Teams.append(link.get('title'))
    return Teams


def reverse_team_rankings(team_rankings):
    '''
    NOT USED
    Reverses the rankings so that teams that did better have a higher number
    '''
    reverse_dict = copy.deepcopy(team_rankings)
    for key in reverse_dict:
        reverse_dict[key] = len(reverse_dict) + 1 - reverse_dict[key]
    return reverse_dict


###############################
##### Soccer DB Functions #####
###############################

def import_sql_player_data(file_path):
    '''
    Imports data from .sqlite file into a pandas dataframe
    '''
    cnx = sqlite3.connect(file_path)
    return pd.read_sql_query("SELECT * FROM Player_Attributes", cnx)


def import_sql_team_data(file_path):
    '''
    Imports data from .sqlite file into a pandas dataframe
    '''
    cnx = sqlite3.connect(file_path)
    return pd.read_sql_query("SELECT * FROM Team", cnx)


def create_name_id_dict(team_data_df):
    '''
    Convert team info dataframe to a dictionary associating team names to id
    '''
    team_names = team_data_df['team_long_name']
    team_api_ids = team_data_df['team_api_id']
    name_id_dict = {}
    for i in range(len(team_names)):
        name_id_dict.update({team_names[i]: team_api_ids[i]})
    return name_id_dict


def create_id_name_dict(team_data_df):
    '''
    NOT NEEDED
    Convert team info dataframe to a dictionary associating team names to id
    '''
    team_names = team_data_df['team_long_name']
    team_api_ids = team_data_df['team_api_id']
    name_id_dict = {}
    for i in range(len(team_names)):
        name_id_dict.update({team_api_ids[i]: team_names[i]})
    return name_id_dict


def import_sql_match_data(file_path):
    '''
    Imports data from .sqlite file into a pandas dataframe
    '''
    cnx = sqlite3.connect(file_path)
    return pd.read_sql_query("SELECT * FROM Match", cnx)


def filter_matches(df, desired_year):
    '''
    Filters dataframe representing the entire set of matches to only the matches
    of interest specified by the desired year input.
    '''
    return df.loc[df['season'] == desired_year]


def scored_and_conceded(df, team_name, name_id_dict):
    '''
    Given match data from sql DB, team name, dictionary mapping team name to id,
    calculates and returns total number of goals scored and conceded 
    (scored by other team)
    '''
    team_id = name_id_dict[team_name]
    home_games_df = df.loc[df['home_team_api_id'] == team_id]
    away_games_df = df.loc[df['away_team_api_id'] == team_id]
    goals_scored = home_games_df['home_team_goal'].sum() + away_games_df['away_team_goal'].sum()
    goals_conceded = home_games_df['away_team_goal'].sum() + away_games_df['home_team_goal'].sum()
    return goals_scored, goals_conceded