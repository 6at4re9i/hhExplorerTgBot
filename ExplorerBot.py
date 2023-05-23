import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
import requests


TOKEN = 'YOUR_BOT_TOKEN'
bot = telegram.Bot(token=TOKEN)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Привет! Я бот, который может помочь тебе узнать среднюю зарплату по профессии в различных регионах. Напиши мне название профессии и региона через запятую')


def salary(update, context):
    text = update.message.text
    words = text.split(', ')
    if len(words) != 2:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='Неверный формат запроса. Напиши название профессии и региона через запятую.')
        return
    profession = words[0]
    user_region = words[1]
    territory = 0
    response1 = requests.get('https://api.hh.ru/areas')
    regions = response1.json()
    areas = []
    for region in regions:
        for i in range(len(region['areas'])):
            if len(region['areas'][i]['areas']) != 0 and (region['id'] == '113'):
                for j in range(len(region['areas'][i]['areas'])):
                    areas.append([region['areas'][i]['areas'][j]['id'],
                                  region['areas'][i]['areas'][j]['name']])
            if len(region['areas'][i]['areas']) == 0 and (region['id'] == '113'):
                areas.append([region['areas'][i]['id'],
                              region['areas'][i]['name']])
    for area in areas:
        if user_region == area[1]:
            territory = area[0]

    all_salaries = []
    params = {'text': profession, 'only_with_salary': True, 'area': territory}
    response2 = requests.get('https://api.hh.ru/vacancies', params=params)
    if response2.status_code != 200:
        context.bot.send_message(chat_id=update.message.chat_id, text="Ошибка при получении данных с сайта hh.ru")
        return

    i = 0
    if response2.ok:
        vacancies = response2.json()
        for vacancy in vacancies['items']:
            salary = vacancy['salary']
            if salary:
                if salary['currency'] == 'RUR':
                    if salary['from'] is None:
                        salary['from'] = 0
                        i += 1
                    if salary['to'] is None:
                        salary['to'] = 0
                        i += 1
                    all_salaries.append(salary['from'] + salary['to'])

    if i <= 0:
        context.bot.send_message(chat_id=update.message.chat_id, text=f'Невозможно получить данные по профессии "{profession}" в регионе "{user_region}".')

    average_salary = (sum(all_salaries) / (2 * len(all_salaries) - i))
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=f'Средняя зарплата по профессии "{profession}" в регионе "{user_region}" составляет {average_salary:.0f} рублей')


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
    
