# bot.py
"""
Главный файл телеграм-бота для обработки точек на плоскости.
Использует те же модули, что и консольное приложение.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler
)

# Загружаем переменные окружения
load_dotenv()

# Импортируем модули из консольного приложения
from exceptions import (
    InvalidInputFormatException, 
    InvalidNumberException, 
    EmptyPointsListException,
    InsufficientPointsException,
    InvalidMethodException
)
from input_data import input_by_hand, make_random_points
from points import process_points

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
(
    MAIN_MENU,
    INPUT_CHOICE,
    MANUAL_INPUT,
    RANDOM_INPUT,
    PROCESS_METHOD,
    VIEW_RESULTS
) = range(6)

# Константы для callback данных
CALLBACK_INPUT_MANUAL = "input_manual"
CALLBACK_INPUT_RANDOM = "input_random"
CALLBACK_BACK = "back"
CALLBACK_COMPARE = "compare"
CALLBACK_EXIT = "exit"

@dataclass
class UserData:
    """Класс для хранения данных пользователя между состояниями."""
    user_id: int
    points: list = field(default_factory=list)
    method: Optional[str] = None
    result: Optional[list] = None
    current_input: str = ""  # Для накопления ввода
    
    def clear(self):
        """Очистить данные пользователя."""
        self.points.clear()
        self.method = None
        self.result = None
        self.current_input = ""

# Глобальный словарь для хранения данных пользователей
user_data_store: Dict[int, UserData] = {}

# Словарь методов обработки
METHODS_MAP = {
    '1': ('original', 'Оригинальный (ближайшая)'),
    '2': ('sequential', 'Последовательный'),
    '3': ('min_sum', 'Минимальная сумма'),
    '4': ('min_x', 'Минимальный X')
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start - точка входа в бота."""
    user_id = update.effective_user.id
    
    # Инициализируем или очищаем данные пользователя
    if user_id in user_data_store:
        user_data_store[user_id].clear()
    else:
        user_data_store[user_id] = UserData(user_id=user_id)
    
    await show_main_menu(update, context)
    return MAIN_MENU

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать главное меню."""
    keyboard = [
        [InlineKeyboardButton("📝 Обработать точки", callback_data="process")],
        [InlineKeyboardButton("📊 Сравнить все методы", callback_data=CALLBACK_COMPARE)],
        [InlineKeyboardButton("❌ Выход", callback_data=CALLBACK_EXIT)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "🤖 *АВТОМАТНОЕ ПРОГРАММИРОВАНИЕ*\n"
        "📐 *ОБРАБОТКА ТОЧЕК НА ПЛОСКОСТИ*\n\n"
        "Выберите действие:"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик выбора в главном меню."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id)
    
    if not user_data:
        await start(update, context)
        return MAIN_MENU
    
    choice = query.data
    
    if choice == "process":
        await show_input_menu(update, context)
        return INPUT_CHOICE
    elif choice == CALLBACK_COMPARE:
        await compare_methods(update, context)
        return MAIN_MENU
    elif choice == CALLBACK_EXIT:
        await query.edit_message_text("👋 До свидания!")
        return ConversationHandler.END
    
    return MAIN_MENU

async def show_input_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать меню ввода точек."""
    keyboard = [
        [InlineKeyboardButton("✍️ Ручной ввод", callback_data=CALLBACK_INPUT_MANUAL)],
        [InlineKeyboardButton("🎲 Случайная генерация", callback_data=CALLBACK_INPUT_RANDOM)],
        [InlineKeyboardButton("⬅️ Назад", callback_data=CALLBACK_BACK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "📝 *ВВОД ТОЧЕК*\n\n"
        "Формат точки: *x,y*\n"
        "Пример: *3.5,-2*\n\n"
        "Выберите способ ввода:"
    )
    
    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def input_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик выбора в меню ввода."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id)
    
    if not user_data:
        await start(update, context)
        return MAIN_MENU
    
    choice = query.data
    
    if choice == CALLBACK_INPUT_MANUAL:
        await show_manual_input_instructions(update, context)
        return MANUAL_INPUT
    elif choice == CALLBACK_INPUT_RANDOM:
        await show_random_input_menu(update, context)
        return RANDOM_INPUT
    elif choice == CALLBACK_BACK:
        await show_main_menu(update, context)
        return MAIN_MENU
    
    return INPUT_CHOICE

async def show_manual_input_instructions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать инструкции для ручного ввода."""
    user_id = update.effective_user.id
    user_data = user_data_store[user_id]
    user_data.clear()  # Очищаем предыдущие точки
    
    message = (
        "✍️ *РУЧНОЙ ВВОД ТОЧЕК*\n\n"
        "Вводите точки в формате: *x,y*\n"
        "Примеры:\n"
        "• *3,4*\n"
        "• *-1.5,2.7*\n"
        "• *0,-3*\n\n"
        "📌 *Команды:*\n"
        "• /done - завершить ввод\n"
        "• /cancel - отменить ввод\n"
        "• /clear - очистить все точки\n\n"
        "Введите первую точку:"
    )
    
    await update.callback_query.edit_message_text(
        text=message,
        parse_mode='Markdown'
    )

async def handle_manual_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик ручного ввода точек."""
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id)
    
    if not user_data:
        await start(update, context)
        return MAIN_MENU
    
    text = update.message.text.strip()
    
    # Обработка команд
    if text.lower() in ['/done', 'готово', 'стоп']:
        if not user_data.points:
            await update.message.reply_text("❌ Не введено ни одной точки!")
            return MANUAL_INPUT
        
        await update.message.reply_text(
            f"✅ Введено точек: {len(user_data.points)}\n"
            f"Точки: {user_data.points}\n\n"
            "Переходим к выбору метода обработки..."
        )
        await show_method_menu(update, context)
        return PROCESS_METHOD
    
    elif text.lower() in ['/cancel', 'отмена']:
        user_data.clear()
        await update.message.reply_text("❌ Ввод отменен.")
        await show_main_menu(update, context)
        return MAIN_MENU
    
    elif text.lower() in ['/clear', 'очистить']:
        user_data.points.clear()
        await update.message.reply_text("🗑 Все точки очищены. Введите первую точку:")
        return MANUAL_INPUT
    
    # Парсинг точки
    try:
        parts = text.split(',')
        if len(parts) != 2:
            raise InvalidInputFormatException(text)
        
        try:
            x = float(parts[0].strip())
        except ValueError:
            raise InvalidNumberException(parts[0], "координата X")
        
        try:
            y = float(parts[1].strip())
        except ValueError:
            raise InvalidNumberException(parts[1], "координата Y")
        
        user_data.points.append((x, y))
        
        await update.message.reply_text(
            f"✅ Добавлена точка: ({x}, {y})\n"
            f"Всего точек: {len(user_data.points)}\n\n"
            "Введите следующую точку или /done для завершения:"
        )
        
    except (InvalidInputFormatException, InvalidNumberException) as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    except Exception as e:
        await update.message.reply_text(f"❌ Неожиданная ошибка: {e}")
    
    return MANUAL_INPUT

async def show_random_input_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать меню для случайной генерации."""
    message = (
        "🎲 *СЛУЧАЙНАЯ ГЕНЕРАЦИЯ ТОЧЕК*\n\n"
        "Введите количество точек для генерации (от 1 до 20):\n\n"
        "Или используйте команды:\n"
        "• /cancel - отменить\n"
        "• /default - создать 5 точек"
    )
    
    await update.callback_query.edit_message_text(
        text=message,
        parse_mode='Markdown'
    )

async def handle_random_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик случайной генерации точек."""
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id)
    
    if not user_data:
        await start(update, context)
        return MAIN_MENU
    
    text = update.message.text.strip()
    
    # Обработка команд
    if text.lower() in ['/cancel', 'отмена']:
        await update.message.reply_text("❌ Генерация отменена.")
        await show_main_menu(update, context)
        return MAIN_MENU
    
    elif text.lower() in ['/default', 'по умолчанию']:
        n = 5
    else:
        try:
            n = int(text)
            if n <= 0:
                raise ValueError("Количество должно быть положительным")
            if n > 20:
                await update.message.reply_text("⚠️ Создано максимум 20 точек для читаемости.")
                n = 20
        except ValueError as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
            return RANDOM_INPUT
    
    # Генерация точек
    try:
        user_data.clear()
        user_data.points = make_random_points(n)
        
        # Для бота переопределяем функцию вывода
        points_str = "\n".join([f"({x}, {y})" for x, y in user_data.points])
        
        await update.message.reply_text(
            f"✅ Создано {n} случайных точек:\n\n"
            f"{points_str}\n\n"
            "Переходим к выбору метода обработки..."
        )
        
        await show_method_menu(update, context)
        return PROCESS_METHOD
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка генерации: {e}")
        return RANDOM_INPUT

async def show_method_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать меню выбора метода обработки."""
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id)
    
    if not user_data or not user_data.points:
        await update.message.reply_text("❌ Нет точек для обработки!")
        await show_main_menu(update, context)
        return
    
    # Создаем клавиатуру с методами
    keyboard = []
    for key, (_, name) in METHODS_MAP.items():
        keyboard.append([InlineKeyboardButton(f"{key}. {name}", callback_data=f"method_{key}")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=CALLBACK_BACK)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "⚙️ *ВЫБОР МЕТОДА ОБРАБОТКИ*\n\n"
        f"Доступно точек: {len(user_data.points)}\n"
        "Выберите метод обработки:"
    )
    
    # Проверяем откуда пришел запрос
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def method_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик выбора метода."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id)
    
    if not user_data:
        await start(update, context)
        return MAIN_MENU
    
    choice = query.data
    
    if choice == CALLBACK_BACK:
        await show_input_menu(update, context)
        return INPUT_CHOICE
    
    if choice.startswith("method_"):
        method_key = choice.split("_")[1]
        
        if method_key not in METHODS_MAP:
            await query.edit_message_text("❌ Неизвестный метод!")
            return PROCESS_METHOD
        
        method_code, method_name = METHODS_MAP[method_key]
        user_data.method = method_code
        
        # Обрабатываем точки
        try:
            user_data.result = process_points(user_data.points, method_code)
            await show_results(update, context)
            return VIEW_RESULTS
            
        except (EmptyPointsListException, InsufficientPointsException, InvalidMethodException) as e:
            await query.edit_message_text(f"❌ Ошибка обработки: {e}")
            return PROCESS_METHOD
        except Exception as e:
            await query.edit_message_text(f"❌ Неожиданная ошибка: {e}")
            return PROCESS_METHOD
    
    return PROCESS_METHOD

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать результаты обработки."""
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id)
    
    if not user_data or not user_data.result:
        await update.callback_query.edit_message_text("❌ Нет результатов для отображения!")
        await show_main_menu(update, context)
        return
    
    # Словарь для красивых названий методов
    method_names = {
        'original': 'Оригинальный',
        'sequential': 'Последовательный',
        'min_sum': 'Минимальная сумма',
        'min_x': 'Минимальный X'
    }
    
    # Форматируем точки для читаемости
    points_str = "\n".join([f"({x}, {y})" for x, y in user_data.points])
    result_str = "\n".join([f"({x}, {y})" for x, y in user_data.result])
    
    message = (
        "📊 *РЕЗУЛЬТАТЫ ОБРАБОТКИ*\n\n"
        f"*Метод:* {method_names.get(user_data.method, user_data.method)}\n\n"
        f"*Исходные точки ({len(user_data.points)}):*\n"
        f"```\n{points_str}\n```\n\n"
        f"*Результат ({len(user_data.result)}):*\n"
        f"```\n{result_str}\n```"
    )
    
    keyboard = [
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
        [InlineKeyboardButton("🔄 Другой метод", callback_data="another_method")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def results_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик действий с результатами."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id)
    
    if not user_data:
        await start(update, context)
        return MAIN_MENU
    
    choice = query.data
    
    if choice == "main_menu":
        await show_main_menu(update, context)
        return MAIN_MENU
    elif choice == "another_method":
        await show_method_menu(update, context)
        return PROCESS_METHOD
    
    return VIEW_RESULTS

async def compare_methods(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сравнение всех методов обработки."""
    query = update.callback_query
    user_id = update.effective_user.id
    user_data = user_data_store.get(user_id)
    
    if not user_data or not user_data.points:
        await query.edit_message_text("❌ Нет точек для сравнения!")
        await show_main_menu(update, context)
        return
    
    message = "📊 *СРАВНЕНИЕ ВСЕХ МЕТОДОВ*\n\n"
    
    for method_key, (method_code, method_name) in METHODS_MAP.items():
        try:
            result = process_points(user_data.points, method_code)
            # Ограничиваем вывод для читаемости
            result_preview = str(result[:3]) + ("..." if len(result) > 3 else "")
            message += f"*{method_name}:*\n"
            message += f"Результат: `{result_preview}`\n"
            message += f"Количество: {len(result)}\n\n"
        except Exception as e:
            message += f"*{method_name}:*\n"
            message += f"Ошибка: {e}\n\n"
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data=CALLBACK_BACK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик отмены/выхода."""
    user_id = update.effective_user.id
    if user_id in user_data_store:
        user_data_store[user_id].clear()
    
    await update.message.reply_text("👋 До свидания!")
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    help_text = (
        "🤖 *Помощь по боту обработки точек*\n\n"
        "*Команды:*\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n"
        "/cancel - отменить текущее действие\n\n"
        "*Формат точек:*\n"
        "• Вводите точки в формате: *x,y*\n"
        "• Пример: *3.5,-2*\n"
        "• Десятичный разделитель: точка\n\n"
        "*Доступные методы обработки:*\n"
        "1. Оригинальный - складывает каждую точку с ближайшей к ней\n"
        "2. Последовательный - складывает точки попарно по порядку\n"
        "3. Минимальная сумма - складывает с точкой, имеющей минимальную сумму координат\n"
        "4. Минимальный X - складывает с точкой, имеющей минимальный X\n\n"
        "Для начала работы введите /start"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main() -> None:
    """Главная функция для запуска бота."""
    # Получаем токен из переменных окружения
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
    
    # Создаем приложение
    application = Application.builder().token(token).build()
    
    # Создаем ConversationHandler для управления состояниями
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(main_menu_handler)
            ],
            INPUT_CHOICE: [
                CallbackQueryHandler(input_menu_handler)
            ],
            MANUAL_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_input),
                CommandHandler("done", lambda u, c: handle_manual_input(u, c)),
                CommandHandler("cancel", cancel),
                CommandHandler("clear", lambda u, c: handle_manual_input(u, c))
            ],
            RANDOM_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_random_input),
                CommandHandler("cancel", cancel),
                CommandHandler("default", lambda u, c: handle_random_input(u, c))
            ],
            PROCESS_METHOD: [
                CallbackQueryHandler(method_handler)
            ],
            VIEW_RESULTS: [
                CallbackQueryHandler(results_handler)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("help", help_command),
            CommandHandler("start", start)
        ],
    )
    
    # Добавляем обработчики
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    
    # Запускаем бота
    print("🤖 Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()