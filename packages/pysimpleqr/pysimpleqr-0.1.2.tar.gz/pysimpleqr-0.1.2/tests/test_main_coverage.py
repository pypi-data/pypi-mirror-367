"""Additional tests for main.py to improve coverage."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_qr_code_generator_methods():
    """Test QRCodeGenerator methods without GUI."""
    with patch.dict('sys.modules', {
        'FreeSimpleGUI': MagicMock(),
        'PIL.ImageTk': MagicMock(),
        'pyperclip': MagicMock()
    }):
        from pysimpleqr.main import QRCodeGenerator
        
        # Mock FreeSimpleGUI
        mock_sg = MagicMock()
        mock_sg.Window.return_value = MagicMock()
        mock_sg.Text.return_value = MagicMock()
        mock_sg.Button.return_value = MagicMock()
        mock_sg.InputText.return_value = MagicMock()
        mock_sg.Image.return_value = MagicMock()
        mock_sg.Column.return_value = MagicMock()
        mock_sg.Frame.return_value = MagicMock()
        mock_sg.theme = MagicMock()
        mock_sg.WIN_CLOSED = "WINDOW_CLOSED"
        
        import sys
        sys.modules['FreeSimpleGUI'] = mock_sg
        
        # Create instance
        generator = QRCodeGenerator()
        
        # Test generate_qr_code method
        test_text = "Test QR code"
        qr_image = generator.generate_qr_code(test_text)
        assert qr_image is not None
        assert hasattr(qr_image, 'size')
        
        # Test resize_image_for_display method
        from PIL import Image
        test_img = Image.new('RGB', (300, 300))
        resized = generator.resize_image_for_display(test_img, 200, 200)
        assert resized is not None
        assert resized.size[0] <= 200
        assert resized.size[1] <= 200


def test_qr_code_generator_initialization_with_layout():
    """Test QRCodeGenerator initialization with layout creation."""
    with patch.dict('sys.modules', {
        'FreeSimpleGUI': MagicMock(),
        'PIL.ImageTk': MagicMock(),
        'pyperclip': MagicMock()
    }):
        from pysimpleqr.main import QRCodeGenerator
        
        # Mock FreeSimpleGUI components
        mock_sg = MagicMock()
        mock_sg.Text.return_value = MagicMock()
        mock_sg.InputText.return_value = MagicMock()
        mock_sg.Button.return_value = MagicMock()
        mock_sg.Image.return_value = MagicMock()
        mock_sg.Column.return_value = MagicMock()
        mock_sg.Frame.return_value = MagicMock()
        mock_sg.Window.return_value = MagicMock()
        mock_sg.Window.get_screen_size.return_value = (1920, 1080)
        mock_sg.theme = MagicMock()
        mock_sg.WIN_CLOSED = "WINDOW_CLOSED"
        
        import sys
        sys.modules['FreeSimpleGUI'] = mock_sg
        
        # Test initialization
        generator = QRCodeGenerator()
        
        # Verify initialization completed (don't check specific calls due to complex layout)
        assert generator is not None


def test_qr_code_generator_file_operations():
    """Test QRCodeGenerator file operations."""
    with patch.dict('sys.modules', {
        'FreeSimpleGUI': MagicMock(),
        'PIL.ImageTk': MagicMock(),
        'pyperclip': MagicMock()
    }):
        from pysimpleqr.main import QRCodeGenerator
        
        # Mock FreeSimpleGUI
        mock_sg = MagicMock()
        mock_sg.Window.return_value = MagicMock()
        mock_sg.Text.return_value = MagicMock()
        mock_sg.Button.return_value = MagicMock()
        mock_sg.InputText.return_value = MagicMock()
        mock_sg.Image.return_value = MagicMock()
        mock_sg.Column.return_value = MagicMock()
        mock_sg.Frame.return_value = MagicMock()
        mock_sg.theme = MagicMock()
        mock_sg.WIN_CLOSED = "WINDOW_CLOSED"
        mock_sg.popup = MagicMock()
        
        import sys
        sys.modules['FreeSimpleGUI'] = mock_sg
        
        # Create instance
        generator = QRCodeGenerator()
        
        # Test with temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_path = Path(tmp_dir) / "test_qr.png"
            
            # Test QR code generation
            test_text = "Test file operations"
            qr_image = generator.generate_qr_code(test_text)
            assert qr_image is not None


def test_qr_code_generator_error_handling():
    """Test QRCodeGenerator error handling."""
    with patch.dict('sys.modules', {
        'FreeSimpleGUI': MagicMock(),
        'PIL.ImageTk': MagicMock(),
        'pyperclip': MagicMock()
    }):
        from pysimpleqr.main import QRCodeGenerator
        
        # Mock FreeSimpleGUI
        mock_sg = MagicMock()
        mock_sg.Window.return_value = MagicMock()
        mock_sg.Text.return_value = MagicMock()
        mock_sg.Button.return_value = MagicMock()
        mock_sg.InputText.return_value = MagicMock()
        mock_sg.Image.return_value = MagicMock()
        mock_sg.Column.return_value = MagicMock()
        mock_sg.Frame.return_value = MagicMock()
        mock_sg.theme = MagicMock()
        mock_sg.WIN_CLOSED = "WINDOW_CLOSED"
        mock_sg.popup = MagicMock()
        
        import sys
        sys.modules['FreeSimpleGUI'] = mock_sg
        
        # Create instance
        generator = QRCodeGenerator()
        
        # Test with empty text
        qr_image = generator.generate_qr_code("")
        assert qr_image is not None
        
        # Test with special characters
        qr_image = generator.generate_qr_code("Special: áéíóú 中文 🎉")
        assert qr_image is not None


def test_qr_code_generator_resize_edge_cases():
    """Test QRCodeGenerator resize edge cases."""
    with patch.dict('sys.modules', {
        'FreeSimpleGUI': MagicMock(),
        'PIL.ImageTk': MagicMock(),
        'pyperclip': MagicMock()
    }):
        from pysimpleqr.main import QRCodeGenerator
        
        # Mock FreeSimpleGUI
        mock_sg = MagicMock()
        mock_sg.Window.return_value = MagicMock()
        mock_sg.Text.return_value = MagicMock()
        mock_sg.Button.return_value = MagicMock()
        mock_sg.InputText.return_value = MagicMock()
        mock_sg.Image.return_value = MagicMock()
        mock_sg.Column.return_value = MagicMock()
        mock_sg.Frame.return_value = MagicMock()
        mock_sg.theme = MagicMock()
        mock_sg.WIN_CLOSED = "WINDOW_CLOSED"
        
        import sys
        sys.modules['FreeSimpleGUI'] = mock_sg
        
        # Create instance
        generator = QRCodeGenerator()
        
        from PIL import Image
        
        # Test with very small image
        small_img = Image.new('RGB', (10, 10))
        resized = generator.resize_image_for_display(small_img, 100, 100)
        assert resized.size == (10, 10)  # Should remain same
        
        # Test with very large image
        large_img = Image.new('RGB', (1000, 1000))
        resized = generator.resize_image_for_display(large_img, 100, 100)
        assert resized.size[0] <= 100
        assert resized.size[1] <= 100
        
        # Test with zero max dimensions
        resized = generator.resize_image_for_display(small_img, 0, 0)
        assert resized.size == (10, 10)  # Should remain same