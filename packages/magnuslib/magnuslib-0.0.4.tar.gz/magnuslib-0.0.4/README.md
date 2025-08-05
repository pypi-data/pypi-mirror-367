# Набор некоторых функций которые будут становиться лучше

### Модули которые могут потребоваться
    import pandas, pywin32, openpyxl

### `links_main()`
Функция: для работы с путями, ссылки, вводные данные хранятся в блокноте
имеют 2 поля (пример текстового блокнота ниже):

ключ;значение       
server;local/32/rut     
pass;111

вызов функции `links_main('ключ', 'значение', 'f_links.txt', 'server', sep=';')` **return** `111`

    
    links_main(name_column_key, name_column_result, name_file, key, sep=';')

### `dir_link()`
Функция : возвращает полный путь к директории
работает в `.py .ipynb` **return**
`*C:\Users\sergey_krutko\PycharmProjects\magnuslb\magnuslib*`

    dir_link()

### `yesterday()`
Функция : возвращает дату на вчера - по уморлчанию минус 1 день, можно регулировать +.-
**result** `2025-08-04 00:01:51.921337` format `datetime`

    yesterday() # или yesterday(5)


    



    
