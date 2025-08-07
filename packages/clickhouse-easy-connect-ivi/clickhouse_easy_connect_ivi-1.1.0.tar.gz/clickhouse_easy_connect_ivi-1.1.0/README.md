# ClickHouse Easy Connect IVI

Упрощенная библиотека для работы с ClickHouse базой данных.

## 📦 Установка

### Для пользователей:

#### Вариант 1: Из wheel файла (рекомендуется)
```bash
pip install dist/clickhouse_easy_connect_ivi-1.1.0-py3-none-any.whl
```

#### Вариант 2: Из архива
```bash
pip install clickhouse_easy_connect_ivi-1.1.0.tar.gz
```

#### Вариант 3: Из Git репозитория
```bash
pip install git+https://github.com/your-company/clickhouse-easy-connect-ivi.git
```

### Для разработчиков:
```bash
git clone https://github.com/your-company/clickhouse-easy-connect-ivi.git
cd clickhouse-easy-connect-ivi
pip install -e .
```

## 🚀 Быстрый старт

### Настройка подключения

ClickHouse Easy поддерживает несколько способов указания параметров подключения:

1. **Через параметры конструктора**
2. **Через переменные окружения**  
3. **Через файл конфигурации**

### Использование переменных окружения (рекомендуется)

Для безопасности рекомендуется использовать переменные окружения:

```bash
export CLICKHOUSE_HOST=your_clickhouse_host
export CLICKHOUSE_PORT=8123
export CLICKHOUSE_USERNAME=your_username
export CLICKHOUSE_PASSWORD=your_password
export CLICKHOUSE_DATABASE=your_database
```

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Параметры будут автоматически загружены из переменных окружения
client = ClickHouseEasy()
df = client.query("SELECT * FROM your_table LIMIT 10")
```

### Вариант 1: Прямое создание клиента

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Создание клиента с параметрами
client = ClickHouseEasy(
    host='your_clickhouse_host',
    port=8123,
    username='your_username',
    password='your_password',
    database='your_database'
)

# Выполнение запроса
df = client.query("SELECT * FROM your_table LIMIT 10")
print(df)
```

### Вариант 2: Использование файла конфигурации

#### Автоматическая инициализация (рекомендуется)

При первом использовании автоматически создастся шаблон конфигурации:

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# При первом запуске создастся clickhouse_config.yaml с шаблоном
client = ClickHouseEasy()
# Отредактируйте созданный файл со своими данными и запустите снова
```

#### Ручная настройка конфигурации

Создайте конфигурацию одним из способов:

```python
from clickhouse_easy_connect_ivi import init_config, quick_setup

# Способ 1: Интерактивная настройка
init_config(interactive=True)

# Способ 2: Программная настройка
init_config(
    host="your_host",
    username="your_username",
    password="your_password",
    database="your_database"
)

# Способ 3: Быстрая настройка с созданием клиента
client = quick_setup(
    host="your_host",
    username="your_username", 
    password="your_password",
    database="your_database"
)
```

Затем просто используйте клиент:

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Конфиг уже создан - используем его
client = ClickHouseEasy()
df = client.query("SELECT * FROM your_table")
```

**⚠️ Важно**: Добавьте `clickhouse_config.yaml` в `.gitignore`, чтобы не попали учетные данные в репозиторий!

#### YAML конфигурация (единственный поддерживаемый формат)
Создайте локальный файл `clickhouse_config.yaml`:
```yaml
host: your_host
port: 8123
username: your_username
password: your_password
database: your_database
```

Или используйте новые функции инициализации:
```python
from clickhouse_easy_connect_ivi import init_config

# Создание шаблона конфигурации
config_path = init_config('my_config.yaml', create_template=True)
# Отредактируйте созданный файл, указав ваши данные

# Или создание с данными сразу
init_config(
    'my_config.yaml',
    host='your_host',
    username='your_username',
    password='your_password',
    database='your_database'
)
```

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Загрузка из файла конфигурации
client = ClickHouseEasy(config_file='clickhouse_config.yaml')

# Выполнение запроса
df = client.query("SELECT * FROM your_table")
```

### Вариант 3: Быстрое создание

```python
from clickhouse_easy_connect_ivi import create_client

# Быстрое создание клиента (теперь требует указать host)
client = create_client(
    host='your_clickhouse_host',
    port=8123,
    username='your_username',
    password='your_password',
    database='your_database'
)

df = client.query("SELECT COUNT(*) as count FROM your_table")
```

### Вариант 4: Использование контекстного менеджера

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

with ClickHouseEasy(
    host='your_host',
    username='user', 
    password='pass', 
    database='db'
) as client:
    df = client.query("SELECT * FROM your_table")
    # Соединение автоматически закроется
```

## 🔒 Безопасность

### Не храните учетные данные в коде!

❌ **Плохо:**
```python
from clickhouse_easy_connect_ivi import ClickHouseEasy
client = ClickHouseEasy(
    host='production-server.com',
    username='admin',
    password='secret123'  # Никогда не делайте так!
)
```

✅ **Хорошо:**
```python
from clickhouse_easy_connect_ivi import ClickHouseEasy
# Используйте переменные окружения
client = ClickHouseEasy()  # Загрузит из env переменных

# Или файл конфигурации (не забудьте добавить в .gitignore)
client = ClickHouseEasy(config_file='clickhouse_config.yaml')
```

### Рекомендации:

1. **Используйте переменные окружения** для продакшена
2. **Файлы конфигурации добавляйте в .gitignore**
3. **Используйте разные учетные данные** для разработки и продакшена
4. **Ограничивайте права пользователей** в ClickHouse

## Примеры использования

### Создание безопасной конфигурации

```python
from clickhouse_easy_connect_ivi import init_config

# Создает пример файла конфигурации
config_path = init_config('clickhouse_config.yaml', create_template=True)
# Файл будет создан с заглушками - отредактируйте его!

# Или интерактивная настройка
init_config(interactive=True)
```

### Выполнение простого запроса

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy
client = ClickHouseEasy(
    host='your_host',
    username='user', 
    password='pass', 
    database='db'
)
df = client.query("SELECT * FROM users WHERE age > 25")
```

### Выполнение команды (INSERT, UPDATE, DELETE)

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy
client = ClickHouseEasy(
    host='your_host',
    username='user', 
    password='pass', 
    database='db'
)
client.execute("INSERT INTO users VALUES (1, 'John', 30)")
```

### Сохранение конфигурации

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy
client = ClickHouseEasy(
    host='your_host',
    username='user', 
    password='pass', 
    database='db'
)
client.save_config('my_config.yaml')  # Только YAML формат
```

## API

### ClickHouseEasy

#### Методы:
- `__init__(host, port, username, password, database, config_file, auto_init_config)` - Инициализация
- `connect()` - Установка соединения
- `query(sql_query, **kwargs)` - Выполнение SELECT-запроса, возвращает DataFrame
- `execute(sql_command)` - Выполнение команды (INSERT, UPDATE, DELETE и т.д.)
- `close()` - Закрытие соединения
- `save_config(config_file, format)` - Сохранение конфигурации (только YAML)

#### Статические методы:
- `initialize_config(config_file, host, port, username, password, database, create_template, overwrite)` - Инициализация конфигурационного файла
- `setup_config_interactive(config_file)` - Интерактивная настройка конфигурации
- `reset_auto_init()` - Сброс флага автоинициализации (для тестирования)

### Функции:
- `create_client(host, port, username, password, database)` - Быстрое создание клиента
- `init_config(config_file, interactive, **kwargs)` - Удобная функция для инициализации конфига
- `quick_setup(**kwargs)` - Быстрая настройка с созданием конфига и клиента

## Требования

- Python >= 3.7
- pandas >= 1.0.0
- clickhouse-connect >= 0.5.0
- PyYAML >= 5.0.0
