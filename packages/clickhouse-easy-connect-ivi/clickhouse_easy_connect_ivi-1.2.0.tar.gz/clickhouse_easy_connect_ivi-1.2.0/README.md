# ClickHouse Easy Connect IVI

Упрощенная библиотека для работы с ClickHouse базой данных с автоматической настройкой конфигурации и поддержкой переменных окружения.

## 📦 Установка

### Для пользователей:

#### Вариант 1: Из wheel файла (рекомендуется)
```bash
pip install dist/clickhouse_easy_connect_ivi-1.2.0-py3-none-any.whl
```

#### Вариант 2: Из архива
```bash
pip install clickhouse_easy_connect_ivi-1.2.0.tar.gz
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

### 🌟 Самый простой способ - автоматическая настройка

Библиотека автоматически создаст шаблон конфигурации при первом использовании:

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# При первом запуске автоматически создастся clickhouse_config.yaml
client = ClickHouseEasy()
# Отредактируйте созданный файл с вашими данными и запустите снова
```

### Способы настройки подключения

ClickHouse Easy поддерживает 4 способа указания параметров подключения (в порядке приоритета):

1. **Параметры конструктора** (наивысший приоритет)
2. **Файл конфигурации** 
3. **Переменные окружения**
4. **Значения по умолчанию** (наименьший приоритет)

### Способ 1: Использование переменных окружения (рекомендуется для продакшена)

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
print(df)
```

### Способ 2: Прямое создание клиента с параметрами

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Создание клиента с параметрами (отключаем автоинициализацию конфига)
client = ClickHouseEasy(
    host='your_clickhouse_host',
    port=8123,
    username='your_username',
    password='your_password',
    database='your_database',
    auto_init_config=False  # Отключаем автосоздание конфига
)

# Выполнение запроса
df = client.query("SELECT * FROM your_table LIMIT 10")
print(df)
```

### Способ 3: Использование файла конфигурации

#### Автоматическая инициализация (рекомендуется для разработки)

При первом использовании автоматически создастся шаблон конфигурации:

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# При первом запуске создастся clickhouse_config.yaml с шаблоном
client = ClickHouseEasy()
# Отредактируйте созданный файл со своими данными и запустите снова
```

#### Создание конфигурации разными способами

```python
from clickhouse_easy_connect_ivi import init_config, quick_setup

# Способ 1: Создание шаблона конфигурации
config_path = init_config('my_config.yaml', create_template=True)
# Отредактируйте созданный файл с вашими данными

# Способ 2: Интерактивная настройка через консоль
init_config(interactive=True)

# Способ 3: Программная настройка конфигурации
init_config(
    'my_config.yaml',
    host="your_host",
    username="your_username",
    password="your_password",
    database="your_database"
)

# Способ 4: Быстрая настройка с созданием клиента сразу
client = quick_setup(
    host="your_host",
    username="your_username", 
    password="your_password",
    database="your_database"
)
```

#### Использование существующего файла конфигурации

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Использование конкретного файла конфигурации
client = ClickHouseEasy(config_file='my_config.yaml')
df = client.query("SELECT * FROM your_table")
```

**⚠️ Важно**: Добавьте `clickhouse_config.yaml` в `.gitignore`, чтобы учетные данные не попали в репозиторий!

#### Формат YAML конфигурации

Создайте файл `clickhouse_config.yaml`:
```yaml
host: your_host
port: 8123
username: your_username
password: your_password
database: your_database
```

### Способ 4: Быстрое создание клиента с помощью функции create_client

```python
from clickhouse_easy_connect_ivi import create_client

# Быстрое создание клиента
client = create_client(
    host='your_clickhouse_host',
    port=8123,
    username='your_username',
    password='your_password',
    database='your_database'
)

df = client.query("SELECT COUNT(*) as count FROM your_table")
```

### Способ 5: Использование контекстного менеджера

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

# Способ 1: Используйте переменные окружения
client = ClickHouseEasy()  # Загрузит из env переменных

# Способ 2: Файл конфигурации (не забудьте добавить в .gitignore)
client = ClickHouseEasy(config_file='clickhouse_config.yaml')

# Способ 3: Автоматический конфиг (создается один раз)
client = ClickHouseEasy()  # При первом запуске создаст шаблон
```

### Рекомендации по безопасности:

1. **Используйте переменные окружения** для продакшена
2. **Файлы конфигурации добавляйте в .gitignore**
3. **Используйте разные учетные данные** для разработки и продакшена
4. **Ограничивайте права пользователей** в ClickHouse
5. **Используйте автоматическую инициализацию** только для разработки

## 📝 Примеры использования

### Создание конфигурации разными способами

```python
from clickhouse_easy_connect_ivi import init_config, ClickHouseEasy

# 1. Создание шаблона конфигурации для ручного редактирования
config_path = init_config('clickhouse_config.yaml', create_template=True)
print(f"Шаблон создан: {config_path}")
# Отредактируйте файл с вашими данными

# 2. Интерактивная настройка через консоль
init_config(interactive=True)

# 3. Программное создание конфигурации
init_config(
    'production_config.yaml',
    host='prod-clickhouse.company.com',
    username='app_user',
    password='secure_password',
    database='analytics'
)

# 4. Создание конфигурации методом класса
ClickHouseEasy.initialize_config(
    'my_config.yaml',
    host='localhost',
    username='developer',
    password='dev_pass',
    database='test_db',
    overwrite=True
)
```

### Автоматическая инициализация (удобно для начала работы)

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# При первом запуске автоматически создается clickhouse_config.yaml
client = ClickHouseEasy()
# Программа создаст шаблон и попросит отредактировать его
```

### Быстрая настройка с созданием клиента

```python
from clickhouse_easy_connect_ivi import quick_setup

# Одной командой создаем конфиг и получаем готового клиента
client = quick_setup(
    host='your_host',
    username='your_user',
    password='your_pass',
    database='your_db'
)

# Сразу можем работать
df = client.query("SELECT version()")
print(df)
```

### Выполнение запросов

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Инициализация клиента (параметры из env или config файла)
client = ClickHouseEasy()

# Простой SELECT запрос
df = client.query("SELECT * FROM users WHERE age > 25")
print(df)

# Запрос с дополнительными параметрами
df = client.query(
    "SELECT name, age, city FROM users WHERE age BETWEEN {min_age} AND {max_age}",
    parameters={'min_age': 18, 'max_age': 65}
)

# Агрегированный запрос
stats = client.query("""
    SELECT 
        city,
        COUNT(*) as user_count,
        AVG(age) as avg_age
    FROM users 
    GROUP BY city 
    ORDER BY user_count DESC
""")
```

### Выполнение команд (INSERT, UPDATE, DELETE)

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

client = ClickHouseEasy()

# Вставка данных
client.execute("INSERT INTO users VALUES (1, 'John', 30)")

# Множественная вставка
client.execute("""
    INSERT INTO users VALUES 
    (2, 'Alice', 25),
    (3, 'Bob', 35),
    (4, 'Carol', 28)
""")

# Обновление данных
client.execute("ALTER TABLE users UPDATE age = age + 1 WHERE name = 'John'")

# Создание таблицы
client.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id UInt32,
        name String,
        price Float64
    ) ENGINE = MergeTree()
    ORDER BY id
""")
```

### Работа с контекстным менеджером

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Соединение автоматически закроется после выхода из блока with
with ClickHouseEasy(config_file='production.yaml') as client:
    # Выполняем множественные операции
    users_df = client.query("SELECT * FROM users LIMIT 100")
    products_df = client.query("SELECT * FROM products WHERE price > 10")
    
    # Вставляем новые данные
    client.execute("INSERT INTO logs VALUES (now(), 'Application started')")
    
    print(f"Найдено пользователей: {len(users_df)}")
    print(f"Найдено товаров: {len(products_df)}")
# Соединение автоматически закрыто здесь
```

### Сохранение конфигурации

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Создаем клиента с параметрами
client = ClickHouseEasy(
    host='your_host',
    username='user', 
    password='pass', 
    database='db'
)

# Сохраняем текущую конфигурацию в файл
client.save_config('my_backup_config.yaml')

# Теперь можно использовать сохраненную конфигурацию
new_client = ClickHouseEasy(config_file='my_backup_config.yaml')
```

### Управление автоинициализацией (для тестирования)

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Сброс флага автоинициализации (полезно в тестах)
ClickHouseEasy.reset_auto_init()

# Теперь при создании клиента шаблон не будет создаваться автоматически
client = ClickHouseEasy()  # Может бросить ошибку, если нет конфига
```

## 📖 API Документация

### Класс ClickHouseEasy

#### Конструктор:
```python
ClickHouseEasy(
    host: Optional[str] = None,
    port: Optional[int] = None, 
    username: Optional[str] = None,
    password: Optional[str] = None,
    database: Optional[str] = None,
    config_file: Optional[str] = None,
    auto_init_config: bool = True
)
```

**Параметры:**
- `host` - Хост ClickHouse сервера
- `port` - Порт для подключения (по умолчанию 8123)
- `username` - Имя пользователя
- `password` - Пароль
- `database` - Имя базы данных
- `config_file` - Путь к файлу конфигурации
- `auto_init_config` - Автоматически создать шаблон конфига при первом использовании

#### Основные методы:

**`connect() -> bool`**
- Установка соединения с ClickHouse
- Возвращает True при успешном подключении

**`query(sql_query: str, **kwargs) -> pd.DataFrame`**
- Выполнение SELECT-запроса
- Возвращает pandas DataFrame с результатами
- Поддерживает дополнительные параметры для query_df

**`execute(sql_command: str) -> Any`**
- Выполнение команды (INSERT, UPDATE, DELETE, CREATE и т.д.)
- Возвращает результат выполнения команды

**`close()`**
- Закрытие соединения с сервером

**`save_config(config_file: str, format: str = "yaml")`**
- Сохранение текущей конфигурации в файл
- Поддерживается только YAML формат

#### Статические методы:

**`initialize_config(config_file, host, port, username, password, database, create_template, overwrite) -> str`**
- Инициализация конфигурационного файла
- `create_template=True` создает шаблон с placeholder'ами
- Возвращает путь к созданному файлу

**`setup_config_interactive(config_file) -> str`**
- Интерактивная настройка конфигурации через консоль
- Запрашивает у пользователя все необходимые параметры

**`reset_auto_init()`**
- Сброс флага автоинициализации (для тестирования)

#### Поддержка контекстного менеджера:
```python
with ClickHouseEasy() as client:
    # Работа с клиентом
    df = client.query("SELECT 1")
# Соединение автоматически закрывается
```

### Вспомогательные функции:

**`create_client(username, password, database, host, port=8123) -> ClickHouseEasy`**
- Быстрое создание клиента ClickHouse
- Все параметры обязательны

**`init_config(config_file="clickhouse_config.yaml", interactive=False, **kwargs) -> str`**
- Удобная функция для инициализации конфига
- `interactive=True` запускает интерактивный режим
- `**kwargs` передаются в initialize_config

**`quick_setup(**kwargs) -> ClickHouseEasy`**
- Быстрая настройка с созданием конфига и клиента
- Создает конфиг с переданными параметрами и возвращает готового клиента

### Приоритет настроек

Параметры подключения применяются в следующем порядке приоритета:

1. **Параметры конструктора** (наивысший приоритет)
2. **Файл конфигурации** 
3. **Переменные окружения**
4. **Значения по умолчанию** (наименьший приоритет)

### Переменные окружения

Поддерживаются следующие переменные окружения:
- `CLICKHOUSE_HOST` - хост сервера
- `CLICKHOUSE_PORT` - порт (по умолчанию 8123)
- `CLICKHOUSE_USERNAME` - имя пользователя
- `CLICKHOUSE_PASSWORD` - пароль
- `CLICKHOUSE_DATABASE` - имя базы данных

## 📋 Требования

- Python >= 3.7
- pandas >= 1.0.0
- clickhouse-connect >= 0.5.0
- PyYAML >= 5.0.0

## 🔧 Устранение неполадок

### Проблемы с подключением

1. **Проверьте параметры подключения:**
```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

client = ClickHouseEasy()
print(f"Host: {client.host}")
print(f"Port: {client.port}")
print(f"Username: {client.username}")
print(f"Database: {client.database}")
```

2. **Проверьте соединение вручную:**
```python
if client.connect():
    print("✅ Подключение успешно!")
else:
    print("❌ Ошибка подключения")
```

### Проблемы с конфигурацией

1. **Сброс автоинициализации:**
```python
ClickHouseEasy.reset_auto_init()
```

2. **Принудительное пересоздание конфига:**
```python
from clickhouse_easy_connect_ivi import init_config

init_config('clickhouse_config.yaml', create_template=True, overwrite=True)
```

3. **Проверка существования конфига:**
```python
from pathlib import Path

if Path('clickhouse_config.yaml').exists():
    print("✅ Конфиг существует")
else:
    print("❌ Конфиг не найден")
```
