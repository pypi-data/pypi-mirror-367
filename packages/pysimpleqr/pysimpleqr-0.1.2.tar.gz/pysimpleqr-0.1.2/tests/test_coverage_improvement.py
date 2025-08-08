"""Additional tests to improve code coverage."""

import io
import os
import tempfile
from PIL import Image

from pysimpleqr.qr_core import QRCodeCore


class TestQRCoreCoverage:
    """Additional tests for QRCodeCore to improve coverage."""
    
    def test_save_qr_code_to_file(self):
        """Test saving QR code to file."""
        test_text = "Test saving"
        qr_image = QRCodeCore.generate_qr_code(test_text)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            # Test saving
            qr_image.save(temp_path, 'PNG')
            
            # Verify file exists and is valid
            assert os.path.exists(temp_path)
            saved_image = Image.open(temp_path)
            assert saved_image.size[0] > 0
            assert saved_image.size[1] > 0
            saved_image.close()
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_qr_code_different_sizes(self):
        """Test QR code generation with different text sizes."""
        test_cases = [
            "",  # Empty
            "A",  # Single character
            "Short text",  # Short
            "Medium length text with some numbers 12345",  # Medium
            "Very long text " * 100,  # Very long
        ]
        
        for text in test_cases:
            qr_image = QRCodeCore.generate_qr_code(text)
            assert qr_image.size[0] > 0
            assert qr_image.size[1] > 0
    
    def test_resize_image_edge_cases(self):
        """Test image resizing with edge cases."""
        # Create test image
        test_img = Image.new('RGB', (300, 200), color='blue')
        
        # Test case 1: Max dimensions larger than image
        resized = QRCodeCore.resize_image_for_display(test_img, 500, 400)
        assert resized.size == (300, 200)  # Should keep original size
        
        # Test case 2: Max width only constraint
        resized = QRCodeCore.resize_image_for_display(test_img, 150, 400)
        assert resized.size[0] == 150
        assert resized.size[1] == 100  # Maintains aspect ratio
        
        # Test case 3: Max height only constraint
        resized = QRCodeCore.resize_image_for_display(test_img, 500, 100)
        assert resized.size[1] == 100
        assert resized.size[0] == 150  # Maintains aspect ratio
        
        # Test case 4: Both dimensions constrained
        resized = QRCodeCore.resize_image_for_display(test_img, 100, 100)
        assert resized.size[0] <= 100
        assert resized.size[1] <= 100
    
    def test_resize_square_image(self):
        """Test resizing a square image."""
        square_img = Image.new('RGB', (100, 100), color='green')
        
        # Should maintain square aspect ratio
        resized = QRCodeCore.resize_image_for_display(square_img, 50, 50)
        assert resized.size == (50, 50)
    
    def test_resize_very_wide_image(self):
        """Test resizing a very wide image."""
        wide_img = Image.new('RGB', (1000, 100), color='red')
        
        resized = QRCodeCore.resize_image_for_display(wide_img, 200, 200)
        assert resized.size[0] == 200
        assert resized.size[1] == 20  # Maintains 10:1 aspect ratio
    
    def test_resize_very_tall_image(self):
        """Test resizing a very tall image."""
        tall_img = Image.new('RGB', (100, 1000), color='yellow')
        
        resized = QRCodeCore.resize_image_for_display(tall_img, 200, 200)
        assert resized.size[1] == 200
        assert resized.size[0] == 20  # Maintains 1:10 aspect ratio
    
    def test_qr_code_unicode_content(self):
        """Test QR code generation with various Unicode content."""
        unicode_texts = [
            "English text",
            "Español con acentos",
            "中文字符",
            "العربية",
            "Русский текст",
            "日本語",
            "🎉🚀🌟 Emojis",
            "Mixed: English + 中文 + Русский + 🎉",
        ]
        
        for text in unicode_texts:
            qr_image = QRCodeCore.generate_qr_code(text)
            assert qr_image.size[0] > 0
            assert qr_image.size[1] > 0
    
    def test_qr_code_content_types(self):
        """Test QR code generation with different content types."""
        content_types = [
            "https://www.example.com",  # URL
            "mailto:test@example.com",  # Email
            "tel:+1234567890",  # Phone
            "SMS:+1234567890:Hello",  # SMS
            "geo:37.7749,-122.4194",  # GPS coordinates
            "WIFI:T:WPA;S:MyNetwork;P:password;;",  # WiFi
            "BEGIN:VCARD\nFN:John Doe\nEND:VCARD",  # vCard
        ]
        
        for content in content_types:
            qr_image = QRCodeCore.generate_qr_code(content)
            assert qr_image.size[0] > 0
            assert qr_image.size[1] > 0


class TestQRCoreImageOperations:
    """Test image operations in QRCodeCore."""
    
    def test_resize_with_zero_max_dimensions(self):
        """Test resize with zero maximum dimensions."""
        img = Image.new('RGB', (100, 100), color='purple')
        
        # Zero width
        resized = QRCodeCore.resize_image_for_display(img, 0, 100)
        assert resized.size == (100, 100)  # Should return original
        
        # Zero height
        resized = QRCodeCore.resize_image_for_display(img, 100, 0)
        assert resized.size == (100, 100)  # Should return original
        
        # Both zero
        resized = QRCodeCore.resize_image_for_display(img, 0, 0)
        assert resized.size == (100, 100)  # Should return original
    
    def test_resize_with_negative_dimensions(self):
        """Test resize with negative maximum dimensions."""
        img = Image.new('RGB', (100, 100), color='orange')
        
        # Negative width
        resized = QRCodeCore.resize_image_for_display(img, -100, 50)
        assert resized.size == (100, 100)  # Should return original
        
        # Negative height
        resized = QRCodeCore.resize_image_for_display(img, 50, -100)
        assert resized.size == (100, 100)  # Should return original
        
        # Both negative
        resized = QRCodeCore.resize_image_for_display(img, -100, -100)
        assert resized.size == (100, 100)  # Should return original
    
    def test_image_to_bytes_conversion(self):
        """Test converting QR code image to bytes."""
        test_text = "Bytes conversion test"
        qr_image = QRCodeCore.generate_qr_code(test_text)
        
        # Convert to bytes using BytesIO
        buffer = io.BytesIO()
        qr_image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        
        assert len(image_bytes) > 0
        assert image_bytes[:8] == b'\x89PNG\r\n\x1a\n'  # PNG header
        
        # Verify we can load the image back
        buffer.seek(0)
        loaded_image = Image.open(buffer)
        assert loaded_image.size == qr_image.size
        loaded_image.close()
