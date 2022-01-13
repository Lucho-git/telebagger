import asyncio  # desyncs telegram calls to make timings work, idk

from telethon import TelegramClient, events
from telethon.sync import TelegramClient
from telethon.sessions import StringSession


async def telegram_scraper():
    loop = asyncio.get_event_loop()

    stringsesh = '1BVtsOIYBu1plRXVE_x8uu9hhzZtXL558s8DxJYuxWavIZvSk3bLgxqzD3pv87gsGJotDsPsS7OqZXoki_SsPWO2gMWUNjmbJtFTtxCNtFy-DfpT8dZ2SUqDa0JvJpH1GG9ha1o5F51rexEmTfOdv8z36w3p7WmGM0N58Iwt3F4ss63wcOpdLuS0GbLYqO-_qw1mMjE8AClV_EUCYjgVsWsJB463w1pkJ3NVcjWaaTwkXQtbsM09inxkgAQIsiyAxYB0PGrAEVTQkeB4OEX2fYFUiURtnSS2Un5foGG_h6UP-efnJzig49oGnlNOIqp0j2ZEj41K0qmbIL2mDIhh-P3MPJxMV_5k='
    api_id = 5747368
    api_hash = '19f6d3c9d8d4e6540bce79c3b9223fbe'
    client = TelegramClient(StringSession(stringsesh), api_id, api_hash)

    @client.on(events.NewMessage())
    async def my_event_handler(event):
        chat = await event.get_chat()
        sender = await event.get_sender()

        sender_id = str(sender.id)
        message = str(event.raw_text)
        print(sender_id)
        print(message)

        if chat.id == 1899129008:  # Telegram Bot
            print("Robot Section +++")
            # Bot commands
            if message == '/stop':
                await client.disconnect()
                print("End of line")

    return client


async def run_tele():
    client = await telegram_scraper()
    print("Launching Telegram Scraper...")
    await client.start()
    await client.get_dialogs()
    await client.run_until_disconnected()

asyncio.run(run_tele())
