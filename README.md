# telebagger
Telebagger is a telegram + discord message scraping program. Which scrapes trading signals from various groups, and simulates their profit/loss outcomes.
The results are automatically stored in a firebase database and some groups are publically displayed on https://telebagger.netlify.app/#!

Telebagger is written in python and hosted using the heroku webservice.
Telebagger can also perform real trades for anyone with a valid trading account at binance.com, by connecting to the Binance API.
This should only be considered if it's likely a signal group will continue making profitable trading calls based on historical data produced using Telebagger.
