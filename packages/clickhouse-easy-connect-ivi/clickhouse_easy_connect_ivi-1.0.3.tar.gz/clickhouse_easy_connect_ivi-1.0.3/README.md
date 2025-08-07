# ClickHouse Easy Connect IVI

Упрощенная библиотека для работы с ClickHouse базой данных.

## 📦 Установка

### Для пользователей:

#### Вариант 1: Из wheel файла (рекомендуется)
```bash
pip install dist/clickhouse_easy_connect_ivi-1.0.2-py3-none-any.whl
```

#### Вариант 2: Из архива
```bash
pip install clickhouse_easy_connect_ivi-1.0.2.tar.gz
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

Скопируйте `clickhouse_config.yaml.example` в `clickhouse_config.yaml` и заполните своими данными:

```yaml
host: your_clickhouse_host_here
port: 8123
username: your_username_here
password: your_password_here
database: your_database_here
```

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Загрузка из файла конфигурации
client = ClickHouseEasy(config_file='clickhouse_config.yaml')
df = client.query("SELECT * FROM your_table")
```

**⚠️ Важно**: Добавьте `clickhouse_config.yaml` в `.gitignore`, чтобы не попали учетные данные в репозиторий!

#### YAML конфигурация (рекомендуется)
Создайте локальный файл `clickhouse_config.yaml`:
```yaml
host: your_host
port: your_port
username: your_username
password: your_password
database: your_database
```

Или используйте функцию `setup_config`:
```python
from clickhouse_easy_connect_ivi import setup_config

# Создание шаблона конфигурации
config_path = setup_config('my_config.yaml')
# Отредактируйте созданный файл, указав ваши данные
```

#### JSON конфигурация
Создайте файл `config.json`:
```json
{
  "username": "your_username",
  "password": "your_password",
  "database": "your_database"
}
```

#### CSV конфигурация (устаревший формат)
Создайте файл `pass.csv`:
```
host___your_clickhouse_host
port___8123
database___your_database
username___your_username
password___your_password
```

```python
from clickhouse_easy_connect_ivi import ClickHouseEasy

# Загрузка из файла конфигурации (YAML - предпочтительный формат)
client = ClickHouseEasy(config_file='clickhouse_config.yaml')
# или из других форматов
client = ClickHouseEasy(config_file='config.json')
client = ClickHouseEasy(config_file='pass.csv')

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
from clickhouse_easy_connect_ivi import setup_config

# Создает пример файла конфигурации
config_path = setup_config('clickhouse_config.yaml')
# Файл будет создан с заглушками - отредактируйте его!
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
client.save_config('my_config.yaml')  # или 'my_config.json', 'my_config.csv'
```

## API

### ClickHouseEasy

#### Методы:
- `__init__(host, port, username, password, database, config_file)` - Инициализация
- `connect()` - Установка соединения
- `query(sql_query, **kwargs)` - Выполнение SELECT-запроса, возвращает DataFrame
- `execute(sql_command)` - Выполнение команды (INSERT, UPDATE, DELETE и т.д.)
- `close()` - Закрытие соединения
- `save_config(config_file, format)` - Сохранение конфигурации

### Функции:
- `create_client(host, port, username, password, database)` - Быстрое создание клиента
- `setup_config(config_file, username, password, database, host, port)` - Создание файла конфигурации

## Требования

- Python >= 3.7
- pandas >= 1.0.0
- clickhouse-connect >= 0.5.0
- PyYAML >= 5.0.0
