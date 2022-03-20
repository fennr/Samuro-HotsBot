# SamuroBot for Heroes of the Storm

## Authors

 **[fennr (@fennr)](fennr.github.io/)**

## Links

На случай выхода патча ссылки для обновления json файлов

 **[heroesdata](https://github.com/HeroesToolChest/heroes-data/tree/master/heroesdata)**
### Автоматическое обновление
* Обновить в конфиге номер текущего патча > config.yaml > patch
* Загрузить *heroesdata* и *gamestrings* запустив файл *download_gamestrings.py*
### Ссылки для ручного обновления
* В папке data взять файл __herodata*.json__, заменить содержимое **heroesdata.json**
* В папке gamestrings взять файл __gamestrings*ruru.json__, заменить содержимое **gamestrings.json**

## To Do для версии 0.5 - 1.0

- [ ] Разгрести папку utils/hots
    - [ ] Или дополнить ее и вынести туда функции из других модулей
    - [ ] Или объединить файлы перенести в utils/library
- [ ] Выделить все embed функции в отдельный файл в utils/library
- [X] Добавить тестовые токены в переменные среды, удалить из конфига
- [ ] Добавить скрипт для создания всех элементов БД
- [ ] Протестировать взаимодействие с БД через **sqlalchemy**
- [ ] Считывать конфиг в отдельный класс в Const
- [ ] Добавить тесты кода
- [ ] Добавить файлы для генерации таблиц в БД
- [ ] Перейти на использование исключений где это возможно
    - [ ] Больше пользовательских исключений
    - [ ] Отдельные обработчики внутри cog
- [ ] Добавить больше комментариев
- [ ] Переписать *create_heroes_ru_data* и все встреонные функции
- [ ] Попробовать собрать docker образ


## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details
