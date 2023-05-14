import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
import requests

TOKEN = 'BOT-TOKEN'
bot = telegram.Bot(token=TOKEN)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Привет! Я бот, который может помочь тебе узнать среднюю зарплату по профессии в различных регионах. Напиши мне название профессии и региона через запятую')


def salary(update, context):
    text = update.message.text
    words = text.split(',')
    if len(words) != 2:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='Неверный формат запроса. Напиши название профессии и региона через пробел.')
        return
    profession = words[0]
    region = words[1]
    url = 'https://api.hh.ru/vacancies'
    params = {'text': profession, 'area': region}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        context.bot.send_message(chat_id=update.message.chat_id, text='Ошибка при получении данных с сайта hh.ru')
        return
    data = response.json()
    if data['found'] == 0:
        context.bot.send_message(chat_id=update.message.chat_id, text='По вашему запросу ничего не найдено')
        return
    salary_list = []
    for vacancy in data['items']:
        if vacancy['salary'] is not None:
            salary_from = vacancy['salary'].get('from')
            salary_to = vacancy['salary'].get('to')
            if salary_from is None:
                salary_from = 0
            if salary_to is None:
                salary_to = 0
            salary_list.append((salary_from + salary_to) / 2)
    if len(salary_list) == 0:
        context.bot.send_message(chat_id=update.message.chat_id, text='Нет данных о зарплате')
        return
    avg_salary = sum(salary_list) / len(salary_list)
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=f'Средняя зарплата по профессии "{profession}" в регионе "{region}" составляет {avg_salary:.2f} рублей')


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, salary))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("Running....")
    main()
