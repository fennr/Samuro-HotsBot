# SamuroBot for Heroes of the Storm

## Authors

 **[fennr (@fennr)](fennr.github.io/)**

## Links

На случай выхода патча ссылки для обноваления json файлов

 **[heroesdata](https://github.com/HeroesToolChest/heroes-data/tree/master/heroesdata)**
### Автоматическое обновление
* Обновить в конфиге номер текущего патча
* Загрузить новый gamestrings запустив файл *download_gamestrings.py*
### Ссылки для ручного обновления
* В папке data взять файл __herodata*.json__, заменить содержимое **heroesdata.json**
* В папке gamestrings взять файл __gamestrings*ruru.json__, заменить содержимое **gamestrings.json**
* Файл с переводом геров основан на спаршеных билдах **[стулка](https://vk.com/@st_lk-builds-roles)**. Обновлений он не требует, При необходимости дописать нового героя в ручную.

## To Do

- [ ] Поправить суб таланты шапки абатура
- [x] Добавить возможность вывести один скилл героя, передавая кнопку как опциональный параметр [Q/W/E/{R1/R2}|R]
- [x] Добавить команду #rotation с текущей ротацией героев. Взять данные из [nexuscompenduim](https://nexuscompendium.com/api/currently/herorotation)
- [ ] При пустом файле новостей выводить, что новостей сейчас нет

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details
