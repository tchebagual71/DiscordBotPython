import asyncio
import discord
from discord.ext import commands
from web3 import Web3
from web3.middleware import geth_poa_middleware
import random
import logging
import json

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('bot.log')

c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

# Web3 setup
infura_url = 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'
web3 = Web3(Web3.HTTPProvider(infura_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Discord bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Your Discord bot token
DISCORD_BOT_TOKEN = 'YOUR_DISCORD_BOT_TOKEN'

# Global dictionaries to store user addresses
user_addresses = {}
tracked_addresses = {}
token_addresses = {}

# List of witty responses for the bot
witty_responses = ["Alright, your wish is my command!", "Consider it done!", "Sure thing, boss!", "On it, chief!", "You got it!"]

# ERC20 token contract ABI
erc20_abi = """[
    {"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function"},
    {"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},
    {"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},
    {"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},
    {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"type":"function"},
    {"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},
    {"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function"},
    {"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},
    {"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},
    {"inputs":[{"name":"_initialAmount","type":"uint256"},{"name":"_tokenName","type":"string"},{"name":"_decimalUnits","type":"uint8"},{"name":"_tokenSymbol","type":"string"}],"payable":false,"type":"constructor"},
    {"payable":false,"type":"fallback"},
    {"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},
    {"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}
]"""

# Functions to save and load user data
def save_data():
    with open('user_data.json', 'w') as f:
        json.dump({
            'user_addresses': user_addresses,
            'tracked_addresses': tracked_addresses,
            'token_addresses': token_addresses
        }, f)

def load_data():
    try:
        with open('user_data.json', 'r') as f:
            data = json.load(f)
            return data.get('user_addresses', {}), data.get('tracked_addresses', {}), data.get('token_addresses', {})
    except FileNotFoundError:
        return {}, {}, {}

# Load data at startup
user_addresses, tracked_addresses, token_addresses = load_data()

def is_valid_address(address):
    return Web3.is_address(address)

# Witty response function
def get_witty_response():
    return random.choice(witty_responses)

# Helper function for formatting balance with commas
def format_balance(balance):
    return "{:,.2f}".format(balance)

@bot.command(name='add', help='➕ Adds an Ethereum address to track with an alias. \nUsage: !add myWallet 0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
async def add_address(ctx, alias: str, address: str):
    logger.info(f'add_address was called with alias: {alias} and address: {address}')
    user_id = ctx.author.id
    if user_id not in user_addresses:
        user_addresses[user_id] = {}

    if len(user_addresses[user_id]) >= 10:
        await ctx.send('❗ You have reached the maximum limit of 10 addresses.')
        return

    if alias in user_addresses[user_id]:
        await ctx.send('❌ This alias is already in use. Please choose a different alias.')
        return

    if is_valid_address(address):
        user_addresses[user_id][alias] = address.lower()
        save_data()
        await ctx.send(f'{get_witty_response()}\n✅ Address `{address}` with alias `{alias}` added. Use `!watch {alias}` to start tracking transactions.')
        logger.info(f'User {ctx.author.name} added address {address} with alias {alias}.')
    else:
        await ctx.send('❌ Invalid address. Please try again.')
        logger.warning(f'User {ctx.author.name} tried to add invalid address {address}.')

@bot.command(name='latest_block', help='🔢 Get the latest block number.')
async def get_latest_block(ctx):
    try:
        latest_block = web3.eth.block_number
        await ctx.send(f'✅ The latest block number is: {latest_block}.')
    except Exception as e:
        await ctx.send(f'❌ Error getting latest block number: {str(e)}')
        logger.error(f'Error getting latest block number: {str(e)}')

@bot.command(name='transaction_count', help='🔢 Get the number of transactions sent from an address. \nUsage: !transaction_count myWallet')
async def get_transaction_count(ctx, alias: str):
    user_id = ctx.author.id
    if user_id not in user_addresses or alias not in user_addresses[user_id]:
        await ctx.send('❌ Invalid alias. Please try again.')
        logger.warning(f'Invalid alias {alias} provided by user {ctx.author.name}.')
        return

    address = user_addresses[user_id][alias]
    checksum_address = Web3.to_checksum_address(address)
    try:
        tx_count = web3.eth.get_transaction_count(checksum_address)
        await ctx.send(f'✅ The number of transactions sent from address `{checksum_address}` (alias: `{alias}`) is: {tx_count}.')
    except Exception as e:
        await ctx.send(f'❌ Error getting transaction count: {str(e)}')
        logger.error(f'Error getting transaction count: {str(e)}')

@bot.command(name='transaction_receipt', help='🧾 Get the receipt of a transaction. \nUsage: !transaction_receipt 0xTransactionHash')
async def get_transaction_receipt(ctx, tx_hash: str):
    try:
        receipt = web3.eth.get_transaction_receipt(tx_hash)
        await ctx.send(f'✅ Transaction receipt for {tx_hash}:\n\n{receipt}.')
    except Exception as e:
        await ctx.send(f'❌ Error getting transaction receipt: {str(e)}')
        logger.error(f'Error getting transaction receipt: {str(e)}')

@bot.command(name='gas_estimate', help='⛽️ Estimate the gas required to send a transaction. \nUsage: !gas_estimate myWallet 0xRecipientAddress EtherValue')
async def estimate_gas(ctx, alias: str, to: str, value: str):
    user_id = ctx.author.id
    if user_id not in user_addresses or alias not in user_addresses[user_id]:
        await ctx.send('❌ Invalid alias. Please try again.')
        logger.warning(f'Invalid alias {alias} provided by user {ctx.author.name}.')
        return

    from_address = user_addresses[user_id][alias]
    checksum_from_address = Web3.to_checksum_address(from_address)
    checksum_to_address = Web3.to_checksum_address(to)
    try:
        gas_estimate = web3.eth.estimate_gas({
            "from": checksum_from_address,
            "to": checksum_to_address,
            "value": web3.to_wei(value, 'ether')
        })
        # Send the gas estimate to the user
        await ctx.send(f'✅ Gas estimate to send {value} Ether from `{checksum_from_address}` (alias: `{alias}`) to `{checksum_to_address}`: {gas_estimate}.')
    except Exception as e:
        # If an error occurs, send an error message to the user
        await ctx.send(f'❌ Error estimating gas: {str(e)}')
        logger.error(f'Error estimating gas: {str(e)}')

# Define a new bot command to check the status of the Ethereum network
@bot.command(name='network_status', help='🌐 Check the status of the Ethereum network.')
async def check_network_status(ctx):
    try:
        # Check if the bot is connected to the Ethereum network
        if web3.isConnected():
            # If connected, send a confirmation message to the user
            await ctx.send('✅ Connected to the Ethereum network.')
        else:
            # If not connected, send an error message to the user
            await ctx.send('❌ Not connected to the Ethereum network.')
    except Exception as e:
        # If an error occurs, send an error message to the user
        await ctx.send(f'❌ Error checking network status: {str(e)}')
        logger.error(f'Error checking network status: {str(e)}')

# Define a new bot command to add a token contract address to track with an alias
@bot.command(name='addtoken', help='➕ Adds a token contract address to track with an alias. \\nUsage: !addtoken myToken 0xTokenContractAddress')
async def add_token_address(ctx, alias: str, address: str):
    logger.info(f'add_token_address was called with alias: {alias} and address: {address}')
    user_id = ctx.author.id

    # If the user doesn't have any token addresses yet, create a new dictionary for them
    if user_id not in token_addresses:
        token_addresses[user_id] = {}

    # Check if the user already has 10 token addresses, which is the limit
    if len(token_addresses[user_id]) >= 10:
        await ctx.send('❗ You have reached the maximum limit of 10 token addresses.')
        return

    # Check if the alias is already in use
    if alias in token_addresses[user_id]:
        await ctx.send('❌ This alias is already in use. Please choose a different alias.')
        return

    # Check if the address is valid
    if is_valid_address(address):
        # Save the address and alias to the token_addresses dictionary and save the data
        token_addresses[user_id][alias] = address.lower()
        save_data()

        # Send a confirmation message to the user
        await ctx.send(f'✅ Token contract address `{address}` with alias `{alias}` added.')
        logger.info(f'User {ctx.author.name} added token contract address {address} with alias {alias}.')
    else:
        # If the address is not valid, send an error message to the user
        await ctx.send('❌ Invalid address. Please try again.')
        logger.warning(f'User {ctx.author.name} tried to add invalid token contract address {address}.')

# Define a new bot command to remove an Ethereum address by its alias
@bot.command(name='remove', help='➖ Removes an Ethereum address by its alias. \\nUsage: !remove myWallet')
async def remove_address(ctx, alias: str):
    logger.info(f'remove_address was called with alias: {alias}')
    user_id = ctx.author.id

    # Check if the user has any addresses
    if user_id not in user_addresses:
        await ctx.send('❗ No addresses to remove.')
        return

    # Check if the alias exists in the user's addresses
    if alias in user_addresses[user_id]:
        # If it does, remove the address and alias from the user_addresses dictionary and save the data
        removed_address = user_addresses[user_id].pop(alias)
        if user_id in tracked_addresses and alias in tracked_addresses[user_id]:
            tracked_addresses[user_id].pop(alias)
            save_data()
        # Send a confirmation message to the user
        await ctx.send(f'{get_witty_response()}\n✅ Address `{removed_address}` with alias `{alias}` removed.')
    else:
        # If the alias does not exist, send an error message to the user
        await ctx.send('❌ Invalid alias. Please try again.')

# Define a new bot command to list all the user's Ethereum addresses and shows which are being tracked
@bot.command(name='list', help='📜 Lists all your Ethereum addresses and shows which are being tracked.')
async def list_addresses(ctx):
    logger.info('list_addresses was called')
    user_id = ctx.author.id

    # Check if the user has any addresses
    if user_id not in user_addresses or not user_addresses[user_id]:
        await ctx.send('❗ No addresses to display.')
        return

    # Create a response string with all the user's addresses and their tracking status
    response = 'Your addresses:\\n\\n'
    for alias, address in user_addresses[user_id].items():
        tracking_status = "👀✅" if user_id in tracked_addresses and alias in tracked_addresses[user_id] else "❌"
        response += f'{alias}: `{address}` {tracking_status}\\n'

    # Send the response to the user
    await ctx.send(response)

# Define a new bot command to list all the user's added token contract addresses
@bot.command(name='tokens', help='📜 Lists all your added token contract addresses.')
async def list_tokens(ctx):
    logger.info('list_tokens was called')
    user_id = ctx.author.id

    # Check if the user has any token contract addresses
    if user_id not in token_addresses or not token_addresses[user_id]:
        await ctx.send('❗ No token contract addresses to display.')
        return

    response = 'Your token contract addresses:\n\n'
    for alias, address in token_addresses[user_id].items():
        response += f'{alias}: `{address}`\n'

    await ctx.send(response)

@bot.command(name='watch', help='👀 Starts tracking transactions for an Ethereum address by its alias. \nUsage: !watch myWallet')
async def track_address(ctx, alias: str):
    logger.info(f'track_address was called with alias: {alias}')
    user_id = ctx.author.id
    if user_id not in user_addresses or alias not in user_addresses[user_id]:
        await ctx.send('❌ Invalid alias. Please add the address first.')
        return

    if user_id not in tracked_addresses:
        tracked_addresses[user_id] = {}
        save_data()

    tracked_addresses[user_id][alias] = user_addresses[user_id][alias]
    await ctx.send(f'{get_witty_response()}\n✅ Started tracking transactions for address with alias `{alias}`.')

@bot.command(name='tokeninfo', help='💰 Get information about a specific ERC20 token. \nUsage: !tokeninfo myToken')
async def get_token_info(ctx, token_alias: str):
    logger.info(f'get_token_info was called with token_alias: {token_alias}')
    user_id = ctx.author.id
    if user_id not in token_addresses or token_alias not in token_addresses[user_id]:
        await ctx.send('❌ Invalid token alias. Please try again.')
        return

    contract_address = token_addresses[user_id][token_alias]
    contract = web3.eth.contract(address=contract_address, abi=erc20_abi)
    try:
        token_name = contract.functions.name().call()
        token_symbol = contract.functions.symbol().call()
        total_supply = contract.functions.totalSupply().call()
        await ctx.send(f'✅ Info for token with contract address `{contract_address}` (alias: `{token_alias}`):\nName: {token_name}\nSymbol: {token_symbol}\nTotal supply: {total_supply}.')
    except Exception as e:
        await ctx.send(f'❌ Error getting token info: {str(e)}')
        logger.error(f'Failed to get token info for token_alias: {token_alias}. Error: {str(e)}')

@bot.command(name='stop', help='⛔ Stops tracking transactions for an Ethereum address by its alias. \nUsage: !stop myWallet')
async def stop_tracking(ctx, alias: str):
    logger.info(f'stop_tracking was called with alias: {alias}')
    user_id = ctx.author.id
    if user_id not in tracked_addresses or alias not in tracked_addresses[user_id]:
        await ctx.send('❌ Invalid alias. Please check the addresses you are tracking.')
        return

    tracked_addresses[user_id].pop(alias)
    await ctx.send(f'{get_witty_response()}\n✅ Stopped tracking transactions for address with alias `{alias}`.')

@bot.command(name='tokenbalance', help='💰 Checks the balance of a specific ERC20 token for an Ethereum address. \\nUsage: !tokenbalance myWallet myToken')
async def check_token_balance(ctx, address_alias: str, token_alias: str):
    user_id = ctx.author.id
    logger.info(f'check_token_balance was called with address_alias: {address_alias} and token_alias: {token_alias}')

    if user_id not in user_addresses or address_alias not in user_addresses[user_id]:
        await ctx.send('❌ Invalid address alias. Please try again.')
        logger.warning(f'Invalid address alias {address_alias} provided by user {ctx.author.name}.')
        return

    if user_id not in token_addresses or token_alias not in token_addresses[user_id]:
        await ctx.send('❌ Invalid token alias. Please try again.')
        logger.warning(f'Invalid token alias {token_alias} provided by user {ctx.author.name}.')
        return

    address = user_addresses[user_id][address_alias]
    checksum_address = Web3.to_checksum_address(address)
    logger.info(f'Using address {checksum_address} for balance check.')

    contract_address = token_addresses[user_id][token_alias]
    checksum_contract_address = Web3.to_checksum_address(contract_address)
    logger.info(f'Using contract address {checksum_contract_address} for balance check.')

    try:
        # Create a contract object
        token_contract = web3.eth.contract(address=checksum_contract_address, abi=erc20_abi)

        # Call the balanceOf function and get the token balance
        token_balance = token_contract.functions.balanceOf(checksum_address).call()

        # Format the token balance
        formatted_token_balance = format_balance(token_balance)

        # Send the response with the token balance
        await ctx.send(f'✅ Balance of token with contract address `{checksum_contract_address}` (alias: `{token_alias}`) for address `{checksum_address}` (alias: `{address_alias}`): {formatted_token_balance}.')
    except web3.exceptions.CannotHandleRequest as e:
        await ctx.send(f'❌ Error connecting to the Ethereum network: {str(e)}')
        logger.error(f'Error connecting to the Ethereum network: {str(e)}')
    except Exception as e:
        await ctx.send(f'❌ Error checking token balance: {str(e)}')
        logger.error(f'Error checking token balance: {str(e)}')

@bot.command(name='checktokenbalance', help='💰 Checks the balance of a specific ERC20 token for an Ethereum address. \nUsage: !checktokenbalance 0xYourEthAddress 0xTokenContractAddress')
async def simplified_check_token_balance(ctx, eth_address: str, token_contract_address: str):
    try:
        # Convert input addresses to checksum addresses
        checksum_eth_address = Web3.to_checksum_address(eth_address)
        checksum_token_contract_address = Web3.to_checksum_address(token_contract_address)

        # Create a contract object
        token_contract = web3.eth.contract(address=checksum_token_contract_address, abi=erc20_abi)

        # Call the balanceOf function and get the token balance
        token_balance = token_contract.functions.balanceOf(checksum_eth_address).call()

        # Format the token balance
        formatted_token_balance = format_balance(token_balance)

        # Send the response with the token balance
        await ctx.send(f'✅ Balance of token with contract address `{checksum_token_contract_address}` for address `{checksum_eth_address}`: {formatted_token_balance}.')
    except web3.exceptions.CannotHandleRequest as e:
        await ctx.send(f'❌ Error connecting to the Ethereum network: {str(e)}')
        logger.error(f'Error connecting to the Ethereum network: {str(e)}')
    except Exception as e:
        await ctx.send(f'❌ Error checking token balance: {str(e)}')
        logger.error(f'Error checking token balance: {str(e)}')



@bot.command(name='blocktransactions', help='📜 List all transactions in a specific block. \nUsage: !blocktransactions blockNumber')
async def get_block_transactions(ctx, block_number: int):
    logger.info(f'get_block_transactions was called with block_number: {block_number}')
    try:
        block = web3.eth.get_block(block_number, full_transactions=True)
        if not block['transactions']:
            await ctx.send('❌ No transactions in this block.')
            return

        response = f'Transactions in block `{block_number}`:\n\n'
        for tx in block['transactions']:
            response += f'From: `{tx["from"]}`\nTo: `{tx["to"]}`\nValue: {web3.fromWei(tx["value"], "ether")} ETH\nHash: `{tx["hash"].hex()}`\n\n'

        await ctx.send(response)
    except Exception as e:
        await ctx.send(f'❌ Error getting transactions: {str(e)}')
        logger.error(f'Failed to get transactions for block_number: {block_number}. Error: {str(e)}')

@bot.command(name='balance', help='💰 Checks the balance of an Ethereum address by its alias. \nUsage: !balance myWallet')
async def check_balance(ctx, alias: str):
    user_id = ctx.author.id
    logger.info(f'check_balance was called with alias: {alias}')

    if user_id not in user_addresses or alias not in user_addresses[user_id]:
        await ctx.send('❌ Invalid alias. Please try again.')
        logger.warning(f'Invalid alias {alias} provided by user {ctx.author.name}.')
        return

    address = user_addresses[user_id][alias]
    checksum_address = Web3.to_checksum_address(address)
    logger.info(f'Using address {checksum_address} for balance check.')

    try:
        balance = web3.eth.get_balance(checksum_address)
        eth_balance = web3.from_wei(balance, 'ether')
        await ctx.send(f'{get_witty_response()}\n✅ Balance of address `{checksum_address}` (alias: `{alias}`): {format_balance(eth_balance)} ETH.')
        logger.info(f'Balance check successful. Balance: {eth_balance} ETH.')
    except Exception as e:
        await ctx.send(f'❌ Error checking balance: {str(e)}')
        logger.error(f'Error checking balance: {str(e)}')
        
@bot.command(name='get_block_details', help='Retrieve the details of a specific block in the Ethereum blockchain. \\nUsage: !get_block_details blockNumber')
async def get_block_details(ctx, block_number: int):
    try:
        block = web3.eth.get_block(block_number)
        await ctx.send(f'Block details: {block}')
    except Exception as e:
        await ctx.send(f'Error getting block details: {str(e)}')

@bot.command(name='gasprice', help='⛽️ Checks the current average gas price.')
async def check_gas_price(ctx):
    gas_price = web3.eth.gas_price
    gwei_gas_price = web3.from_wei(gas_price, 'gwei')
    await ctx.send(f'{get_witty_response()}\n✅ Current average gas price: {gwei_gas_price} Gwei. (Source: [Etherscan](https://etherscan.io/gastracker))')

@bot.command(name='transaction', help='📄 Get details about a specific transaction. \nUsage: !transaction myWallet 0xTransactionHash')
async def get_transaction(ctx, alias: str, tx_hash: str):
    user_id = ctx.author.id
    if user_id not in user_addresses or alias not in user_addresses[user_id]:
        await ctx.send('❌ Invalid alias. Please try again.')
        return

    try:
        tx = web3.eth.get_transaction(tx_hash)
    except Exception as e:
        await ctx.send(f'❌ Failed to get transaction: {str(e)}')
        return

    msg = f'📄 Transaction details for {tx_hash} (Address alias: `{alias}`):\n\n'
    msg += f'👤 From: `{tx["from"]}`\n'
    msg += f'👥 To: `{tx["to"]}`\n'
    msg += f'💰 Value: {format_balance(web3.from_wei(tx["value"], "ether"))} ETH\n'
    msg += f'⛽ Gas Price: {web3.from_wei(tx["gasPrice"], "gwei")} Gwei\n'
    msg += f'💸 Transaction Fee: {format_balance(web3.from_wei(tx["gas"] * tx["gasPrice"], "ether"))} ETH\n'
    msg += f'🔍 Etherscan: [View on Etherscan](https://etherscan.io/tx/{tx_hash})'


    await ctx.send(f'✅ {msg}')    

async def watch_transactions():
    while not bot.is_closed():
        for user_id, addresses in tracked_addresses.items():
            if not addresses:
                continue

            user = bot.get_user(user_id)
            if not user:
                continue

            block = web3.eth.get_block('latest')
            if block and block.transactions:
                for transaction in block.transactions:
                    tx_hash = transaction.hex()
                    tx = web3.eth.get_transaction(tx_hash)
                    if tx.to is not None:
                        for alias, address in addresses.items():
                            if tx.to.lower() == address or tx['from'].lower() == address:
                                direction = "to" if tx.to.lower() == address else "from"
                                msg = f"✅ Transaction found for address `{address}` (alias: `{alias}`) in block {block.number} ({direction}):\n\n"
                                msg += f"🔗 Hash: `{tx_hash}`\n"
                                msg += f"👤 From: `{tx['from']}`\n"
                                msg += f"👥 To: `{tx['to']}`\n"
                                msg += f"💰 Value: {format_balance(web3.from_wei(tx['value'], 'ether'))} ETH\n"
                                msg += f"⛽ Gas Price: {web3.from_wei(tx['gasPrice'], 'gwei')} Gwei\n"
                                msg += f"💸 Transaction Fee: {format_balance(web3.from_wei(tx['gas'] * tx['gasPrice'], 'ether'))} ETH\n"
                                msg += f"🔍 Etherscan: [View on Etherscan](https://etherscan.io/tx/{tx_hash})"

                                await user.send(f'✉️ {msg}')
                                # Send message to the 'transaction-alerts' channel
                                transaction_alerts_channel = None
                                for guild in bot.guilds:
                                    for channel in guild.text_channels:
                                        if channel.name == "transaction-alerts":
                                            transaction_alerts_channel = channel
                                            break
                                    if transaction_alerts_channel:
                                        break

                                if transaction_alerts_channel:
                                    await transaction_alerts_channel.send(f'🔔 {msg}')

        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f'Ready! Logged in as {bot.user.name}#{bot.user.discriminator}')
    bot.loop.create_task(watch_transactions())
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                greeting_message = f"```🤖👀\nBot connected and ready!\nBot tag: {bot.user.name}#{bot.user.discriminator}```\n```Use !help for a list of commands```"
                await channel.send(greeting_message)
                break

async def main():
    try:
        await bot.start(DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.logout()
        await bot.close()

if __name__ == '__main__':
    asyncio.run(main())