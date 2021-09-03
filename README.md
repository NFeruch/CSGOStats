# CSGOStats Data Collection

This is a data engineering/analysis project that consists of the creation of a basic ETL pipeline built by scraping a steam webpage. 

The html file that the python script scrapes the stats from is not dynamic, as to access the html, you must be signed in with two-factor authentication, which the requests library is unable to bypass (and unaccessable by Selenium too as far as I know)

There are two scripts which output pandas dataframes in different formats:

1. GameSummaryStats.py
 	- This outputs a dataframe that consists of one line per game, displaying each team's summary statistics for that match
	- Can be used to identify overarching trends throughout each game and per team
1. GameStatsPerPlayer.py
 	- This outputs a dataframe that consists of 10 lines per game, simply recording the stats for each individual player per match
	- Can be used for more in depth analysis per player
	
## Future Uses
Since the wins/losses per team and per person are included in either script, I want to look into the most import factors when winning a match. I planned to achieve this using basic **linear regression** and **logistic regression** as well as other machine learning models as I continue my learning
