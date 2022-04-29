# OurLittlePony
- **WIP, not intended for actual use, only as a learning experience!**
- Scrapes odds from SVK bookmakers and finds possible arbitrage bets. 
- Execution time ~30minutes

![Capture](https://user-images.githubusercontent.com/22457563/165987707-6afaad97-4eb6-4915-8bee-b6e9e0b2f4d9.PNG)

## Requirements:
- [Python 3](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker-compose](https://docs.docker.com/compose/install/)
- [psqlodbc 13.02](https://www.postgresql.org/ftp/odbc/versions/)


Create DB container (run from root directory)
```
docker-compose -f postgres\docker-compose.yaml up -d
```

Install required python packages ([virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) is recommended).
```
pip install -r requirements.txt
```
Discord is used for result output.
[Create webhook in discord text channel](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) and copy its url into /src/config.py
