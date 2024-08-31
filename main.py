import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

#логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    filename='bot_logs.log',
)

logger = logging.getLogger(__name__)

# словарь с голосами
votes = {}
vote_threshold = 5  # количество голосов для бана, я бы сделал больше


# типикал старт
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Привет! Если вы хотите забанить пользователя, ответьте на его сообщение с текстом '@ban'. Бот уведомит, когда будет набрано 5 голосов.")
    logger.info(f"Бот запущен в чате {update.message.chat_id} участником {update.message.from_user.username}")


# Функция для голосования
async def vote_for_ban(update: Update, context: CallbackContext) -> None:
    logger.debug("Обработка сообщения для голосования.")

    replied_message = update.message.reply_to_message

    if not replied_message:
        logger.debug("Не найдено ответное сообщение. Сообщение с @ban не является ответом.")
        return

    if "@ban" in update.message.text.lower():
        user_to_ban = replied_message.from_user.username
        chat_id = update.message.chat_id

        if chat_id not in votes:
            votes[chat_id] = {}

        if user_to_ban in votes[chat_id]:
            votes[chat_id][user_to_ban] += 1
        else:
            votes[chat_id][user_to_ban] = 1

        logger.info(
            f"Голос за бан пользователя @{user_to_ban}. Текущее количество голосов: {votes[chat_id][user_to_ban]}")

        if votes[chat_id][user_to_ban] >= vote_threshold:
            try:
                # сопсно сам бан
                await context.bot.ban_chat_member(chat_id, replied_message.from_user.id)
                await update.message.reply_text(
                    f"Пользователь @{user_to_ban} был забанен после получения {vote_threshold} голосов.")
                logger.info(f"Пользователь @{user_to_ban} был забанен в чате {chat_id}")

                # снести пост, за который голосовали
                await context.bot.delete_message(chat_id, replied_message.message_id)
                logger.info(f"Сообщение пользователя @{user_to_ban} было удалено.")

                del votes[chat_id][user_to_ban]
            except Exception as e:
                logger.error(f"Ошибка при попытке бана пользователя @{user_to_ban}: {e}")
                await update.message.reply_text(
                    f"Не удалось забанить пользователя @{user_to_ban}. Проверьте права бота.")
    else:
        logger.debug("'@ban' не найдено в тексте сообщения.")


def main():
    application = Application.builder().token("сюда ткнуть полученный токен для бота").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, vote_for_ban))

    logger.info("Бот запущен и готов к работе.")
    application.run_polling()


if __name__ == '__main__':
    main()
