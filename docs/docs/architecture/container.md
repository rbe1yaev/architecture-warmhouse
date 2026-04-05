```puml
@startuml
!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title C4 Container Diagram (TO-BE) — SaaS-платформа "Тёплый дом"

LAYOUT_LEFT_RIGHT()

Person(user, "Пользователь", "Самостоятельно подключает устройства, управляет домом, настраивает сценарии и смотрит телеметрию")
Person(support_agent, "Сотрудник поддержки", "Просматривает состояние устройств пользователя и помогает решить проблему")

System_Ext(partner_devices, "Устройства", "Датчики, реле, свет, ворота, термостаты")

System_Boundary(warm_home, "SaaS-платформа «Тёплый дом»") {

  Container(web_app, "Web App", "SPA", "Личный кабинет: дома, устройства, сценарии, телеметрия")
  Container(mobile_app, "Mobile App", "iOS / Android", "Мобильное управление домом, быстрые команды, уведомления")
  Container(support_portal, "Support Portal", "Web App", "Интерфейс поддержки для просмотра состояния устройств пользователя")

  Container(api_gateway, "API Gateway / BFF", "Go", "Единая точка входа для клиентов, маршрутизация, агрегация API, авторизация")
  Container(identity_svc, "Identity Service", "Go", "Пользователи, роли, доступ, аутентификация")
  Container(household_svc, "Household Service", "Go", "Дома, комнаты, посёлки, привязка пользователей к объектам")
  Container(device_mgmt_svc, "Device Management Service", "Go", "Каталог устройств, реестр устройств, подключение и активация")
  Container(iot_gateway_svc, "IoT Gateway Service", "Go", "Подключение устройств через интернет, протоколы, сессии устройств")
  Container(device_control_svc, "Device Control Service", "Go", "Команды устройствам, текущее и целевое состояние, статус исполнения")
  Container(telemetry_svc, "Telemetry Service", "Go", "Приём и хранение телеметрии, последние значения, история")
  Container(automation_svc, "Automation Service", "Go", "Сценарии, правила, триггеры, автоматические действия")
  Container(notification_svc, "Notification Service", "Go", "Push, email, SMS, системные уведомления")
  Container(event_bus, "Event Bus", "Kafka / RabbitMQ", "Асинхронный обмен событиями между сервисами")
  Container(redis_cache, "Redis", "Redis", "Кэш, быстрый доступ к актуальному (последнему) состоянию датчиков")

  ContainerDb(identity_db, "Identity DB", "PostgreSQL", "Пользователи, роли, права доступа")
  ContainerDb(household_db, "Household DB", "PostgreSQL", "Дома, комнаты, структура объектов")
  ContainerDb(device_mgmt_db, "Device Management DB", "PostgreSQL", "Реестр устройств, каталог, активация")
  ContainerDb(device_control_db, "Device Control DB", "PostgreSQL", "Команды, статусы команд, текущее состояние")
  ContainerDb(telemetry_db, "Telemetry DB", "TimescaleDB / InfluxDB", "Временные ряды и показания датчиков")
  ContainerDb(automation_db, "Automation DB", "PostgreSQL", "Правила, сценарии, история срабатываний")
  ContainerDb(notification_db, "Notification DB", "PostgreSQL", "Журнал уведомлений")
}

Rel(user, web_app, "Использует", "HTTPS")
Rel(user, mobile_app, "Использует", "HTTPS")
Rel(support_agent, support_portal, "Использует", "HTTPS")

Rel(web_app, api_gateway, "Вызывает API", "HTTPS/JSON")
Rel(mobile_app, api_gateway, "Вызывает API", "HTTPS/JSON")
Rel(support_portal, api_gateway, "Вызывает API", "HTTPS/JSON")

Rel(api_gateway, identity_svc, "Вход, профиль, права доступа", "HTTPS/JSON")
Rel(api_gateway, household_svc, "Дома, комнаты, структура объектов", "HTTPS/JSON")
Rel(api_gateway, device_mgmt_svc, "Каталог устройств, подключение, список устройств", "HTTPS/JSON")
Rel(api_gateway, device_control_svc, "Ручное управление устройствами и просмотр состояния", "HTTPS/JSON")
Rel(api_gateway, telemetry_svc, "Просмотр показаний и истории", "HTTPS/JSON")
Rel(api_gateway, automation_svc, "Создание и настройка сценариев", "HTTPS/JSON")

Rel(identity_svc, identity_db, "Читает и записывает")
Rel(household_svc, household_db, "Читает и записывает")
Rel(device_mgmt_svc, device_mgmt_db, "Читает и записывает")
Rel(device_control_svc, device_control_db, "Читает и записывает")
Rel(telemetry_svc, telemetry_db, "Читает и записывает")
Rel(automation_svc, automation_db, "Читает и записывает")
Rel(notification_svc, notification_db, "Читает и записывает")

Rel(iot_gateway_svc, redis_cache, "Хранит сессии устройств и кэш состояний")
Rel(device_control_svc, redis_cache, "Кэширует актуальное состояние")
Rel(telemetry_svc, redis_cache, "Хранит последние значения")

Rel(device_mgmt_svc, household_svc, "Привязывает устройство к дому или комнате", "HTTPS/JSON")
Rel(device_control_svc, device_mgmt_svc, "Получает тип устройства, возможности и статус", "HTTPS/JSON")
Rel(device_control_svc, household_svc, "Проверяет, к какому дому относится устройство", "HTTPS/JSON")
Rel(notification_svc, identity_svc, "Получает контакты получателей", "HTTPS/JSON")

Rel(device_control_svc, iot_gateway_svc, "Передаёт команды устройствам", "MQTT / HTTPS")
Rel(partner_devices, iot_gateway_svc, "Подключаются, отправляют показания и получают команды", "MQTT")

Rel(device_mgmt_svc, event_bus, "Публикует события: устройство зарегистрировано, устройство активировано", "Асинхронно")
Rel(iot_gateway_svc, event_bus, "Публикует события: устройство подключилось, пришли значения с датчиков, ошибка доставки команды", "Асинхронно")
Rel(device_control_svc, event_bus, "Публикует события: состояние устройства изменилось, команда выполнена, команда не выполнена", "Асинхронно")
Rel(telemetry_svc, event_bus, "Публикует события: значения с датчиков сохранены, превышен порог", "Асинхронно")
Rel(automation_svc, event_bus, "Публикует события: сценарий сработал, ошибка выполнения сценария", "Асинхронно")
Rel(notification_svc, event_bus, "Подписывается на события", "Асинхронно")

Rel(event_bus, telemetry_svc, "Передаёт события о значениях с датчиков", "Асинхронно")
Rel(event_bus, automation_svc, "Передаёт события о новых показаниях и изменении состояния устройств", "Асинхронно")
Rel(automation_svc, device_control_svc, "Запрашивает выполнение действий по сценарию", "HTTPS/gRPC")

SHOW_LEGEND()
@enduml
``` 