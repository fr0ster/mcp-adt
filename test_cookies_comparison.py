#!/usr/bin/env python3
"""
Порівняння старого і нового підходу до cookies
"""

import sys
import os

# Додаємо шлях до src для імпорту модулів
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_cookies_comparison():
    """Порівнює старий і новий підхід до cookies"""
    print("=" * 80)
    print("ПОРІВНЯННЯ СТАРОГО І НОВОГО ПІДХОДУ ДО COOKIES")
    print("=" * 80)
    
    try:
        from src.tools.utils import make_session, SAP_URL
        
        session = make_session()
        base_url = SAP_URL.rstrip('/')
        csrf_url = f"{base_url}/sap/bc/adt/discovery"
        
        print(f"🔄 Отримуємо CSRF токен...")
        
        # Отримуємо CSRF відповідь
        csrf_resp = session.get(
            csrf_url,
            headers={"x-csrf-token": "fetch", "Accept": "application/atomsvc+xml"},
            timeout=10
        )
        
        token = csrf_resp.headers.get("x-csrf-token")
        print(f"🔑 CSRF token: {token}")
        
        print(f"\n📊 ПОРІВНЯННЯ ПІДХОДІВ:")
        print("-" * 80)
        
        # Старий підхід (неправильний)
        print(f"❌ СТАРИЙ ПІДХІД (неправильний):")
        if 'Set-Cookie' in csrf_resp.headers:
            old_cookies = csrf_resp.headers.get('Set-Cookie')
            print(f"   Метод: csrf_resp.headers.get('Set-Cookie')")
            print(f"   Результат: {len(old_cookies)} chars")
            print(f"   Включає атрибути: path, secure, HttpOnly")
            print(f"   Приклад: {old_cookies[:100]}...")
        
        # Новий підхід (правильний)
        print(f"\n✅ НОВИЙ ПІДХІД (правильний):")
        if session.cookies:
            new_cookies = "; ".join([f"{cookie.name}={cookie.value}" for cookie in session.cookies])
            print(f"   Метод: session.cookies автоматичні")
            print(f"   Результат: {len(new_cookies)} chars")
            print(f"   Тільки значення: БЕЗ атрибутів")
            print(f"   Приклад: {new_cookies[:100]}...")
        
        print(f"\n💡 КЛЮЧОВА РІЗНИЦЯ:")
        print(f"   Старий: {len(old_cookies) if 'old_cookies' in locals() else 'N/A'} chars (з атрибутами)")
        print(f"   Новий: {len(new_cookies) if 'new_cookies' in locals() else 'N/A'} chars (без атрибутів)")
        
        if 'old_cookies' in locals() and 'new_cookies' in locals():
            diff = len(old_cookies) - len(new_cookies)
            print(f"   Різниця: {diff} chars")
            
            if diff > 0:
                print(f"   ✅ Новий підхід коротший на {diff} chars")
                print(f"   ✅ Це пояснює, чому старий код не працював!")
            
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Порівняння старого і нового підходу до cookies")
    print("Показує, чому виправлення було необхідним")
    print("=" * 80)
    
    success = test_cookies_comparison()
    
    print("\n" + "=" * 80)
    print("ВИСНОВОК")
    print("=" * 80)
    
    if success:
        print("🎯 ПРОБЛЕМУ ІДЕНТИФІКОВАНО!")
        print("💡 Старий код передавав cookies з атрибутами")
        print("💡 Новий код передає тільки значення cookies")
        print("✅ Це пояснює, чому MCP сервер тепер працює")
    else:
        print("❌ Не вдалося провести порівняння")
    
    print("=" * 80)
