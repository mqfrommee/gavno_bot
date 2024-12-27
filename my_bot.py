import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, CommandHandler, MessageHandler, ApplicationBuilder, CallbackQueryHandler, ContextTypes
from database import init_db, User

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

session = init_db()

jokes = [
    "Шутка 1: Я сам делал этого бота",
    "Шутка 2: Я бы трубку курил если бы был моряком",
    "Шутка 3: А шутки нету, время такое - несмешное"
]

facts = [
    "Факт 1: Цыганей никто нелюбитю",
    "Факт 2: Армяне придумали вселеннуюю",
    "Факт 3: Чем гуще лес - тем шкипиди доп ес ес"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Начать", callback_data='authorize')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Добро пожаловать! Нажмите кнопку ниже, чтобы начать.',
        reply_markup=reply_markup
    )

async def authorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    context.user_data['step'] = 'waiting_for_full_name'

    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='back_to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text('Введите свое ФИО:', reply_markup=reply_markup)

async def go_back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if 'step' not in context.user_data:
        keyboard = [
            [InlineKeyboardButton("Начать", callback_data='authorize')],
            [InlineKeyboardButton("Контактная информация", callback_data='contact')],
            [InlineKeyboardButton("Часто задаваемые вопросы", callback_data='faq')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('Добро пожаловать! Нажмите кнопку ниже, чтобы начать.', reply_markup=reply_markup)
        return

    context.user_data['step'] = None
    keyboard = [
        [InlineKeyboardButton("Просмотр БД", callback_data='view_db')],
        [InlineKeyboardButton("Ссылка на код", url='https://ewq-qigd.onrender.com/')], 
        [InlineKeyboardButton("Случайный прикол", callback_data='funny')],
        [InlineKeyboardButton("Часто задаваемые вопросы", callback_data='faq')],
        [InlineKeyboardButton("Контактная информация", callback_data='contact')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Выберите действие:', reply_markup=reply_markup)

async def contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    contact_text = """
    Контактная информация:
    - Email: qwerty@qwerty.com
    - Телефон: +56 9 1233 3952
    - Социальные сети:
      - GitHub: https://github.com/mqfrommee
      - Telegram: trebweb
    """
    
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='back_to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(contact_text, reply_markup=reply_markup)

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    faq_text = """
    Часто задаваемые вопросы:
    1. Как зарегистрироваться?
    - Никак, данной функции не существует.
    
    2. Как обновить свой номер телефона?
    - Свяжитесь с нашей поддержкой, и мы не поможем вам.

    3. Где найти помощь?
    - А нигде, пора бы уже самому проблемы решать:)
    """
    
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='back_to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(faq_text, reply_markup=reply_markup)
    

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    step = context.user_data.get('step')

    if step == 'waiting_for_full_name':
        user_full_name = update.message.text
        context.user_data['full_name'] = user_full_name
        context.user_data['step'] = 'waiting_for_phone_number'
        await update.message.reply_text('Красава! Теперь введите свой номер телефона.')

        keyboard = [
            [InlineKeyboardButton("Назад", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Введите свой номер телефона: +7XXXXXXXXXX', reply_markup=reply_markup)

    elif step == 'waiting_for_phone_number':
        user_phone_number = update.message.text

        if not user_phone_number.startswith('+7') or not user_phone_number[1:].isdigit() or len(user_phone_number) != 12:
            await update.message.reply_text('Ах ты крыса, решил меня опракинуть? Ты во мне лоха увидел?')
            return

        full_name = context.user_data.get('full_name')

        new_user = User(full_name=full_name, phone_number=user_phone_number)
        session.add(new_user)
        session.commit()

        context.user_data['step'] = None
        await update.message.reply_text('умничка! Теперь жди... докс, сват, деанон, ОМОН, ФБР, ФСБ, снайперов и т. д.')

        keyboard = [
            [InlineKeyboardButton("Просмотр БД", callback_data='view_db')],
            [InlineKeyboardButton("Ссылка на код", url='https://ewq-qigd.onrender.com/')], 
            [InlineKeyboardButton("Случайный прикол", callback_data='funny')],
            [InlineKeyboardButton("Часто задаваемые вопросы", callback_data='faq')],
            [InlineKeyboardButton("Контактная информация", callback_data='contact')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)

    else:
        await update.message.reply_text('Введите /start для начала.')

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'authorize':
        await authorize(update, context)

    elif query.data == 'back_to_start':
        await go_back_to_start(update, context)

    elif query.data == 'view_db':
        if 'step' not in context.user_data:
            await query.edit_message_text('Сначала авторизуйтесь.')
            return
        users = session.query(User).all()
        if users:
            response = "Данные пользователей:\n" + "\n".join([f"{u.id}: {u.full_name} - {u.phone_number}" for u in users])
        else:
            response = "База данных пуста."
        keyboard = [
            [InlineKeyboardButton("Назад", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(response, reply_markup=reply_markup)

    elif query.data == 'funny':
        random_joke = random.choice(jokes + facts)
        await query.edit_message_text(random_joke)

        keyboard = [
            [InlineKeyboardButton("Назад", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('Выберите действие:', reply_markup=reply_markup)

    elif query.data == 'contact':
        await contact_info(update, context)

    elif query.data == 'faq':
        await faq(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f'Update {update} caused error {context.error}')

def main():
    TOKEN = '7940254732:AAGAjvE1itjJnd9eQ7c5iCtVCo9Z_dNojnw'

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == '__main__':
    main()