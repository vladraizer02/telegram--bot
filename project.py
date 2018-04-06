from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import requests


def start(bot, update):
    update.message.reply_text("Добро пожаловать! Вас приветствует Бот-справочник по организациям в городах!")
    update.message.reply_text('Введите пожалуйста название населённого пункта, в котором вы хотите найти какую-либо организацию.')
    return 1


def first_response(bot, update, user_data):
    sity = update.message.text
    user_data['sity'] = sity
    update.message.reply_text('Какие организации поискать?')
    return 2


def poisk_organiz(bot, update, user_data):
    organization = update.message.text
    user_data['organization'] = organization
    update.message.reply_text('Ищем...')

    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "3c4a592e-c4c0-4949-85d1-97291c87825c"
    sity = user_data['sity']

    search_params = {
        "apikey": api_key,
        "text": sity+','+organization,
        "lang": "ru_RU",
        "type": "biz"
    }

    try:
        response = requests.get(search_api_server, params=search_params)
        if response:
            pass
        else:
            update.message.reply_text("Ошибка выполнения запроса:")
            update.message.reply_text(search_api_server)
            update.message.reply_text("Http статус:", response.status_code, "(", response.reason, ")")
            update.message.reply_text('Перезапустите бота командой /start')
            return ConversationHandler.END
    except:
        update.message.reply_text("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
        update.message.reply_text('Перезапустите бота командой /start')
        return ConversationHandler.END

        update.message.reply_text('Ничего не найдено, по вашему запросу. Для перезапуска бота, напишите, пожалуйста /start')
        return ConversationHandler.END

    json_response = response.json()

    try:
        coord_x = json_response["features"][0]["geometry"]['coordinates'][0]
        coord_y = json_response["features"][0]["geometry"]['coordinates'][1]
        organization1 = json_response["features"][0]["properties"]["CompanyMetaData"]
    except:
        update.message.reply_text('Ничего не найдено, по вашему запросу. Для перезапуска бота, напишите, пожалуйста /start')
        return ConversationHandler.END

    user_data['coord_x'] = coord_x
    user_data['coord_y'] = coord_y
    user_data['organization1'] = organization1
    update.message.reply_text('Найдена организация:')
    update.message.reply_text(organization1["name"])
    update.message.reply_text('Пишите нам свои вопросы, насчёт этой организации.')
    return 3


def info_response(bot, update, user_data):
    organization1 = user_data['organization1']
    answer = update.message.text

    try:
        if 'телефон' in answer.lower():
            update.message.reply_text(organization1['Phones'][0]['formatted'])
        elif 'адрес' in answer.lower():
            update.message.reply_text(organization1['address'])
        elif 'индекс' in answer.lower():
            update.message.reply_text(organization1['postalCode'])
        elif 'расписание' in answer.lower():
            update.message.reply_text(organization1['Hours']['text'])
        elif 'открыта' in answer.lower():
            if organization1['Hours']['State']['is_open_now'] == '0':
                update.message.reply_text('Закрыто')
            else:
                update.message.reply_text('Открыто')
        elif 'сайт' in answer.lower():
            update.message.reply_text(organization1['url'])
        elif 'карта' in answer.lower():
            coord_x = user_data['coord_x']
            coord_y = user_data['coord_y']
            static_api_requests = "http://static-maps.yandex.ru/1.x/?ll="+str(coord_x)+','+str(coord_y)+"&spn=0.01,0.01&l=map&pt="+str(coord_x)+','+str(coord_y)
            bot.sendPhoto(chat_id=update.message.chat_id, photo=static_api_requests)
        elif 'смена' in answer.lower():
            update.message.reply_text('Введите пожалуйста название населённого пункта, в котором вы хотите найти каккую-либо организацию.')
            return 1
        else:
            update.message.reply_text('У нас нет такого критерия поиска. Напишите коианду /help чтобы узнать критерии поиска')
    except:
        update.message.reply_text('Нет информации об этом')
    return 3


def stop(bot, update):
    update.message.reply_text("Всего самого наилучшего!!!")
    return ConversationHandler.END


def help(bot, update):
    update.message.reply_text("Для того чтобы я правильно понял ваш вопрос, нужно в своих вопросах использовать опорные слова, такие как:")
    update.message.reply_text('Телефон(напишу вам телефон данной организации),')
    update.message.reply_text('Адрес(напишу вам адрес данной организации),')
    update.message.reply_text('Индекс(напишу вам почтовый индекс данной организации),')
    update.message.reply_text('Расписание(напишу вам дни и время работы данной организации),')
    update.message.reply_text('Открыта(напишу вам открыта или же закрыта данная организация),')
    update.message.reply_text('Сайт(напишу вам сайт данной организации),')
    update.message.reply_text('Карта(отправлю вам карту, на которой будет метка данной организации).')
    update.message.reply_text('Смена(поменяем город для поиска организации).')


def main():
    updater = Updater("517314390:AAFFULrK4rJlphQ_Jr5Da2IpY8hByKppdLw")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            1: [MessageHandler(Filters.text, first_response, pass_user_data=True)],
            2: [MessageHandler(Filters.text, poisk_organiz, pass_user_data=True)],
            3: [MessageHandler(Filters.text, info_response, pass_user_data=True)]
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    dp.add_handler(conv_handler)

    print("bot started...")

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()