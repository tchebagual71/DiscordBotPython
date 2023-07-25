# WalletWatcher - A Discord Bot for Tracking Eth Transactions

WalletWatcher is a Discord bot designed to track and notify users about transactions related to their Ethereum addresses. Perfect for monitoring your Ethereum wallets directly from Discord.

## Description

The bot has the capability to track up to 10 Ethereum addresses per user. Each address can be given an alias for easier management. For example, you can give the alias "myWallet" to your Ethereum address, and use this alias for all future commands, making it easier to remember and manage your addresses.

Beyond tracking addresses, WalletWatcher provides an array of functionalities including retrieving the balance of an Ethereum address or ERC20 token, getting the transaction count of an address, estimating the gas required to send a transaction, and more. It can also provide network status checks, such as the latest block number and the current average gas price.

To enhance interaction, it includes witty responses that add a fun touch to the notifications and responses it sends.

## Features

    Track up to 10 Ethereum addresses per user, each with its own alias.
    Get notified about transactions involving your tracked addresses.
    Check the balance of your Ethereum addresses.
    Check the balance of ERC20 tokens.
    Get the transaction count of your addresses.
    Estimate gas required to send a transaction.
    Retrieve the details of a specific block in the Ethereum blockchain.
    Get network status like the latest block number and the current average gas price.
    Add and track ERC20 token contract addresses.
    All interactions are made simple through commands in Discord.

## Setup

To set up this project, you need Python, a virtual environment, necessary packages, and environment variables.

## Install Python

Install Python on your machine. Download it from the official website. This project requires Python 3.6 or higher.

## Set up a virtual environment (Optional, but recommended)

Create a virtual environment for the project to manage dependencies. You can create it using the venv module:

bash

python3 -m venv env

Activate the environment:

    Windows: .\env\Scripts\activate
    Linux/macOS: source env/bin/activate

## Install packages

With the virtual environment activated, install the discord.py and web3.py libraries using pip:

python3 -m pip install discord.py web3

## Configure environment variables

Set two environment variables: DISCORD_BOT_TOKEN and INFURA_URL.

    DISCORD_BOT_TOKEN: Your Discord bot token. Get it from the Discord Developer Portal by creating a new bot.
    INFURA_URL: The URL of your Ethereum node. Get it from Infura by creating a new project. Choose the Ethereum network.

You can set these environment variables in your terminal session or add them to a .env file if you're using the python-dotenv package.

## Running the bot

Run the bot with the command:

python walletwatcher.py

The bot now connects to your Discord server and starts responding to commands.

## Usage

Use the !help command to get a full list of commands and their descriptions. Here are some examples:

    !add [alias] [address]: Add an Ethereum address to track with an alias.
    !remove [alias]: Remove a tracked Ethereum address by its alias.
    !list: List all your Ethereum addresses and their tracking status.
    !balance [alias]: Check the balance of an Ethereum address by its alias.
    !addtoken [alias] [address]: Add an ERC20 token contract address to track with an alias.
    !tokenbalance [address_alias] [token_alias]: Check the balance of a specific ERC20 token for an Ethereum address.

Remember, you can track up to 10 Ethereum addresses and 10 token contract addresses, each with its own alias for easy interaction.

- `!balance [alias]`: Checks the balance of an Ethereum address by its alias.

- And more...

Use the `!help` command to get a full list of commands and their descriptions.

# Potential Improvements and Issues

    Enhanced Error Handling: Developers could work on implementing more comprehensive error handling to make the bot more robust and reliable. This could include handling more specific exceptions, improved logging, or even user-friendly error messages.

    Implement Data Persistence: Right now, all the data is lost when the bot is restarted. Implementing a database or some form of persistent storage would be a significant improvement. This could be done using a variety of technologies, such as SQLite for a lightweight solution, or a more robust database system like PostgreSQL for larger applications.

    Testing Suite: There currently aren't any tests for the bot. Developers could create a suite of unit tests to ensure that all commands and functions work as expected. This would make the bot more reliable and easier to maintain and upgrade.

    Security Enhancements: While the bot is relatively safe as it is, there's always room for improvement in security. Developers could look into ways to further sanitize inputs, implement rate limiting to prevent abuse, or audit the code for potential security vulnerabilities.

    User Experience (UX) Improvements: The bot could be more interactive. Developers could implement embeds for better-looking responses, or add reactions for simple user interactions. They could also make the help command more detailed or easier to understand.

    Command Extensions: Developers could add new commands or features to the bot. This could include integrating with other Ethereum services, adding support for more types of transactions, or even allowing users to interact with smart contracts directly from Discord.

    Code Refactoring: The code could be refactored to make it more efficient, readable, or maintainable. This could include things like separating the code into more files, improving the structure of the code, or even just cleaning up and commenting the code better.

Please remember this is just a fun side project with alot of fluff and bad code. Please reach out if you have any questions, my twitter handle is on my profile.
