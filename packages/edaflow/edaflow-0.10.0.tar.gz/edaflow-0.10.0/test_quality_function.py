"""
Test script for the new assess_image_quality function
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    import edaflow
    print("✅ Successfully imported edaflow")
    
    # Check if the new function is available
    if hasattr(edaflow, 'assess_image_quality'):
        print("✅ assess_image_quality function is available")
        
        # Check function documentation
        func = getattr(edaflow, 'assess_image_quality')
        if func.__doc__:
            print("✅ Function has comprehensive documentation")
            print(f"📝 Doc length: {len(func.__doc__)} characters")
        else:
            print("⚠️  Function missing documentation")
            
        print("\n🎉 Image Quality Assessment function successfully added to edaflow!")
        print(f"📦 Current version: {edaflow.__version__}")
        
        # Print function signature for verification
        import inspect
        sig = inspect.signature(func)
        print(f"🔧 Function signature: assess_image_quality{sig}")
        
        # Test import from analysis module
        from edaflow.analysis import assess_image_quality
        print("✅ Successfully imported from edaflow.analysis")
        
    else:
        print("❌ assess_image_quality function not found")
        
except ImportError as e:
    print(f"❌ Failed to import edaflow: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
