# Посібник з відладки MCP сервера

## Швидкий старт

### 1. Відладка через VSCode
1. Відкрийте проект у VSCode
2. Перейдіть до панелі "Run and Debug" (Ctrl+Shift+D)
3. Виберіть одну з конфігурацій:
   - **Debug MCP Server (HTTP)** - основний сервер через HTTP
   - **Debug MCP Server (STDIO)** - основний сервер через STDIO
   - **Debug Fixed MCP Server** - сервер з виправленими імпортами
   - **Debug Minimal MCP Server** - мінімальний сервер
   - **Debug Server with Breakpoints** - з автоматичними breakpoints

### 2. Відладка через командний рядок
```bash
# Основний сервер через HTTP
python debug_run.py --server main --transport http

# Мінімальний сервер
python debug_run.py --server minimal --transport http

# З детальним логуванням
python debug_run.py --server main --transport http --verbose

# З іншим environment файлом
python debug_run.py --server main --env e19.env
```

## Доступні сервери

### 1. Основний сервер (`mcp_server.py`)
- Всі інструменти (20+)
- Повна функціональність
- **Проблема**: зависає на `tools/list`

### 2. Мінімальний сервер (`mcp_server_minimal.py`)
- 4 базових інструменти
- Спрощена логіка
- **Проблема**: також зависає на `tools/list`

### 3. Фіксований сервер (`mcp_server_fixed.py`)
- Fallback імпорти (tools/ → src/tools/)
- Автоматичне визначення шляхів
- **Проблема**: зависання залишається

### 4. Базовий сервер (`mcp_server_basic.py`)
- Без FastMCP, базова MCP бібліотека
- **Проблема**: помилки API

## Транспорти

### HTTP (рекомендовано для відладки)
```bash
python mcp_server.py --transport http --port 8000
```
- Легше тестувати через curl/Postman
- Детальніші логи
- Можна використовувати breakpoints

### STDIO (стандартний MCP)
```bash
python mcp_server.py --transport stdio
```
- Стандартний протокол MCP
- Складніше відлагоджувати
- Використовується в продакшені

## Тестування

### Тест через curl (HTTP)
```bash
# Запустити сервер
python mcp_server.py --transport http

# В іншому терміналі
curl -X POST http://localhost:8000/tools/list \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### Автоматичні тести
```bash
# Тест основного сервера
python test/test_mcp_client.py

# Тест мінімального сервера
python test/test_minimal_server.py

# Тест фіксованого сервера
python test/test_fixed_server.py
```

## Логування

### Файли логів
- `debug_server.log` - детальні логи сервера
- VSCode Debug Console - інтерактивні логи

### Рівні логування
```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Максимальна деталізація
logging.basicConfig(level=logging.INFO)   # Стандартна деталізація
```

## Відомі проблеми

### 1. Зависання tools/list
**Симптоми**: Сервер запускається, ініціалізується, але зависає на запиті `tools/list`

**Причина**: Проблема в бібліотеці FastMCP 1.9.1

**Обхідні шляхи**:
- Використовувати HTTP транспорт
- Спробувати базову MCP бібліотеку
- Оновити FastMCP до нової версії

### 2. Помилки імпортів
**Симптоми**: `ModuleNotFoundError` при запуску

**Рішення**: Використовувати `mcp_server_fixed.py` з fallback імпортами

### 3. API помилки
**Симптоми**: `TypeError` з `get_capabilities()` або `InitializationOptions`

**Рішення**: Перевірити версії MCP бібліотек

## Environment файли

### .env (за замовчуванням)
```bash
python mcp_server.py --env .env
```

### e19.env (SAP система E19)
```bash
python mcp_server.py --env e19.env
```

### btp_02.env (BTP система)
```bash
python mcp_server.py --env btp_02.env
```

## Корисні команди

### Перевірка версій
```bash
pip show mcp
pip show fastmcp
python --version
```

### Оновлення бібліотек
```bash
pip install --upgrade mcp
pip install --upgrade fastmcp
```

### Очистка кешу Python
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

## Поради з відладки

1. **Почніть з HTTP транспорту** - легше відлагоджувати
2. **Використовуйте мінімальний сервер** - менше змінних
3. **Увімкніть детальне логування** - `--verbose`
4. **Ставте breakpoints** у VSCode на критичних місцях
5. **Перевіряйте логи** в `debug_server.log`

## Контакти

При виникненні проблем:
1. Перевірте `debug_server.log`
2. Запустіть автоматичні тести
3. Спробуйте різні конфігурації серверів
4. Використовуйте VSCode debugger з breakpoints
