# Как создать базу данных Supabase

## Вариант 1: Использовать существующий проект Supabase

У вас уже есть проект Supabase! Нужно только получить правильный Connection String.

### Шаг 1: Откройте Supabase Dashboard
1. Зайдите на https://supabase.com
2. Войдите в свой аккаунт
3. Откройте проект `ydcavbizdrfidujtfekr`

### Шаг 2: Получите Connection Pooling URL
1. В левом меню выберите **Settings** → **Database**
2. Прокрутите до секции **Connection string**
3. Выберите вкладку **Transaction** (или Session)
4. Скопируйте URI

Должно получиться:
```
postgresql://postgres.ydcavbizdrfidujtfekr:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

### Шаг 3: Замените в .env
Замените в файле `.env` строку `DATABASE_URL` на:
```
DATABASE_URL=postgresql://postgres.ydcavbizdrfidujtfekr:Axisline2026@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**Обратите внимание**: порт изменился с `5432` на `6543`!

---

## Вариант 2: Создать новый проект Supabase

### Шаг 1: Создайте новый проект
1. Зайдите на https://supabase.com/dashboard
2. Нажмите **New Project**
3. Заполните:
   - **Name**: TrendScout
   - **Database Password**: (придумайте надежный пароль)
   - **Region**: выберите ближайший к вам
4. Нажмите **Create new project**
5. Подождите 2-3 минуты пока проект создается

### Шаг 2: Получите Connection String
1. Перейдите в **Settings** → **Database**
2. Найдите **Connection string**
3. Выберите вкладку **Transaction**
4. Скопируйте URI
5. Замените `[YOUR-PASSWORD]` на пароль, который вы указали при создании

### Шаг 3: Настройте схему БД

#### Способ A: Через Supabase SQL Editor (рекомендуется)
1. Откройте **SQL Editor** в Supabase Dashboard
2. Создайте новый запрос
3. Скопируйте и выполните SQL из файла `supabase/migrations/` (если есть в оригинальном репо)

#### Способ B: Через Alembic миграции
```bash
cd server
alembic upgrade head
```

### Шаг 4: Обновите .env
Замените `DATABASE_URL` в `.env` на ваш новый connection string

---

## Вариант 3: Локальная PostgreSQL (для разработки)

### Установка PostgreSQL

#### Windows:
1. Скачайте PostgreSQL 15: https://www.postgresql.org/download/windows/
2. Установите с настройками по умолчанию
3. Запомните пароль для пользователя `postgres`

#### macOS:
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Linux:
```bash
sudo apt-get update
sudo apt-get install postgresql-15 postgresql-contrib-15
```

### Создание базы данных

1. Откройте терминал/командную строку
2. Подключитесь к PostgreSQL:
```bash
psql -U postgres
```

3. Создайте базу данных и расширение:
```sql
CREATE DATABASE trendscout;
\c trendscout
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

4. Обновите `.env`:
```
DATABASE_URL=postgresql://postgres:ВАШ_ПАРОЛЬ@localhost:5432/trendscout
```

5. Запустите миграции:
```bash
cd server
alembic upgrade head
```

---

## Проверка подключения

После настройки БД проверьте подключение:

```bash
cd server
python -c "from app.db.database import engine; print(engine.connect())"
```

Если видите `<sqlalchemy.engine.base.Connection object>` - подключение работает!

---

## Частые проблемы

### Connection timeout
- **Причина**: Используется Direct Connection вместо Pooling
- **Решение**: Используйте порт `6543` вместо `5432`

### IPv6 блокировка
- **Причина**: Windows/Firewall блокирует IPv6
- **Решение**: Используйте Connection Pooling (автоматически использует IPv4)

### Password authentication failed
- **Причина**: Неправильный пароль в DATABASE_URL
- **Решение**: Проверьте пароль в Supabase Dashboard → Settings → Database

### Extension "vector" does not exist
- **Причина**: Расширение pgvector не установлено
- **Решение**: Выполните `CREATE EXTENSION vector;` в SQL Editor

---

## Следующие шаги

После настройки БД:

1. Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Заполните все переменные окружения

3. Запустите миграции:
```bash
cd server
alembic upgrade head
```

4. Запустите сервер:
```bash
cd server
uvicorn app.main:app --reload
```

Готово! 🎉
