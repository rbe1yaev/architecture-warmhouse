# «Тёплый дом» - трансформация компании

# Задание 1. Анализ и планирование

### 1. Описание функциональности монолитного приложения

**Управление отоплением:**

- Пользователи могут изменить статус сенсора - выключить/включить его (предполагается таким образом могут управлять температурой), но фактически по коду это не подтверждается, воздействия на сенсор нет, статус меняется только в бд. *Вероятно это просто нюанс в рамках учебного примера.

**Мониторинг температуры:**

- Пользователи могут проверять температуру отопления через внешний сервис по всем сенсорам, по конкретному сенсору и с фильтром по локациям

**Подключение датчика:**

- При включении датчик регистрируется в системе (настраивает сотрудник компании)
- Для целей прописывания сенсора в монолите присутствует специальный метод, который добавляет сенсор в БД

**Управление пользователями**

- В текущей реализации монолита отсутствует сущность - пользователь, не очень понятно где осуществляется привязка сенсоров к конкретному пользователю, вероятно это функция приложения, через которое осуществляется доступ к системе

### 2. Анализ архитектуры монолитного приложения

**Стек и компоненты:**
- **Язык/фреймворк:** Go 1.22, Gin Web Framework
- **БД:** PostgreSQL (через `pgx/v5/pgxpool`)
- **Контейнеризация:** многостадийный Dockerfile (alpine), порт `8080`
- **Конфигурация через ENV:**
  - `DATABASE_URL` (по умолчанию `postgres://postgres:postgres@localhost:5432/smarthome`)
  - `TEMPERATURE_API_URL` (по умолчанию `http://temperature-api:8081`)
  - `PORT` (по умолчанию `:8080`)

**Архитектура (слои):**
- `main.go:19` — точка входа: инициализация БД, инициализация клиента температурного сервиса, запуск HTTP-сервера, graceful shutdown по SIGINT/SIGTERM.
- `db/db.go` — слой доступа к данным (CRUD по сенсорам, пул соединений PostgreSQL).
- `models/sensor.go` — доменные модели: `Sensor`, `SensorCreate`, `SensorUpdate`, тип `SensorType` (на данный момент единственное значение — `temperature`).
- `services/temperature_service.go` — HTTP-клиент к внешнему `temperature-api` с таймаутом 10 с.
- `handlers/sensors.go` — HTTP-обработчики Gin, маршрутизация и оркестрация БД ↔ внешний сервис.
- `init.sql` — DDL: таблица `sensors` и индексы по `type`, `location`, `status`.

**Модель данных `sensors`**
Поля: `id`, `name`, `type`, `location`, `value`, `unit`, `status` (`active`/`inactive`/…), `last_updated`, `created_at`. Индексы по `type`, `location`, `status` для частых выборок.

**HTTP API**
Базовый префикс — `/api/v1`.

- `GET /health` — `main.go:39` — health-check (`{"status":"ok"}`).
- `GET /api/v1/sensors` — `handlers/sensors.go:46` — список всех сенсоров. Для каждого сенсора с `type=temperature` подмешивает актуальные `value/status/last_updated` из внешнего API (`GET {TEMPERATURE_API_URL}/temperature/{id}`); при сбое внешнего API запись возвращается с данными из БД, ошибка только логируется.
- `GET /api/v1/sensors/:id` — `handlers/sensors.go:73` — получить один сенсор по ID; для температурных — также обогащение данными из внешнего API.
- `POST /api/v1/sensors` — `handlers/sensors.go:132` — создать сенсор. Тело: `SensorCreate{name,type,location,unit}`. Статус по умолчанию `inactive`.
- `PUT /api/v1/sensors/:id` — `handlers/sensors.go:149` — частичное обновление (динамический SQL по непустым полям `SensorUpdate`).
- `DELETE /api/v1/sensors/:id` — `handlers/sensors.go:172` — удаление.
- `PATCH /api/v1/sensors/:id/value` — `handlers/sensors.go:189` — точечное обновление `value` и `status` (например, для приёма телеметрии).
- `GET /api/v1/sensors/temperature/:location` — `handlers/sensors.go:104` — проксирующий запрос к внешнему API: `GET {TEMPERATURE_API_URL}/temperature?location={location}`, возвращает `{location, value, unit, status, timestamp, description}`.

**Интеграция с внешним сервисом**
`services.TemperatureService` (`services/temperature_service.go:11`):
- `GetTemperature(location)` — `services/temperature_service.go:39` — запрос по локации.
- `GetTemperatureByID(sensorID)` — `services/temperature_service.go:61` — запрос по идентификатору сенсора.
- HTTP-клиент с таймаутом 10 секунд; разбор JSON в `TemperatureResponse`.

**Ключевые особенности поведения**
- **Гибрид «БД + live-данные»:** для температурных сенсоров операции чтения объединяют статическую конфигурацию из БД и текущие значения из внешнего сервиса.
- **Отказоустойчивость по чтению:** ошибки внешнего API не прерывают ответ — клиент получает данные из БД, ошибка попадает в лог.
- **Graceful shutdown:** `main.go:67` — обработка SIGINT/SIGTERM с таймаутом 5 секунд на завершение запросов.
- **Динамический UPDATE:** в `db.UpdateSensor` (`db/db.go:144`) запрос собирается только из переданных непустых полей; пустая строка трактуется как «не обновлять», что не позволяет очистить строковое поле через PUT (потенциальное ограничение API).
- **Расширяемость по типам сенсоров:** `SensorType` уже вынесен в enum-подобный тип, но фактически реализован только `temperature` — задел под другие типы (освещение, наблюдение, ворота и тп).

**Развёртывание**
Dockerfile собирает статический бинарник (`CGO_ENABLED=0`), финальный образ — `alpine` с `ca-certificates`/`tzdata`, экспонирует порт `8080`. Сервис рассчитан на запуск рядом с `temperature-api` и PostgreSQL (вероятно, через docker-compose в корне репозитория).

### 3. Определение доменов и границы контекстов

#### Core Domain: Управление устройствами

Основная бизнес-ценность системы — управление конкретными типами умных устройств.
Каждый тип устройства имеет уникальную доменную логику, поэтому выделен в отдельный bounded context.

**BC: Управление отоплением (Heating Control)**
- **Агрегаты:** HeatingDevice (термодатчик + реле)
- **Сущности:** Thermostat, HeatingRelay
- **Value Objects:** Temperature, TemperatureRange
- **Команды:** SetTemperature, TurnHeatingOn, TurnHeatingOff
- **Доменные события:** TemperatureSet, HeatingToggled
- **Сценарии:** изменение целевой температуры по локациям и конкретным приборам, включение/выключение отопительных приборов

**BC: Управление освещением (Lighting Control)**
- **Агрегаты:** LightingDevice (осветительный прибор)
- **Сущности:** Lamp
- **Value Objects:** LightState (on/off)
- **Команды:** SwitchLightOn, SwitchLightOff
- **Доменные события:** LightToggled
- **Сценарии:** включение/выключение осветительных приборов по локациям и конкретным приборам

**BC: Управление воротами (Gate Control)**
- **Агрегаты:** GateDevice (привод ворот)
- **Value Objects:** GateState (open/closed/moving)
- **Команды:** OpenGate, CloseGate
- **Доменные события:** GateOpened, GateClosed
- **Сценарии:** открытие/закрытие ворот

**BC: Управление видеонаблюдением (Surveillance Control)**
- **Агрегаты:** Camera
- **Value Objects:** StreamURL, CameraState
- **Команды:** EnableCamera, DisableCamera, GetCameraStream
- **Доменные события:** CameraEnabled, CameraDisabled
- **Сценарии:** включение/выключение камер и удалённый просмотр видеопотока

---

#### Supporting Domain: Подключение устройств (Device Provisioning)

Единый процесс подключения для всех типов устройств.
Специфика типа устройства вынесена в адаптеры — новый тип = новый адаптер, без переписывания сервиса.

**BC: Подключение устройств**
- **Агрегаты:** Device, DeviceRegistration
- **Сущности:** Device (id, type, location, connectionStatus, config)
- **Value Objects:** DeviceType, ConnectionStatus (pending/active/offline), DeviceConfig
- **Команды:** RegisterDevice, ActivateDevice, DeactivateDevice, RemoveDevice
- **Доменные события:** DeviceRegistered, DeviceActivated, DeviceDeactivated, DeviceRemoved, DeviceOffline
- **Адаптеры по типу устройства:** HeatingDeviceAdapter, LightingDeviceAdapter, GateAdapter, CameraAdapter
- **Расширяемость:** добавление нового типа устройства — реализация нового адаптера без изменения общего процесса
- **Интеграция с устройствами партнёров:** компания не производит устройства — все устройства в экосистеме являются партнёрскими. Подключение обеспечивается через стандартные протоколы (MQTT, HTTP, CoAP) и адаптеры

---

#### Supporting Domain: Управление локациями (Home Topology)

Топология домов и помещений пользователя, к которым привязываются устройства.
Является Upstream-контекстом для Device Provisioning, Telemetry и Scheduling — публикует язык локаций, не встраиваясь в их логику.

**BC: Управление локациями**
- **Агрегаты:** Home, Room
- **Value Objects:** Address, RoomType
- **Команды:** AddHome, AddRoom, RemoveRoom
- **Доменные события:** HomeAdded, RoomAdded, RoomRemoved

---

#### Supporting Domain: Телеметрия и мониторинг (Telemetry & Monitoring)

Единый сбор, хранение и визуализация данных со всех типов устройств.
Специфика типа данных вынесена в парсеры/коллекторы.

**BC: Сбор и хранение телеметрии (Data Collection)**
- **Агрегаты:** MetricStream (поток метрик с устройства)
- **Value Objects:** MetricPoint (value, unit, timestamp), MetricType (temperature, light_state, gate_state, video_status)
- **Команды:** IngestMetric, ConfigureCollection
- **Доменные события:** MetricReceived, DeviceDataStale
- **Парсеры по типу данных:** TemperatureParser, LightStateParser, GateStateParser, VideoStatusParser

**BC: Визуализация (Data Visualization)**
- **Сценарии:** дашборды по устройствам, по локациям, видеопоток с камер

---

#### Supporting Domain: Расписания (Scheduling)

Единый механизм расписаний для всех типов устройств.
Действие (Action) — полиморфное, определяется конкретным BC управления устройством.

**BC: Управление расписаниями**
- **Агрегаты:** Schedule
- **Сущности:** ScheduledAction
- **Value Objects:** TimeSlot, ActionPayload (полиморфный: SetTemperature(22°C), SwitchLight(on), OpenGate(), EnableCamera())
- **Команды:** CreateSchedule, ActivateSchedule, DeactivateSchedule, DeleteSchedule
- **Доменные события:** ScheduleCreated, ScheduleTriggered, ActionExecuted, ActionFailed
- **Сценарии:** расписание по календарю, дням недели и времени; выполнение активных расписаний

---

#### Generic Domain: Управление пользователями (Identity & Access Management)

**BC: Аутентификация и авторизация**
- **Агрегаты:** User
- **Value Objects:** Credentials, Session
- **Команды:** RegisterUser, Authenticate, ResetPassword
- **Доменные события:** UserRegistered, UserAuthenticated, PasswordReset

---

#### Связи между контекстами (Context Map)

| Upstream | Downstream | Тип связи | Примечание |
|----------|-----------|-----------|-----------|
| Device Provisioning | Heating/Lighting/Gate/Surveillance Control | Published Language | DeviceRegistered / DeviceDeactivated — контроллеры подписываются на события регистрации |
| Heating/Lighting/Gate/Surveillance Control | Telemetry | Event-driven | Контроллеры публикуют события телеметрии; Telemetry не знает о типах устройств |
| Scheduling | Heating/Lighting/Gate/Surveillance Control | Customer-Supplier (REST / OpenAPI) | Scheduling по таймеру синхронно вызывает нужный control-сервис с ActionPayload и получает подтверждение исполнения |
| IAM | Все контексты | ACL (Anti-Corruption Layer) | Каждый BC проверяет аутентификацию через ACL, не встраивая логику IAM напрямую |
| Home Topology | Device Provisioning | Published Language (Upstream → Downstream) | Device Provisioning принимает `locationId` как Value Object; Home Topology публикует HomeAdded / RoomAdded / RoomRemoved — Provisioning подписывается для валидации. Топологией владеет Home Topology, Provisioning только ссылается |
| Home Topology | Telemetry & Monitoring | Published Language (Upstream → Downstream) | Telemetry использует `locationId` для группировки метрик и дашбордов по комнатам/домам; не владеет топологией |
| Home Topology | Scheduling | Published Language (Upstream → Downstream) | Расписания могут быть привязаны к локации ("включить отопление во всём доме"); Scheduling читает локации через Published Language |

### 4. Проблемы монолитного решения

- затруднено масштабирование отдельных функций
- затруднено параллельное развитие и развертывание функционала независимыми командами (медленно, трудноуправляемо из за большого кол-ва внутренних согласований)
- высокий риск возникновения ошибок, которые положат всю систему (высокая созависимость компонентов)
- единая БД — невозможно выбрать оптимальное хранилище для каждого домена
- изменение модели Sensor затрагивает все слои
- отсутствие асинхронности — невозможно эффективно обрабатывать телеметрию от тысяч датчиков

### 5. Визуализация контекста системы — диаграмма С4

- [As-Is Context](/docs/diagrams/out/asis_context.png)

# Задание 2. Проектирование микросервисной архитектуры

В этом задании вам нужно предоставить только диаграммы в модели C4. Мы не просим вас отдельно описывать получившиеся микросервисы и то, как вы определили взаимодействия между компонентами To-Be системы. Если вы правильно подготовите диаграммы C4, они и так это покажут.

**Диаграмма контейнеров (Containers)**

- [To-Be Containers](/docs/diagrams/out/tobe_containers.png) — все контейнеры и взаимодействия
- [To-Be Containers Sync](/docs/diagrams/out/tobe_containers_sync.png) — отдельно синхронные
- [To-Be Containers Async](/docs/diagrams/out/tobe_containers_async.png) — отдельно асинхронные


**Диаграмма компонентов (Components)**

- [Device Provisioning Service](/docs/diagrams/out/tobe_component_device_provisioning.png)
- [Heating Control Service](/docs/diagrams/out/tobe_component_heating_control.png)
- [Lighting Control Service](/docs/diagrams/out/tobe_component_lighting_control.png)
- [Gate Control Service](/docs/diagrams/out/tobe_component_gate_control.png)
- [Surveillance Service](/docs/diagrams/out/tobe_component_surveillance.png)
- [Home Topology Service](/docs/diagrams/out/tobe_component_home_topology.png)
- [Telemetry Service](/docs/diagrams/out/tobe_component_telemetry.png)
- [Scheduling Service](/docs/diagrams/out/tobe_component_scheduling.png)
- [IAM Service](/docs/diagrams/out/tobe_component_iam.png)

**Диаграмма кода (Code)**

- [RegisterDevice](/docs/diagrams/out/tobe_code_register_device.png)

# Задание 3. Разработка ER-диаграммы

[To-Be ER Diagram](/docs/diagrams/out/tobe_er.png)

Диаграмма отражает логическую модель данных целевой микросервисной архитектуры. Связи между сущностями разных сервисов показаны как логические ссылки по идентификаторам, а не как физические внешние ключи между базами данных разных микросервисов.

# Задание 4. Создание и документирование API

### 1. Тип API

Укажите, какой тип API вы будете использовать для взаимодействия микросервисов. Объясните своё решение.

### 2. Документация API

Здесь приложите ссылки на документацию API для микросервисов, которые вы спроектировали в первой части проектной работы. Для документирования используйте Swagger/OpenAPI или AsyncAPI.

# Задание 5. Работа с docker и docker-compose

Перейдите в apps.

Там находится приложение-монолит для работы с датчиками температуры. В README.md описано как запустить решение.

Вам нужно:

1) сделать простое приложение temperature-api на любом удобном для вас языке программирования, которое при запросе /temperature?location= будет отдавать рандомное значение температуры.

Locations - название комнаты, sensorId - идентификатор названия комнаты

```
	// If no location is provided, use a default based on sensor ID
	if location == "" {
		switch sensorID {
		case "1":
			location = "Living Room"
		case "2":
			location = "Bedroom"
		case "3":
			location = "Kitchen"
		default:
			location = "Unknown"
		}
	}

	// If no sensor ID is provided, generate one based on location
	if sensorID == "" {
		switch location {
		case "Living Room":
			sensorID = "1"
		case "Bedroom":
			sensorID = "2"
		case "Kitchen":
			sensorID = "3"
		default:
			sensorID = "0"
		}
	}
```

2) Приложение следует упаковать в Docker и добавить в docker-compose. Порт по умолчанию должен быть 8081

3) Кроме того для smart_home приложения требуется база данных - добавьте в docker-compose файл настройки для запуска postgres с указанием скрипта инициализации ./smart_home/init.sql

Для проверки можно использовать Postman коллекцию smarthome-api.postman_collection.json и вызвать:

- Create Sensor
- Get All Sensors

Должно при каждом вызове отображаться разное значение температуры

Ревьюер будет проверять точно так же.
