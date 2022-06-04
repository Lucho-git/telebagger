# telebagger
Telebagger is a telegram + discord message scraping program. Which scrapes trading signals from various groups, and simulates their profit/loss outcomes.
The results are automatically stored in a firebase database and some groups are publically displayed on https://telebagger.netlify.app/#!

The scraping program is written in python and hosted using the heroku webservice.
Telebagger can also perform real trades for anyone with a binance.com trading account, by connecting to it's API if it's likely a signal group will continue making profitable trading calls.
