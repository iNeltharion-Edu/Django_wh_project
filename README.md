```markdown
# Django Inventory Management System

Проект на Django для управления складом и продуктами, поддерживающий роли пользователей (поставщики и потребители).
```

## Установка

### 1. Клонирование репозитория

Клонируйте репозиторий на свой локальный компьютер:

```bash
git clone https://github.com/iNeltharion/Django_wh_project.git
cd Django_wh_project
```

### 2. Установка зависимостей

Убедитесь, что у вас установлен Python 3.10 или новее. Установите виртуальное окружение и активируйте его:

```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

Установите необходимые пакеты:

```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных и выполнение миграций

Проект настроен для использования SQLite, поэтому дополнительных настроек для базы данных не требуется. Примените миграции, чтобы создать таблицы базы данных:

```bash
python manage.py migrate
```

### 4. Создание суперпользователя

Создайте суперпользователя для доступа к админке Django:

```bash
python manage.py createsuperuser
```

### 5. Запуск сервера разработки

Запустите сервер разработки:

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: `http://127.0.0.1:8000`

## API-эндпоинты

### Аутентификация

- **Получение токена**: `POST /auth/token/` с параметрами `username` и `password`.
- **Выход из системы**: `POST /auth/logout/` с токеном в заголовке `Authorization`.

### Пользователи

- **Создание пользователя**: `POST /users/` (требуется роль `supplier` или `consumer`).
  
### Склады

- **Создание склада**: `POST /warehouse/`
- **Просмотр складов**: `GET /warehouse/`

### Продукты

- **Добавить товар (только для поставщика)**: `POST /product/<id>/supply/`
- **Изъять товар (только для потребителя)**: `POST /product/<id>/consume/`
- **Получение товара по имени**: `GET /product/retrieve-product/?name=<название_товара>&quantity=<количество>`

## Тестирование

### 1. Загрузка начальных данных

Вы можете создать тестовые данные вручную через админку Django, которая доступна по адресу `http://127.0.0.1:8000/admin`. Для этого войдите под суперпользователем, созданным ранее.

### 2. Запросы через Postman или Curl

Для тестирования API вы можете использовать Postman или curl. 

#### Пример запроса для добавления товара (поставщик)

```bash
curl -X POST http://127.0.0.1:8000/product/1/supply/ \
     -H "Authorization: Token <ваш_токен>" \
     -H "Content-Type: application/json" \
     -d '{"quantity": 10}'
```

#### Пример запроса для изъятия товара (потребитель)

```bash
curl -X POST http://127.0.0.1:8000/product/1/consume/ \
     -H "Authorization: Token <ваш_токен>" \
     -H "Content-Type: application/json" \
     -d '{"quantity": 5}'
```

#### Пример запроса для получения товара по имени

```bash
curl -X GET "http://127.0.0.1:8000/product/retrieve-product/?name=Товар1&quantity=3" \
     -H "Authorization: Token <ваш_токен>"
```

## Замечания

- Убедитесь, что у пользователей назначены правильные роли (`supplier` или `consumer`).
- Поставщики могут только добавлять товары, а потребители — забирать их.