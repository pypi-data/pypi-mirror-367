# python-zalo-bot

This SDK package is developed based on [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) – a popular open-source library for Telegram Bot, licensed under [MIT License](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/LICENSE).

This SDK version is customized and extended to meet the requirements for building Zalo Bot. All modifications comply with the MIT license and retain the original author's copyright.

# python-zalo-bot

A Python wrapper for the Zalo Bot API — making it easy to build chatbots for the Zalo ecosystem, inspired by python-telegram-bot.

## Require

- Python >= 3.8

## Install

```sh
pip install python-zalo-bot
```

---

## Example

### Introduction to the API

```python
import asyncio
import zalo_bot

async def main():
    bot = zalo_bot.Bot("YOUR_BOT_TOKEN")
    async with bot:
        me = await bot.get_me()
        print(f"Bot's name: {me.account_name}, ID: {me.id}")
        update = await bot.get_update(timeout=60)
        chat_id = update.message.chat.id if update and update.message else "CHAT_ID"
        await bot.send_message(chat_id, "Hello from Zalo Bot!")
        await bot.send_photo(chat_id, "Ảnh demo", "https://placehold.co/600x400")
        await bot.send_sticker(chat_id, "d063f44dc80821567819")

if __name__ == '__main__':
    asyncio.run(main())
```

---

### Long Polling

```python
from zalo_bot import Update
from zalo_bot.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chào {update.effective_user.display_name}! Tôi là chatbot!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Bạn vừa nói: {update.message.text}")

if __name__ == "__main__":
    app = ApplicationBuilder().token("ZALO_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🤖 Bot đang chạy...")
    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("Bot đã dừng lại.")
```

---

### Webhook

```python
from flask import Flask, request
from zalo_bot import Bot, Update
from zalo_bot.ext import Dispatcher, CommandHandler, MessageHandler, filters

app = Flask(__name__)
TOKEN = 'ZALO_BOT_TOKEN'
bot = Bot(token=TOKEN)

async def start(update: Update, context):
    await update.message.reply_text(f"Xin chào {update.effective_user.display_name}!")

async def echo(update: Update, context):
    await update.message.reply_text(f"Bạn vừa nói: {update.message.text}")

with app.app_context():
    webhook_url = 'your_webhook_url'
    bot.set_webhook(url=webhook_url, secret_token='your_secret_token_here')

    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True)['result'], bot)
    dispatcher.process_update(update)
    return 'ok'

if __name__ == '__main__':
    app.run(port=8443)
```

---

## API

### `class zalo_bot.Bot(token: str)`

Khởi tạo bot với mã thông báo xác thực.

#### Methods

- `async get_me() -> User`  
  Lấy thông tin tài khoản bot.

- `async get_update(timeout: int = 60) -> Optional[Update]`  
  Lấy một cập nhật mới từ server.

- `async send_message(chat_id: str, text: str) -> Message`  
  Gửi tin nhắn văn bản.

- `async send_photo(chat_id: str, caption: str, photo_url: str) -> Message`  
  Gửi hình ảnh với chú thích.

- `async send_sticker(chat_id: str, sticker_id: str) -> Message`  
  Gửi sticker.

- `async send_chat_action(chat_id: str, action: str) -> bool`  
  Gửi hành động chat (typing).

- `async set_webhook(url: str, secret_token: str) -> bool`  
  Cài đặt webhook.

- `async get_webhook_info() -> WebhookInfo`  
  Lấy thông tin webhook.

- `async delete_webhook() -> bool`  
  Xóa webhook.

---

### `class zalo_bot.Message(...)`

Đại diện cho một tin nhắn gửi đến bot. Cung cấp các phương thức trả lời nhanh.

#### Methods

- `async reply_text(text: str)`  
  Trả lời văn bản.

- `async reply_photo(photo_url: str, caption: str = "")`  
  Gửi ảnh kèm chú thích.

- `async reply_sticker(sticker_id: str)`  
  Gửi sticker trả lời.

- `async reply_action(action: str)`  
  Gửi hành động chat trả lời (typing).

---

## Chat Actions

Chat actions cho phép bot hiển thị các chỉ báo trực quan như "đang soạn tin..." để cải thiện trải nghiệm người dùng.

### Các hành động có sẵn

```python
from zalo_bot.constants import ChatAction

# Các hành động cơ bản
ChatAction.TYPING              # Đang soạn tin...
```

### Cách sử dụng

```python
import asyncio
from zalo_bot import Update
from zalo_bot.ext import ApplicationBuilder, CommandHandler, ContextTypes
from zalo_bot.constants import ChatAction

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Hiển thị "đang soạn tin..." trước khi trả lời
    await context.bot.send_chat_action(
        chat_id=update.message.chat.id, 
        action=ChatAction.TYPING
    )
    await asyncio.sleep(2)
    await update.message.reply_text("Chào bạn!")
```

---

## zalo_bot.ext

Thư mục `ext` (extension) cung cấp các thành phần mở rộng giúp xây dựng bot theo cách hướng sự kiện (event-based)

### `ApplicationBuilder`

Khởi tạo một ứng dụng bot với cấu hình tùy chỉnh.

```python
from zalo_bot.ext import ApplicationBuilder

app = ApplicationBuilder().token("ZALO_BOT_TOKEN").build()
```

#### Phương thức:
- `token(token: str)` – cấu hình token.
- `build()` – khởi tạo `Application` từ builder.

---

### `Application`

Một thực thể điều phối bot, xử lý sự kiện và chạy polling hoặc webhook.

#### Phương thức chính:
- `add_handler(handler: BaseHandler)` – thêm handler xử lý lệnh hoặc tin nhắn.
- `run_polling()` – khởi động polling để nhận update.

---

### `CommandHandler`

Xử lý các lệnh kiểu `/start`, `/echo`,...

```python
CommandHandler("start", start_callback)
```

---

### `MessageHandler`

Xử lý tin nhắn văn bản, hình ảnh,... phù hợp với filter.

```python
MessageHandler(filters.TEXT & ~filters.COMMAND, echo_callback)
```

---

### `filters`

Cung cấp các filter để lọc loại dữ liệu từ tin nhắn:

- `filters.TEXT` – tin nhắn dạng văn bản
- `filters.COMMAND` – tin nhắn là command (bắt đầu với /)
- `filters.TEXT & ~filters.COMMAND` – chỉ văn bản, không phải command

---

### Ví dụ sử dụng ext

```python
from zalo_bot import Update
from zalo_bot.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chào {update.effective_user.display_name}!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Bạn vừa nói: {update.message.text}")

if __name__ == "__main__":
    app = ApplicationBuilder().token("ZALO_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.bot.delete_webhook()
    app.run_polling()
```
