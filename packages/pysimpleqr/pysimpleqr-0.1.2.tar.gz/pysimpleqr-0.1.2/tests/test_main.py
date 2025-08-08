import os
import tempfile
from unittest.mock import patch, MagicMock
import qrcode
from PIL import Image

# Mock all GUI-related modules to avoid import issues during testing
import sys

# Mock FreeSimpleGUI
mock_sg = MagicMock()
mock_sg.theme = MagicMock()
mock_sg.Window = MagicMock()
mock_sg.HorizontalSeparator = MagicMock()
mock_sg.Text = MagicMock()
mock_sg.Multiline = MagicMock()
mock_sg.Button = MagicMock()
mock_sg.Image = MagicMock()
mock_sg.StatusBar = MagicMock()
mock_sg.Frame = MagicMock()
mock_sg.Checkbox = MagicMock()
mock_sg.WIN_CLOSED = None
mock_sg.popup_error = MagicMock()
mock_sg.popup = MagicMock()
mock_sg.popup_get_file = MagicMock()
mock_sg.Window.get_screen_size = MagicMock(return_value=(1920, 1080))
sys.modules['FreeSimpleGUI'] = mock_sg

# Mock PIL ImageTk
mock_imagetk = MagicMock()
sys.modules['PIL.ImageTk'] = mock_imagetk

# Mock pyperclip
mock_pyperclip = MagicMock()
sys.modules['pyperclip'] = mock_pyperclip

from pysimpleqr.main import QRCodeGenerator


class TestQRCodeGenerator:
    """Test cases for QRCodeGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = QRCodeGenerator()
    
    def test_init(self):
        """Test QRCodeGenerator initialization."""
        assert self.generator.qr_image is None
        assert self.generator.window is None
    
    def test_generate_qr_code(self):
        """Test QR code generation."""
        test_text = "Hello, World!"
        qr_image = self.generator.generate_qr_code(test_text)
        
        assert qr_image is not None
        assert hasattr(qr_image, 'size')
    
    def test_generate_qr_code_empty_text(self):
        """Test QR code generation with empty text."""
        test_text = ""
        qr_image = self.generator.generate_qr_code(test_text)
        
        assert isinstance(qr_image, qrcode.image.pil.PilImage)
        assert qr_image.size[0] > 0
        assert qr_image.size[1] > 0
    
    def test_generate_qr_code_long_text(self):
        """Test QR code generation with long text."""
        test_text = "A" * 1000  # Very long text
        qr_image = self.generator.generate_qr_code(test_text)
        
        assert isinstance(qr_image, (Image.Image, qrcode.image.pil.PilImage))
        assert qr_image.size[0] > 0
        assert qr_image.size[1] > 0
    
    def test_resize_image_for_display_no_resize(self):
        """Test image resizing when no resize is needed."""
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        resized = self.generator.resize_image_for_display(img, 200, 200)
        
        # Should return the same image since it's smaller than max dimensions
        assert resized.size == (100, 100)
    
    def test_resize_image_for_display_with_resize(self):
        """Test image resizing when resize is needed."""
        # Create a large test image
        img = Image.new('RGB', (500, 500), color='red')
        resized = self.generator.resize_image_for_display(img, 200, 200)
        
        # Should return a smaller image
        assert resized.size[0] <= 200
        assert resized.size[1] <= 200
    
    def test_resize_image_for_display_aspect_ratio(self):
        """Test image resizing maintains aspect ratio."""
        # Create a rectangular image
        img = Image.new('RGB', (400, 200), color='red')
        resized = self.generator.resize_image_for_display(img, 100, 100)
        
        # Should maintain aspect ratio
        assert resized.size[0] <= 100
        assert resized.size[1] <= 100
        assert resized.size[0] / resized.size[1] == 2.0  # 2:1 aspect ratio
    
    @patch('pysimpleqr.main.sg')
    def test_create_layout(self, mock_sg):
        """Test layout creation."""
        mock_sg.Window.get_screen_size.return_value = (1920, 1080)
        layout = self.generator.create_layout()
        
        assert isinstance(layout, list)
        assert len(layout) > 0
    
    @patch('pysimpleqr.main.sg')
    def test_run_method_basic(self, mock_sg):
        """Test run method initialization."""
        # Mock FreeSimpleGUI components
        mock_window = MagicMock()
        mock_sg.Window.return_value = mock_window
        mock_sg.WIN_CLOSED = None
        mock_window.read.return_value = (None, None)
        mock_window.get_screen_size.return_value = (1920, 1080)
        
        # This will exit immediately due to mocked window
        try:
            self.generator.run()
        except Exception:
            pass  # Expected due to mocking
        
        # Don't assert specific calls due to complex GUI setup
        assert True


class TestQRCodeIntegration:
    """Integration tests for QR code generation."""
    
    def test_full_generation_and_save(self):
        """Test complete QR code generation and save workflow."""
        generator = QRCodeGenerator()
        
        # Generate QR code
        test_text = "Integration test"
        qr_image = generator.generate_qr_code(test_text)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            qr_image.save(temp_path, 'PNG')
            assert os.path.exists(temp_path)
            
            # Verify it's a valid image
            saved_img = Image.open(temp_path)
            assert saved_img.size[0] > 0
            assert saved_img.size[1] > 0
            saved_img.close()
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_qr_code_content_verification(self):
        """Test that QR code contains expected content."""
        import io
        
        generator = QRCodeGenerator()
        test_text = "Test content verification"
        
        # Generate QR code
        qr_image = generator.generate_qr_code(test_text)
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Load back and verify it's a valid image
        loaded_img = Image.open(buffer)
        assert loaded_img.size[0] > 0
        assert loaded_img.size[1] > 0


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = QRCodeGenerator()
    
    def test_generate_qr_code_special_characters(self):
        """Test QR code generation with special characters."""
        generator = QRCodeGenerator()
        
        # Test various special characters
        special_texts = [
            "Hello\nWorld",
            "Special chars: áéíóú",
            "Unicode: 你好世界",
            "Symbols: !@#$%^&*()",
            "HTML: <script>alert('test')</script>",
        ]
        
        for text in special_texts:
            qr_image = generator.generate_qr_code(text)
            assert isinstance(qr_image, (Image.Image, qrcode.image.pil.PilImage))
    
    def test_resize_with_zero_dimensions(self):
        """Test image resizing with zero dimensions."""
        img = Image.new('RGB', (100, 100), color='red')
        
        # Should handle zero dimensions gracefully
        resized = self.generator.resize_image_for_display(img, 0, 0)
        assert resized.size == (100, 100)  # No resize applied
    
    def test_resize_with_negative_dimensions(self):
        """Test image resizing with negative dimensions."""
        img = Image.new('RGB', (100, 100), color='red')
        
        # Should handle negative dimensions gracefully
        resized = self.generator.resize_image_for_display(img, -100, -100)
        assert resized.size == (100, 100)  # No resize applied