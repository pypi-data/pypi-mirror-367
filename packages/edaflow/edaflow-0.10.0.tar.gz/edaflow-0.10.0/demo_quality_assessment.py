"""
Demo script for assess_image_quality function
"""
import sys
import os
import tempfile
from PIL import Image
import random

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def create_sample_images():
    """Create sample images for testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create some test images
    for i in range(5):
        # Create a small test image
        img = Image.new('RGB', (100, 100), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        img.save(os.path.join(temp_dir, f'test_image_{i}.jpg'))
    
    # Create a grayscale image
    gray_img = Image.new('L', (100, 100), color=128)
    gray_img.save(os.path.join(temp_dir, 'grayscale_image.jpg'))
    
    return temp_dir

def test_assess_image_quality():
    """Test the assess_image_quality function."""
    try:
        import edaflow
        
        # Create sample images
        test_dir = create_sample_images()
        print(f"📁 Created test images in: {test_dir}")
        
        # Test the function
        print("\n🔍 Testing assess_image_quality function...")
        
        report = edaflow.assess_image_quality(
            test_dir,
            sample_size=10,  # Small sample for test
            verbose=True
        )
        
        print(f"\n✅ Function executed successfully!")
        print(f"📊 Quality Score: {report['quality_score']}/100")
        print(f"🖼️  Total Images: {report['total_images']}")
        print(f"🚨 Corrupted Images: {len(report['corrupted_images'])}")
        print(f"💡 Recommendations: {len(report['recommendations'])}")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing function: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_assess_image_quality()
    if success:
        print("\n🎉 assess_image_quality function is working correctly!")
    else:
        print("\n💥 Function test failed!")
