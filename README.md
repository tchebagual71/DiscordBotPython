# DiscordBotPython

WalletWatcher is a Discord bot that tracks Ethereum addresses and notifies users about new transactions. It's perfect for monitoring your Ethereum wallets directly from Discord.

## What does it do?

This bot allows users to add Ethereum addresses, start and stop tracking them, check the balance of addresses and tokens, get the transaction history, and more. Every time a new transaction related to a tracked address occurs, the bot sends a message with the transaction details.

## Dependencies

This bot is built in Python, using the `discord.py` and `web3.py` libraries. 

- `discord.py` is a modern, easy-to-use, feature-rich, and async-ready API wrapper for Discord written in Python.

- `web3.py` is a Python library for interacting with Ethereum. It's commonly used for smart contracts and decentralized applications (dApps).

## Setup

To set up this project, you'll need to install Python, set up a virtual environment, install the necessary packages, and configure some environment variables.

1. **Install Python**

   Make sure you have Python installed on your machine. You can download it from the [official website](https://www.python.org/downloads/). This project requires Python 3.6 or higher.

2. **Set up a virtual environment** (Optional, but recommended)

   It's a good practice to create a virtual environment for each Python project to manage dependencies separately. You can create a virtual environment using the venv module:

   python3 -m venv env
   
   To activate the environment, run:

- Windows: `.\env\Scripts\activate`
- Linux/macOS: `source env/bin/activate`

3. **Install packages**

With your virtual environment activated, install the `discord.py` and `web3.py` libraries using pip:

python3 -m pip install web3
python3 -m pip install discord.py

OR if that doesn't work, depending on your python version

pip install discord.py
pip install web3


4. **Configure environment variables**

This project requires two environment variables: `DISCORD_BOT_TOKEN` and `INFURA_URL`.

- `DISCORD_BOT_TOKEN`: The token of your Discord bot. You can get this from the [Discord Developer Portal](https://discord.com/developers/applications) by creating a new bot.

- `INFURA_URL`: The URL of your Ethereum node. You can get this from [Infura](https://infura.io/) by creating a new project. Make sure to choose the Ethereum network.

You can set these environment variables in your terminal session or add them to a `.env` file if you're using a package like python-dotenv.

## Running the bot

With everything set up, you can now run the bot:

python walletwatcher.py

The bot will now connect to your Discord server and start responding to commands.

## Usage

The bot provides several commands for users:

- `!add [alias] [address]`: Adds an Ethereum address to track with an alias.

- `!remove [alias]`: Removes an Ethereum address by its alias.

- `!list`: Lists all your Ethereum addresses and shows which are being tracked.

- `!balance [alias]`: Checks the balance of an Ethereum address by its alias.

- And more...

Use the `!help` command to get a full list of commands and their descriptions.

