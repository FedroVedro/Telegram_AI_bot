from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from openai import OpenAI

TELEGRAM_TOKEN = "..."
OPEN_AI_API = "..."

model_chat_gpt = "gpt-4o-mini" # Выбор модели из доступних в OpenAI

client = OpenAI(api_key=OPEN_AI_API)

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        ["Навигатор по информационным системам", "Чат с искусственным интеллектом"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Добрый день! Я бот-помощник компании BM Group. Выберите действие:",
        reply_markup=reply_markup
    )

# Функция для обработки нажатия кнопки "Навигатор"
async def navigator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите нужный ресурс:\n"
        "1. [ELMA](http://178.210.46.53:8000/)\n"
        "2. [HR Box](https://bmgroup.hrbox.io/)\n"
        "3. [AmoCRM](https://bmgroup.amocrm.ru/)\n"
        "4. [MangoOffice](https://lk.mango-office.ru)\n"
        "5. [Exon](https://exon.exonproject.ru/)\n"
        "6. [Техзор](https://tehzor.com/)",
        reply_markup=reply_markup,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# Функция для обработки кнопки "Чат с искусственным интеллектом"
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["ai_chat"] = True
    keyboard = [["Выйти из режима ИИ"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Бот подключен к нейросети OpenAI. Для начала общения напишите пожалуйста Ваш запрос.",
        reply_markup=reply_markup
    )

# Функция для обработки сообщений в чате с AI
async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get("ai_chat"):
        if update.message.text == "Выйти из режима ИИ":
            context.user_data["ai_chat"] = False
            await update.message.reply_text(
                "Вы вышли из режима ИИ. Возвращаюсь в главное меню."
            )
            await start(update, context)
            return

        user_message = update.message.text
        try:
            # Отправляем запрос к OpenAI
            completion = client.chat.completions.create(
                model=model_chat_gpt,
                store=True,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            reply = completion.choices[0].message.content
            await update.message.reply_text(reply)
        except Exception as e:
            error_message = str(e)
            if "insufficient_quota" in error_message:
                await update.message.reply_text(
                    "Извините, превышен лимит использования API OpenAI. Пожалуйста, проверьте квоту или попробуйте позже."
                )
            else:
                print(f"Error: {e}")
                await update.message.reply_text(
                    "Произошла ошибка при обращении к AI. Попробуйте позже."
                )
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите 'Чат с искусственным интеллектом' для начала общения."
        )

# Функция для обработки кнопки "Назад"
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["ai_chat"] = False 
    await start(update, context)

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Навигатор по информационным системам$"), navigator))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Чат с искусственным интеллектом$"), ai_chat))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Назад$"), back_to_main))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Выйти из режима ИИ$"), handle_ai_chat))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.Regex("^(Навигатор|Чат с искусственным интеллектом|Назад|Выйти из режима ИИ)$"), handle_ai_chat))

    application.run_polling()

if __name__ == "__main__":
    main()
