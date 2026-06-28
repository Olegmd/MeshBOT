from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import database as db

# ⚠️ ВСТАВЬ СЮДА СВОЙ ТОКЕН от @BotFather
TOKEN = "8455376964:AAFOoiKso7kkh3w_2sGq1S7vRvDgfaCDlG8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# МЕНЮ КОФЕЙНИ
MENU = {
    "espresso": {"name": "Эспрессо", "price": 150},
    "americano": {"name": "Американо", "price": 180},
    "cappuccino": {"name": "Капучино", "price": 220},
    "latte": {"name": "Латте", "price": 250},
    "raff": {"name": "Раф", "price": 280},
    "flat_white": {"name": "Флэт Уайт", "price": 260},
}

# Главное меню
def main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="☕ Меню", callback_data="menu")],
        [InlineKeyboardButton(text="📊 Мои бонусы", callback_data="bonus")],
        [InlineKeyboardButton(text="📍 Контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="about")],
    ])
    return keyboard

# Меню с напитками
def menu_keyboard():
    buttons = []
    for key, item in MENU.items():
        buttons.append([InlineKeyboardButton(
            text=f"{item['name']} - {item['price']}₽",
            callback_data=f"order_{key}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    # Регистрируем пользователя
    db.get_or_create_user(message.from_user.id, message.from_user.username)
    
    await message.answer(
        f"Привет, {message.from_user.first_name}! ☕\n\n"
        f"Добро пожаловать в CoffeeBot!\n"
        f"У нас вы можете заказать кофе и копить бонусы.\n"
        f"Каждый 10-й кофе — бесплатно! 🎁\n\n"
        f"Выберите действие:",
        reply_markup=main_menu()
    )

# Обработка кнопок
@dp.callback_query(F.data == "menu")
async def show_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "☕ Наше меню:\n\nВыберите напиток:",
        reply_markup=menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("order_"))
async def order_item(callback: types.CallbackQuery):
    item_key = callback.data.split("_")[1]
    item = MENU[item_key]
    
    # Сохраняем заказ
    got_bonus = db.add_order(callback.from_user.id, item['name'], item['price'])
    
    text = f"✅ Заказ принят!\n\n{item['name']} - {item['price']}₽\n\n"
    
    if got_bonus:
        text += "🎉 ПОЗДРАВЛЯЕМ! Вы получили бесплатный кофе! 🎁\n"
    
    text += "Мы уже готовим ваш заказ. Ожидайте 5-10 минут.\n\nСпасибо, что выбираете нас! ❤️"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer("Заказ оформлен! ✅")

@dp.callback_query(F.data == "bonus")
async def show_bonus(callback: types.CallbackQuery):
    bonus_points, total_orders = db.get_user_stats(callback.from_user.id)
    
    await callback.message.edit_text(
        f"📊 Ваша статистика:\n\n"
        f"☕ Заказов всего: {total_orders}\n"
        f"🎁 Бонусных баллов: {bonus_points}\n"
        f"🆓 Бесплатных кофе: {total_orders // 10}\n\n"
        f"До следующего бесплатного кофе: {10 - (total_orders % 10)} заказов",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "contacts")
async def show_contacts(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📍 Наши контакты:\n\n"
        "🏠 Адрес: ул. Примерная, д. 123\n"
        "📞 Телефон: +7 (999) 123-45-67\n"
        "🕐 Режим работы: 8:00 - 22:00\n\n"
        "📱 Instagram: @coffee_example\n"
        "💬 Telegram: @coffee_example",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def show_about(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ О нашей кофейне:\n\n"
        "Мы варим лучший кофе в городе с 2020 года!\n"
        "Используем только свежую обжарку и качественное молоко.\n\n"
        "🌟 Наши преимущества:\n"
        "• Зёрна собственной обжарки\n"
        "• Альтернативное молоко бесплатно\n"
        "• Программа лояльности\n"
        "• Быстрое обслуживание",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите действие:",
        reply_markup=main_menu()
    )
    await callback.answer()

# Запуск бота
async def main():
    print("Бот запущен! 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
