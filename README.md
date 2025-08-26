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

[![](https://img.plantuml.biz/plantuml/svg/nLRTQjim5BxNKmXVfT1rzxae7QMmmjQDflT6iRN4n9Q2fBJaRalPog1G6BiSR7s3h6reM9hi5QHNs0li5NPanxMSEFsxMQ1OLew-yvrpla_fbbH4g5uI8z9JdFMI9XL8TYBM9O8aE8uOLVqknLoeDdU-w9AWGrgqeVennO86Yh1MJ15IaO8D_KEFzAKUcmzcODxheVa4wpEiftgcB-3lKi-m_WsBYJdLr-dcq0pWpCIS8H8eBl2BC8aOchzinn5b2a5g5GLHbp25Nn8Mni3LtTkdNIuZED0lRU-orpI1pMqIj2aAYI9D8Yb-owLg2IehOnk00lKXX1XNKFuXdLDQNmh1yD7VqsAEpGaKCTLZFS9wgA_q3IodJXy6UWRFcRx1ywsP_gN7628djZyNvYFiNEaXeYp4DZD2QLRyR3El6DUnfxz2s4_8S07O0tEwifcURM1qIA24l64v322M6WEu90pzX4e9LTNcpxKY7WvaN830ds-V_uw1y1T8DWB2OviGquH4ySEcNFTM4gdZNXU6H7rBdREQTqGY5R6M_uuBFqtX4yl3MrlgZMqDJCASG9fXAKCXZJeE1BNmRIBRjHHl7TlrMj4hHqZ5qiBacgdZtRt6plu1F0xUW1caFE8Yb0N2hRZoHTe_byKUPo16kdp2pUYMjdZ08Raqexghhs65lcuxbrdhtdWdRowa1phZ712kBKRkYsjGmHbe0OJlo3pZKTRvy_HoGdTgk8W6wGITNRdFkSek3xShStWhaB9chK2jNipnQaNY1qYo9wa0HLQLKQr9f_UBd8fPcEFbMNZBIIp4-LtpUsfjLjc-L0BUeRXLXcfHbKLQ6_dDVjQIp5kFSnLkxBpQsJwuTLIA-1XNbGy-nbuhJpgqxxbHh0Pg6niRJxz9BCB_lqKs5vsSZhX1Of8Kt1RDll1UpWeM076EhSf1fY1l-ykbHvxBP16msYahS2gZvsFfq7wJ4n7M18_X1wtgAjk2YyZ-4_GF)](https://editor.plantuml.com/uml/nLRTQjim5BxNKmXVfT1rzxae7QMmmjQDflT6iRN4n9Q2fBJaRalPog1G6BiSR7s3h6reM9hi5QHNs0li5NPanxMSEFsxMQ1OLew-yvrpla_fbbH4g5uI8z9JdFMI9XL8TYBM9O8aE8uOLVqknLoeDdU-w9AWGrgqeVennO86Yh1MJ15IaO8D_KEFzAKUcmzcODxheVa4wpEiftgcB-3lKi-m_WsBYJdLr-dcq0pWpCIS8H8eBl2BC8aOchzinn5b2a5g5GLHbp25Nn8Mni3LtTkdNIuZED0lRU-orpI1pMqIj2aAYI9D8Yb-owLg2IehOnk00lKXX1XNKFuXdLDQNmh1yD7VqsAEpGaKCTLZFS9wgA_q3IodJXy6UWRFcRx1ywsP_gN7628djZyNvYFiNEaXeYp4DZD2QLRyR3El6DUnfxz2s4_8S07O0tEwifcURM1qIA24l64v322M6WEu90pzX4e9LTNcpxKY7WvaN830ds-V_uw1y1T8DWB2OviGquH4ySEcNFTM4gdZNXU6H7rBdREQTqGY5R6M_uuBFqtX4yl3MrlgZMqDJCASG9fXAKCXZJeE1BNmRIBRjHHl7TlrMj4hHqZ5qiBacgdZtRt6plu1F0xUW1caFE8Yb0N2hRZoHTe_byKUPo16kdp2pUYMjdZ08Raqexghhs65lcuxbrdhtdWdRowa1phZ712kBKRkYsjGmHbe0OJlo3pZKTRvy_HoGdTgk8W6wGITNRdFkSek3xShStWhaB9chK2jNipnQaNY1qYo9wa0HLQLKQr9f_UBd8fPcEFbMNZBIIp4-LtpUsfjLjc-L0BUeRXLXcfHbKLQ6_dDVjQIp5kFSnLkxBpQsJwuTLIA-1XNbGy-nbuhJpgqxxbHh0Pg6niRJxz9BCB_lqKs5vsSZhX1Of8Kt1RDll1UpWeM076EhSf1fY1l-ykbHvxBP16msYahS2gZvsFfq7wJ4n7M18_X1wtgAjk2YyZ-4_GF)

