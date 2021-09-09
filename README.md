# SamuroBot for Heroes of the Storm

## Authors

 **[fennr (@fennr)](fennr.github.io/)**

## Links

На случай выхода патча ссылки для обноваления json файлов

 **[heroesdata](https://github.com/HeroesToolChest/heroes-data/tree/master/heroesdata)**
### Автоматическое обновление
* Обновить в конфиге номер текущего патча > config.yaml > patch
* Загрузить *heroesdata* и *gamestrings* запустив файл *download_gamestrings.py*
### Ссылки для ручного обновления
* В папке data взять файл __herodata*.json__, заменить содержимое **heroesdata.json**
* В папке gamestrings взять файл __gamestrings*ruru.json__, заменить содержимое **gamestrings.json**
* Файл с переводом геров основан на спаршеных билдах **[стулка](https://vk.com/@st_lk-builds-roles)**. Обновлений он не требует, При необходимости дописать нового героя в ручную.

## To Do

- [ ] Поправить суб таланты шапки абатура
- [ ] Добавить для класса Hero возможность принимать или строку (и искать) или сразу словарь
- [ ] Добавить инструкции по настройке PostegreSQL, по возможности автоматизировать процессы
- [ ] Отрефакторить *cogs*, посмотреть где логичнее описание команд
- [ ] Добавить блэклист в БД
- [ ] Добавить новости в БД
- [ ] Добавить простые методы по добавлению и удалению записей из БД
- [ ] Протестировать взаимодействие с БД через **sqlalchemy**
- [ ] Возможно перейти на конфиг в json или считывать его в отдельный класс
- [ ] Добавить тесты кода

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details
