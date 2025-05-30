# test_imports.py
"""
Test script to verify all imports work correctly
"""

try:
    # Test new modules
    from src.tools.table_contents import get_table_contents_definition
    from src.tools.sql_query import get_sql_query_definition  
    from src.tools.enhancements import get_enhancements_definition
    
    print("✅ All new modules imported successfully!")
    
    # Test definitions exist
    print(f"✅ Table contents definition: {get_table_contents_definition['name']}")
    print(f"✅ SQL query definition: {get_sql_query_definition['name']}")
    print(f"✅ Enhancements definition: {get_enhancements_definition['name']}")
    
    print("\n🎉 All tests passed! The new features are ready to use.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
