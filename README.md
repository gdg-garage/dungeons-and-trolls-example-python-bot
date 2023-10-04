
## Dungeons and Trolls Python bot
This project implements a Python bot for the Dungeons and Trolls RPG game https://github.com/gdg-garage/dungeons-and-trolls.

**Installation**

To install the bot, you will need to have Python 3 installed. Once you have it, you can create a virtual environment:

```
python3 -m venv venv
```

Once the virtual environment is created, you can activate it and install the bot's dependencies:

```
source venv/bin/activate
pip install -r requirements.txt
```

**Usage**

* Add your api key to the .env file. You can api key by calling register in the following manner:
```sh
curl --location --request POST 'https://docker.tivvit.cz/v1/register' \
--header 'Content-Type: application/json' \
--data-raw '{
  "username": "<your name>"
}'
```
* Run the bot with 
```
python3 bot.py
```
