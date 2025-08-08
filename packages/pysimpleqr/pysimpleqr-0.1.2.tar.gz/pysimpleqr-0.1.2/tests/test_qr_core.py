"""Tests for QR code core functionality."""

import io
import tempfile

import pytest
import qrcode
from PIL import Image

from pysimpleqr.qr_core import QRCodeCore


class TestQRCodeCore:
    """Test cases for QRCodeCore class."""
    
    def test_generate_qr_code_basic(self):
        """Test basic QR code generation."""
        test_text = "Hello, World!"
        qr_image = QRCodeCore.generate_qr_code(test_text)
        
        assert hasattr(qr_image, 'size')
        assert qr_image.size[0] > 0
        assert qr_image.size[1] > 0
    
    def test_generate_qr_code_empty_text(self):
        """Test QR code generation with empty text."""
        test_text = ""
        qr_image = QRCodeCore.generate_qr_code(test_text)
        
        assert hasattr(qr_image, 'size')
        assert qr_image.size[0] > 0
        assert qr_image.size[1] > 0
    
    def test_generate_qr_code_long_text(self):
        """Test QR code generation with long text."""
        test_text = "A" * 1000  # Very long text
        qr_image = QRCodeCore.generate_qr_code(test_text)
        
        assert hasattr(qr_image, 'size')
        assert qr_image.size[0] > 0
        assert qr_image.size[1] > 0
    
    def test_generate_qr_code_special_characters(self):
        """Test QR code generation with special characters."""
        special_texts = [
            "Hello\nWorld",
            "Special chars: áéíóú",
            "Unicode: 你好世界",
            "Symbols: !@#$%^&*()",
            "HTML: <script>alert('test')</script>",
        ]
        
        for text in special_texts:
            qr_image = QRCodeCore.generate_qr_code(text)
            assert hasattr(qr_image, 'size')
    
    def test_resize_image_no_resize_needed(self):
        """Test image resizing when no resize is needed."""
        img = Image.new('RGB', (100, 100), color='red')
        resized = QRCodeCore.resize_image_for_display(img, 200, 200)
        
        # Should return the same image since it's smaller than max dimensions
        assert resized.size == (100, 100)
    
    def test_resize_image_with_resize(self):
        """Test image resizing when resize is needed."""
        img = Image.new('RGB', (500, 500), color='red')
        resized = QRCodeCore.resize_image_for_display(img, 200, 200)
        
        # Should return a smaller image
        assert resized.size[0] <= 200
        assert resized.size[1] <= 200
    
    def test_resize_image_maintains_aspect_ratio(self):
        """Test image resizing maintains aspect ratio."""
        # Create a rectangular image (2:1 aspect ratio)
        img = Image.new('RGB', (400, 200), color='red')
        resized = QRCodeCore.resize_image_for_display(img, 100, 100)
        
        # Should maintain aspect ratio
        assert resized.size[0] <= 100
        assert resized.size[1] <= 100
        assert abs((resized.size[0] / resized.size[1]) - 2.0) < 0.1  # 2:1 aspect ratio
    
    def test_resize_image_zero_dimensions(self):
        """Test image resizing with zero dimensions."""
        img = Image.new('RGB', (100, 100), color='red')
        resized = QRCodeCore.resize_image_for_display(img, 0, 0)
        
        # Should handle zero dimensions gracefully
        assert resized.size == (100, 100)
    
    def test_resize_image_negative_dimensions(self):
        """Test image resizing with negative dimensions."""
        img = Image.new('RGB', (100, 100), color='red')
        resized = QRCodeCore.resize_image_for_display(img, -100, -100)
        
        # Should handle negative dimensions gracefully
        assert resized.size == (100, 100)
    
    
    def test_save_qr_code_invalid_path(self):
        """Test QR code saving with invalid path."""
        import tempfile
        from unittest.mock import patch
        
        img = QRCodeCore.generate_qr_code("Test save")
        
        # Mock the save operation to simulate failure
        with patch('PIL.Image.Image.save', side_effect=IOError("Permission denied")):
            invalid_path = "C:\\invalid\\path\\test.png"
            result = QRCodeCore.save_qr_code(img, invalid_path)
            assert result is False
    
    def test_get_qr_code_bytes(self):
        """Test getting QR code as bytes."""
        img = QRCodeCore.generate_qr_code("Test bytes")
        img_bytes = QRCodeCore.get_qr_code_bytes(img)
        
        assert isinstance(img_bytes, bytes)
        assert len(img_bytes) > 0
        
        # Verify it's valid image data
        buffer = io.BytesIO(img_bytes)
        loaded_img = Image.open(buffer)
        assert loaded_img.size[0] > 0
        assert loaded_img.size[1] > 0
    
    
    def test_different_image_sizes(self):
        """Test QR code generation with different text lengths."""
        test_cases = [
            ("Short", 50),
            ("Medium length text" * 10, 200),
            ("Very long text" * 100, 500),
        ]
        
        for text, max_size in test_cases:
            qr_image = QRCodeCore.generate_qr_code(text)
            resized = QRCodeCore.resize_image_for_display(qr_image, max_size, max_size)
            
            assert resized.size[0] <= max_size
            assert resized.size[1] <= max_size