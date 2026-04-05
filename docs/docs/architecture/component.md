```puml
@startuml
!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Component Diagram — API Gateway / BFF

LAYOUT_LEFT_RIGHT()

Person(user, "Пользователь", "Работает через web и mobile")
Person(support_agent, "Сотрудник поддержки", "Просматривает состояние устройств пользователя")

Container(web_app, "Web App", "SPA", "Веб-клиент")
Container(mobile_app, "Mobile App", "iOS / Android", "Мобильный клиент")
Container(support_portal, "Support Portal", "Web App", "Портал поддержки")

Container(identity_svc, "Сервис пользователей", "Go", "Пользователи, роли, доступ")
Container(household_svc, "Сервис домов", "Go", "Дома, комнаты, объекты")
Container(device_mgmt_svc, "Сервис устройств", "Go", "Каталог, реестр, подключение")
Container(device_control_svc, "Сервис управления устройствами", "Go", "Команды и состояние устройств")
Container(telemetry_svc, "Сервис телеметрии", "Go", "Показания и история")
Container(automation_svc, "Сервис сценариев", "Go", "Правила и сценарии")

Container_Boundary(api_gateway, "API Gateway / BFF") {
  Component(auth_proxy, "Проверка доступа", "Go", "Проверяет токены и права доступа")
  Component(request_router, "Маршрутизация запросов", "Go", "Направляет запросы в нужные сервисы")
  Component(client_api, "Клиентский API", "Go", "Единый API для web, mobile и поддержки")
}

Rel(user, web_app, "Использует", "HTTPS")
Rel(user, mobile_app, "Использует", "HTTPS")
Rel(support_agent, support_portal, "Использует", "HTTPS")

Rel(web_app, client_api, "Вызывает API", "HTTPS/JSON")
Rel(mobile_app, client_api, "Вызывает API", "HTTPS/JSON")
Rel(support_portal, client_api, "Вызывает API", "HTTPS/JSON")

Rel(client_api, auth_proxy, "Проверяет доступ")
Rel(client_api, request_router, "Передаёт запрос")

Rel(auth_proxy, identity_svc, "Проверяет пользователя и права", "HTTPS/JSON")
Rel(request_router, household_svc, "Маршрутизирует запросы", "HTTPS/JSON")
Rel(request_router, device_mgmt_svc, "Маршрутизирует запросы", "HTTPS/JSON")
Rel(request_router, device_control_svc, "Маршрутизирует запросы", "HTTPS/JSON")
Rel(request_router, telemetry_svc, "Маршрутизирует запросы", "HTTPS/JSON")
Rel(request_router, automation_svc, "Маршрутизирует запросы", "HTTPS/JSON")



SHOW_LEGEND()
@enduml
```


```puml
@startuml
!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Component Diagram — Сервис пользователей

LAYOUT_LEFT_RIGHT()

Container(api_gateway, "API Gateway / BFF", "Go", "Единая точка входа")
Container(notification_svc, "Сервис уведомлений", "Go", "Отправка уведомлений")

ContainerDb(identity_db, "Identity DB", "PostgreSQL", "Пользователи, роли, права доступа")

Container_Boundary(identity_svc, "Сервис пользователей") {
  Component(identity_api, "API пользователей", "Go", "Обрабатывает запросы на вход, профиль и права")
  Component(auth_manager, "модуль аутентификации", "Go", "Проверяет логин и пароль, управляет сессией")
  Component(token_manager, "модуль токенов", "Go", "Выдаёт и проверяет токены доступа")
  Component(access_manager, "модуль прав доступа", "Go", "Управляет ролями и разрешениями")
  Component(user_manager, "модуль пользователей", "Go", "Профиль пользователя и учётные данные")
  Component(identity_repo, "Репозиторий пользователей", "Go", "Работа с БД пользователей")
}

Rel(api_gateway, identity_api, "Вход, профиль, права", "HTTPS/JSON")
Rel(notification_svc, identity_api, "Запрашивает контакты получателей", "HTTPS/JSON")

Rel(identity_api, auth_manager, "Передаёт запросы на вход")
Rel(identity_api, token_manager, "Проверяет токены")
Rel(identity_api, access_manager, "Проверяет права")
Rel(identity_api, user_manager, "Работает с профилями")

Rel(auth_manager, identity_repo, "Читает данные пользователя")
Rel(token_manager, identity_repo, "Проверяет и сохраняет токены")
Rel(access_manager, identity_repo, "Читает роли и права")
Rel(user_manager, identity_repo, "Читает и обновляет профиль")

Rel(identity_repo, identity_db, "Читает и записывает")

SHOW_LEGEND()
@enduml
```

```puml
@startuml
!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Component Diagram — Сервис домов

LAYOUT_LEFT_RIGHT()

Container(api_gateway, "API Gateway / BFF", "Go", "Единая точка входа")
Container(device_mgmt_svc, "Сервис устройств", "Go", "Каталог, реестр, подключение")
Container(device_control_svc, "Сервис управления устройствами", "Go", "Команды и состояние устройств")

ContainerDb(household_db, "Household DB", "PostgreSQL", "Дома,")

Container_Boundary(household_svc, "Сервис домов") {
  Component(household_api, "API домов", "Go", "Обрабатывает запросы по домам")
  Component(home_manager, "модуль домов", "Go", "Создаёт и изменяет дома")
  Component(residency_manager, "модуль привязки пользователей", "Go", "Связывает пользователей с домами")
  Component(household_repo, "Репозиторий домов", "Go", "Работа с данными о домах")
}

Rel(api_gateway, household_api, "Запрашивает дома", "HTTPS/JSON")
Rel(device_mgmt_svc, household_api, "Привязывает устройство к дому или комнате", "HTTPS/JSON")
Rel(device_control_svc, household_api, "Проверяет принадлежность устройства дому", "HTTPS/JSON")

Rel(household_api, home_manager, "Передаёт запросы")
Rel(household_api, residency_manager, "Передаёт запросы")


Rel(home_manager, household_repo, "Читает и записывает")
Rel(residency_manager, household_repo, "Читает и записывает")


Rel(household_repo, household_db, "Читает и записывает")

SHOW_LEGEND()
@enduml
```

```puml
@startuml
!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Component Diagram — Сервис устройств

LAYOUT_LEFT_RIGHT()

Container(api_gateway, "API Gateway / BFF", "Go", "Единая точка входа")
Container(household_svc, "Сервис домов", "Go", "Дома и комнаты")
Container(device_control_svc, "Сервис управления устройствами", "Go", "Команды и состояние")
Container(event_bus, "Event Bus", "Kafka / RabbitMQ", "Асинхронный обмен событиями")

ContainerDb(device_mgmt_db, "Device Management DB", "PostgreSQL", "Реестр устройств, каталог, активация")

Container_Boundary(device_mgmt_svc, "Сервис устройств") {
  Component(device_api, "API устройств", "Go", "Обрабатывает запросы на подключение и просмотр устройств")
  
  Component(registry_manager, "Модуль реестра устройств", "Go", "Ведёт список подключённых устройств")
  Component(onboarding_manager, "Модуль подключения устройств", "Go", "Запускает процесс подключения и активации")
  
  Component(device_repo, "Репозиторий устройств", "Go", "Работа с каталогом, реестром и активацией")
  Component(device_events, "Публикатор событий", "Go", "Публикует события о новых и активированных устройствах")
}

Rel(api_gateway, device_api, "Запрашивает каталог и список устройств", "HTTPS/JSON")
Rel(device_control_svc, device_api, "Получает тип устройства, возможности и статус", "HTTPS/JSON")


Rel(device_api, registry_manager, "Передаёт запросы")
Rel(device_api, onboarding_manager, "Передаёт запросы")


Rel(onboarding_manager, household_svc, "Привязывает устройство к дому или комнате", "HTTPS/JSON")


Rel(registry_manager, device_repo, "Читает и записывает")
Rel(onboarding_manager, device_repo, "Читает и записывает")


Rel(registry_manager, device_events, "Передаёт событие")


Rel(device_repo, device_mgmt_db, "Читает и записывает")
Rel(device_events, event_bus, "Публикует события", "Асинхронно")

SHOW_LEGEND()
@enduml
```



```puml
@startuml
!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Component Diagram — Шлюз устройств

LAYOUT_LEFT_RIGHT()

System_Ext(partner_devices, "Устройства", "Датчики, реле, свет, ворота, термостаты")

Container(device_mgmt_svc, "Сервис устройств", "Go", "Реестр и активация устройств")
Container(event_bus, "Event Bus", "Kafka / RabbitMQ", "Асинхронный обмен событиями")
Container(device_control_svc, "Сервис управления устройствами", "Go", "Передаёт команды устройствам")


Container_Boundary(iot_gateway_svc, "Шлюз устройств") {
  Component(protocol_adapter, "Адаптеры протоколов", "Go", "Работают с MQTT, HTTP, WebSocket")
  Component(device_auth, "Проверка устройства", "Go", "Проверяет, что устройство зарегистрировано и может подключиться")
  Component(telemetry_receiver, "Приём показаний", "Go", "Принимает значения с датчиков")
  Component(command_dispatcher, "Доставка команд", "Go", "Передаёт команды физическим устройствам")
  Component(gateway_events, "Публикатор событий", "Go", "Публикует события о подключении и новых показаниях")
}

Rel(partner_devices, protocol_adapter, "Подключаются и обмениваются сообщениями", "MQTT / HTTP / WebSocket")

Rel(protocol_adapter, device_auth, "Проверяет устройство")

Rel(protocol_adapter, telemetry_receiver, "Передаёт показания")
Rel(device_control_svc, command_dispatcher, "Передаёт команды устройствам", "MQTT / HTTPS")

Rel(device_auth, device_mgmt_svc, "Проверяет регистрацию и активацию устройства", "HTTPS/JSON")


Rel(telemetry_receiver, gateway_events, "Передаёт новые значения")

Rel(command_dispatcher, gateway_events, "Передаёт ошибки доставки")

Rel(gateway_events, event_bus, "Публикует события", "Асинхронно")

SHOW_LEGEND()
@enduml
```