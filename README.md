# Telegram Shift Exchange Bot

A Telegram bot for managing shift exchanges in a group chat. The bot provides an interactive form for submitting shift exchange requests.

## Features

- Interactive inline buttons for day selection
- Forum topics support - messages are kept in the same thread
- Automatic message cleanup after conversation ends
- Simple and intuitive user interface

## Setup

1. Create a new Telegram bot using [@BotFather](https://t.me/botfather)
2. Get your bot token and set it as an environment variable:
   ```bash
   export BOT_TOKEN="your_bot_token_here"
   ```
3. Install required dependencies:
   ```bash
   pip install python-telegram-bot
   ```
4. Update the `GROUP_CHAT_ID` and `GROUP_THREAD_ID` in the code to match your group settings
5. Run the bot:
   ```bash
   python formularz_bot.py
   ```

## Usage

1. Start the bot with `/start` command
2. Follow the interactive prompts to submit a shift exchange request
3. The request will be automatically posted to the designated group thread

## Requirements

- Python 3.7+
- python-telegram-bot library
