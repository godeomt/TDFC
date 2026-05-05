# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

태둥포스 PC방 — a Streamlit-based food ordering web app for a private PC cafe. Orders are sent to a Discord channel via webhook.

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Environment Variables

Create a `.env` file (not committed) with:

```
PASSWORD=your_password
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

For cloud deployment (Streamlit Cloud), set these in `st.secrets` instead. `discord_utils.py` and `app.py` both try `st.secrets` first, then fall back to `.env`.

## Architecture

- **`app.py`**: Single-file Streamlit app. Handles login (password check), renders menu tabs, manages cart via `st.session_state`, and sends orders to Discord.
- **`menu_data.py`**: Menu as a plain Python dict `menu = { category: { item_name: price } }`. Edit this to add/remove menu items.
- **`discord_utils.py`**: Thin wrapper around the Discord webhook API. `send_discord_message(text)` returns `"성공"` on success or an error string.

## Key Patterns

- Session state keys: `logged_in` (bool), `cart` (list of `{name, qty, price}`), `total_price` (int).
- Each menu item widget uses a unique key `f"{category}_{item_name}"` for its `number_input`, and `f"btn_{category}_{item_name}"` for its button.
- Cart items are appended via `add_to_cart()` callback (Streamlit `on_click`), which resets the number input to 0 after adding.
