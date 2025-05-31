#!/usr/bin/env python3
"""
Дебаг тест для MCP сервера
"""

import sys
import os

# Додаємо шлях до src для імпорту модулів
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_import_debug():
    """Тестує, який код імпортується"""
    print("=" * 80)
    print("ДЕБАГ ТЕСТ ІМПОРТУ")
    print("=" * 80)
    
    try:
        # Імпортуємо функцію
        from src.tools.package_structure import get_package_structure
        
        # Перевіряємо docstring
        print(f"📋 Docstring функції:")
        print(f"   {get_package_structure.__doc__[:200]}...")
        
        # Перевіряємо код функції
        import inspect
        source_lines = inspect.getsourcelines(get_package_structure)
        source_code = ''.join(source_lines[0])
        
        print(f"\n🔍 Перевіряємо ключові рядки:")
        
        # Перевіряємо Accept заголовок
        if 'application/vnd.sap.as+xml' in source_code:
            print("✅ Accept заголовок: ВИПРАВЛЕНИЙ (SAP-специфічний)")
        elif 'application/xml, application/json' in source_code:
            print("❌ Accept заголовок: СТАРИЙ (загальний)")
        else:
            print("❓ Accept заголовок: НЕВІДОМИЙ")
        
        # Перевіряємо cookies
        if 'session.cookies' in source_code and 'cookie.name}={cookie.value}' in source_code:
            print("✅ Cookies: ВИПРАВЛЕНІ (автоматичні без атрибутів)")
        elif 'Set-Cookie' in source_code:
            print("❌ Cookies: СТАРІ (з атрибутами)")
        else:
            print("❓ Cookies: НЕВІДОМІ")
        
        # Перевіряємо коментарі
        if 'Working version using requests automatic cookie handling' in source_code:
            print("✅ Коментарі: ВИПРАВЛЕНІ")
        else:
            print("❌ Коментарі: СТАРІ")
        
        print(f"\n📄 Перші 10 рядків функції:")
        for i, line in enumerate(source_lines[0][:10]):
            print(f"   {i+1:2d}: {line.rstrip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_call():
    """Тестує прямий виклик функції"""
    print("\n" + "=" * 80)
    print("ТЕСТ ПРЯМОГО ВИКЛИКУ")
    print("=" * 80)
    
    try:
        from src.tools.package_structure import get_package_structure
        
        print("🔄 Викликаємо get_package_structure('ZOK_LAB')...")
        result = get_package_structure('ZOK_LAB')
        
        print(f"✅ Результат: {len(result)} об'єктів")
        return True, len(result)
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False, 0

if __name__ == "__main__":
    print("Дебаг тест для MCP сервера")
    print("Перевіряє, який код імпортується")
    print("=" * 80)
    
    # Тест імпорту
    import_ok = test_import_debug()
    
    # Тест виклику
    call_ok, count = test_direct_call()
    
    print("\n" + "=" * 80)
    print("ПІДСУМОК ДЕБАГУ")
    print("=" * 80)
    
    if import_ok and call_ok:
        print("🎉 КОД ВИПРАВЛЕНИЙ І ПРАЦЮЄ!")
        print(f"📦 Отримано {count} об'єктів")
        print("💡 Проблема може бути в кешуванні MCP сервера")
        print("💡 Спробуйте перезапустити MCP сервер")
    elif import_ok:
        print("⚠️ Код виправлений, але є помилки виконання")
    else:
        print("❌ Проблеми з імпортом коду")
    
    print("=" * 80)
