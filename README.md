# Работа с приложением


## Запуск через Docker Compose (Рекомендуется):

#### создайте .env по [.env.example](./.env.example)

#### Запустите приложение:
```
make compose-build
```
` (дождитесь проведения миграций в контейнере db-migration)`


#### стоп через Docker Compose:
```
make compose-stop
```

## Запуск локально (Не рекомендуется):
#### создайте .env.local по [.env.local.example](./.env.local.example)

#### выполните миграции (для выполнения должен быть установлен go):
```
make migrate-up
```

#### установите все зависимости:
```
make install-requirements
```

#### Запустите приложение
```
python -m cmd.main
```

для работы нужна рабочая pastgreSQL, также можете подключить prometheus получая метрики с `:2112`

---

- ### порты бота:
    - `:2112` - метрики 
- ### порты приложения (при запуске через Docker compose)
    - `postgresql-master:5432` - мастер подключение базы данных
    - `postgresql-slave:5432` - слейв подключение базы данных
    - `prometheus:9090` - prometheus
    - `grafana:3000` - grafana 

`(при старте через Docker compose метрики бота по адресу hr-bot:2112)`

`(при старте через docker compose, чтобы подключить prometheus в grafana используйте http://prometheus:9090 вместо http://localhost:9090)`

### кастомные метрики prometheus:
- users_registered_total
- users_current_total
- requests_total (по разным эндпоинтам)
- active_users_percentage

--- 
# Взаимодействие с ботом

- для добавления администратора в .env (или .env.local при локальном запуске) необходимо вписать его telegramID в ROOT_ADMIN_ID(через запятую)
- /start - начало взаимодействия с ботом, как со стороны админисратора, так и пользователя


