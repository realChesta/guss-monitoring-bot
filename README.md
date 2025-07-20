# guss-monitoring-bot

Small Telegram bot that checks the guss.ch website for available apartments and notifies you via Telegram.

## Features

- Automatic hourly checks for new apartments
- Filter apartments by colony, rooms, area, and price
- Manual commands: `/subscribe`, `/filter`, `/list`, `/check`, `/resetapartments`, `/help`
- Sends apartment details with image, floor plan PDF link, and listing page link

## Prerequisites

- Python 3.13 or higher
- Telegram Bot Token
- Admin Telegram User ID (to authorize commands)

## Installation

```bash
git clone https://github.com/<your-username>/guss-monitoring-bot.git
cd guss-monitoring-bot
uv sync --system
```

Or using Hatch (requires Hatch ≥1.9 and the built-in `uv` environment plugin):

```bash
hatch run uv sync --system
```

## Configuration

Set the following environment variables:

```bash
export TELEGRAM_TOKEN="your-telegram-bot-token"
export ADMIN_USER_ID="your-telegram-user-id"
```

(`ADMIN_USER_ID` must be your Telegram user ID to authorize bot commands.)

On first run, a `settings.json` will be created automatically in the project root. You can also pre-populate it with:

```json
{
  "chat_id": null,
  "apartments": [],
  "apartment_filter": {
    "colony": [],
    "apartment_rooms": [],
    "min_apartment_area": 0,
    "max_apartment_area": 0,
    "min_price": 0,
    "max_price": 0
  }
}
```

## Usage

Start the bot:

```bash
gussbot
```

In your Telegram chat:

1. `/subscribe` - Subscribe the chat for notifications
2. `/filter colonies Langenhof,AnotherColony` - Set colony filter
3. `/filter rooms 2-3` - Set rooms filter (min-max)
4. `/filter area 0-80` - Set area filter in m²
5. `/filter price 1000-2000` - Set rent price filter
6. `/list` - List current available apartments
7. `/check` - Run manual check and get updates
8. `/resetapartments` - Reset seen apartments history
9. `/help` - Show help message

## Development

1. Create virtual environment:

```bash
uv venv venv
source venv/bin/activate
uv sync
```

2. Run the bot for development:

```bash
gussbot
```

## License

MIT License. See [LICENSE](LICENSE) for details.
