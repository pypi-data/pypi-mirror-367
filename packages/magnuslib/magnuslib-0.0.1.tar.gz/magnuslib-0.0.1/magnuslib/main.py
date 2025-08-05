

def retry(times, sec_):
    """декоратор для times-повторного выполнения функции при неудачном выполнении

    Args:
        times (_type_): попыток
        sec_ (_type_): секунд между попытками
    """

    def wrapper_fn(f):
        @wraps(f)
        def new_wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    print('---ПОПЫТКА ЧТЕНИЯ ФАЙЛА ---- %s' % (i + 1))
                    return f(*args, **kwargs)
                except Exception as e:
                    error = e
                    print(time.sleep(sec_))
            raise error

        return new_wrapper

    return wrapper_fn


@retry(10, 5)
def links_main(name_file, key, sep=';'):
    """функция для работы с путями, ссылки, вводные данные хранятся в блокноте

    Args:
        name_file (_type_): имя файла
        key (_type_): имя ключа
        sep (str): разделитель

    Returns:
        _type_: _description_
    """
    try:
        file = pd.read_csv(name_file, sep=sep)
        result = list(file[file['ключ'] == key]['значение'])[0]
        return result
    except Exception as ex_:
        print(
            f'ошибка функции {links_main.__name__} не удалось считать файл {name_file} или данные в нем {key} ошибка {ex_}')


def dir_link():
    """возвращает абсолютный путь в (.py .ipynp)
    """

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return script_dir
    except:
        script_dir_2 = os.getcwd()
        return script_dir_2


def yesterday(days: int = 1):
    """возвращает дату на вчера - по уморлчанию минус 1 день

    Args:
        days (int, optional): на сколько дней назад откатываемся по дате. Defaults to 1.

    Returns:
        _type_: _description_
    """

    try:

        date = datetime.now()
        new_date = date - timedelta(days=days)  # вычитание одного дня
        return new_date
    except Exception as ex_:
        print(f'ошибка функции {yesterday.__name__}  {ex_}')


def create_date(year, month):

    """
    Создает объект даты по году и месяцу.
  
    Args:
      year: Год (целое число).
      month: Месяц (целое число от 1 до 12).
  
    Returns:
      Объект datetime.date, представляющий первый день указанного месяца и года.
    """
    try:
        return date(year, month, 1)
    except Exception as ex_:
        print(f'ошибка функции {create_date.__name__}  {ex_}')


def converter_month_to_int(word, param='long' or 'short'):
    try:
        if param == 'short':
            word_ = word.lower()
            if 'янв' in word_:
                return 1
            elif 'фев' in word_:
                return 2
            elif 'мар' in word_:
                return 3
            elif 'апр' in word_:
                return 4
            elif 'май' in word_:
                return 5
            elif 'июн' in word_:
                return 6
            elif 'июл' in word_:
                return 7
            elif 'авг' in word_:
                return 8
            elif 'сен' in word_:
                return 9
            elif 'окт' in word_:
                return 10
            elif 'ноя' in word_:
                return 11
            elif 'дек' in word_:
                return 12
            else:
                return f'{word} не распознано'
        elif param == 'long':
            word_ = word.lower()
            if 'январь' in word_:
                return 1
            elif 'февраль' in word_:
                return 2
            elif 'мар' in word_:
                return 3
            elif 'апрель' in word_:
                return 4
            elif 'май' in word_:
                return 5
            elif 'июнь' in word_:
                return 6
            elif 'июль' in word_:
                return 7
            elif 'август' in word_:
                return 8
            elif 'сентябрь' in word_:
                return 9
            elif 'октябрь' in word_:
                return 10
            elif 'ноябрь' in word_:
                return 11
            elif 'декабрь' in word_:
                return 12
            else:
                return f'{word} не распознано'
        else:
            print(f'Не указан обязательный параметр функции - param (long or short)')
    except Exception as ex_:
            print(f'ошибка функции {converter_month_to_int.__name__}  {ex_}')


def last_day_of_month(year, month):

    """
    Возвращает последний день указанного месяца и года.
  
    Args:
      year: Год.
      month: Месяц (1-12).
  
    Returns:
      Последний день месяца.
    """
    try:
        return calendar.monthrange(year, month)[1]
    except Exception as ex_:
        print(f'ошибка функции {last_day_of_month.__name__}  {ex_}')


def convert_str_to_datetime(year, month, day):
    """конвертирует str date в datetime

    Args:
        year (_type_): _description_
        month (_type_): _description_
        day (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:

        date_object = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()
        return date_object
    except Exception as ex_:
        print(f'ошибка функции {convert_str_to_datetime.__name__}  {ex_}')


def date_start_stop(year, month):
    """возвращает начало и конец периода в формате YYYY-MM-DD

    Args:
        year (int): _description_
        month (int): _description_

    Returns:
        tuple(date:str, date:str): ('2025-07-01', '2025-07-31')
    """
    try:
        start_date = create_date(year, month)
        start_date_ret = f'{start_date.year}-{"0" + str(start_date.month) if len(str(start_date.month)) == 1 else start_date.month}-{"0" + str(start_date.day) if len(str(start_date.day)) == 1 else start_date.day}'

        end_day = last_day_of_month(year, month)
        end_date = f'{start_date.year}-{"0" + str(start_date.month) if len(str(start_date.month)) == 1 else start_date.month}-{"0" + str(end_day) if len(str(end_day)) == 1 else end_day}'

        return start_date_ret, end_date
    except Exception as ex_:
        print(f'ошибка функции {date_start_stop.__name__}  {ex_}')


def pred_month():
    """функция возвращает даты на начало и конец предыдущего месяца

    Returns:
        _type_: _description_
    """
    try:
        previous_month_date = datetime.now() + relativedelta(months=-1)
        first_date_pred_month = f'{previous_month_date.year}-{"0" + str(previous_month_date.month) if len(str(previous_month_date.month)) == 1 else previous_month_date.month}-{"01"}'
        last_day = last_day_of_month(previous_month_date.year, previous_month_date.month)
        last_date_pred_month = f'{previous_month_date.year}-{"0" + str(previous_month_date.month) if len(str(previous_month_date.month)) == 1 else previous_month_date.month}-{"0" + str(last_day) if len(str(last_day)) == 1 else last_day}'
        return first_date_pred_month, last_date_pred_month
    except Exception as ex_:
        print(f'ошибка функции {pred_month.__name__}  {ex_}')


def update_file(link: str, sleep_: int = 30):
    """обновление сводной таблицы Excel
    # блок импортов для обновления сводных
    import pythoncom
    pythoncom.CoInitializeEx(0)
    import win32com.client
    Args:
        link (_type_): ссылка на файл - который нужно обновить
        sleep_(int): задержка в сек на обновление сводной таблицы
    """
    try:
        xlapp = win32com.client.DispatchEx("Excel.Application")
        wb = xlapp.Workbooks.Open(link)
        wb.Application.AskToUpdateLinks = False  # разрешает автоматическое  обновление связей (файл - парметры - дополнительно - общие - убирает галку запрашивать об обновлениях связей)
        wb.Application.DisplayAlerts = True  # отображает панель обновления иногда из-за перекрестного открытия предлагает ручной выбор обновления True - показать панель
        wb.RefreshAll()
        # xlapp.CalculateUntilAsyncQueriesDone() # удержит программу и дождется завершения обновления. было прописано time.sleep(30)
        time.sleep(sleep_)  # задержка 60 секунд, чтоб уж точно обновились сводные wb.RefreshAll() - иначе будет ошибка
        wb.Application.AskToUpdateLinks = True  # запрещает автоматическое  обновление связей / то есть в настройках экселя (ставим галку обратно)
        wb.Save()
        wb.Close()
        xlapp.Quit()
        wb = None  # обнуляем сслыки переменных иначе процесс эксель не завершается и висит в дистпетчере
        xlapp = None  # обнуляем сслыки переменных иначе процесс эксел ь не завершается и висит в дистпетчере
        del wb  # удаляем сслыки переменных иначе процесс эксель не завершается и висит в дистпетчере
        del xlapp  # удаляем сслыки переменных иначе процесс эксель не завершается и висит в дистпетчере
    except Exception as ex_:
        print(f'ошибка функции {update_file.__name__} {ex_} не удалось обновить файл по ссылке {link}')


def send_mail(SEND_FROM: str, SERVER: str, PORT: int, USER_NAME: str, PASSWORD: str, send_to: list, file_link: str,
              file_name: str, them: str = '', body: str = ''):
    """рассылка почты

    # блок импорта отправки почты - необходимые библиотеки
    import smtplib,ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.utils import formatdate
    from email import encoders

    Args:
        SEND_FROM (str): от кого
        SERVER (str): имя сервера
        PORT (int): обозначение порта
        USER_NAME (str): имя пользователя в системе
        PASSWORD (str): пароль пользователя в системе
        send_to (list): список адресов для рассылки
        file_link(str): ссылка на файл
        file_name(str): имя файла в данном варианте нужно указывать с расширением 'BAIC_MSK.xlsx' or 'file.txt' and ....
        them(str) - тема письма
        body(str) - тело письма

    prim:
        send_mail('xxxxxx@xxxx.ru'
        'server-vm20.XXL.LOCAL',
        555,
        'skrutko',
        'XXXZZZpoew11o',
        ['xxxxxx@xxxx.ru', 'zzzzzzzx@xxxx.ru'],
        'C:index_road.xlsx',
        'email_adress.xlsx',
        'Индекс РОАД',
        'Здравствуйте во вложении файл ......')

    """
    from datetime import datetime, date, timedelta

    try:
        send_from = SEND_FROM
        subject = f"{them}"
        text = f"{body}"
        files = fr'{file_link.strip()}'
        server = SERVER
        port = PORT
        username = USER_NAME
        password = PASSWORD
        isTls = True

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = ','.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(text))

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(files, "rb").read())
        encoders.encode_base64(part)

        part.add_header('Content-Disposition',
                        f'attachment; filename={file_name.strip()}')  # имя файла должно быть на латинице иначе придет в кодировке bin
        msg.attach(part)

        smtp = smtplib.SMTP(server, port)
        if isTls:
            smtp.starttls()
        smtp.login(username, password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()

    except Exception as ex_:
        print(
            f'ошибка функции {send_mail.__name__} {ex_} входне параметры {SEND_FROM, SERVER, PORT, USER_NAME, PASSWORD, send_to, file_link, file_name, them, body}')


