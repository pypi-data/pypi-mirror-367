"""Unit tests for main.py QRCodeGenerator class."""

from unittest.mock import patch, MagicMock


class TestQRCodeGeneratorUnit:
    """Unit tests for QRCodeGenerator without GUI dependencies."""
    
    def test_generate_qr_code_method(self):
        """Test QR code generation method."""
        with patch.dict('sys.modules', {
            'FreeSimpleGUI': MagicMock(),
            'PIL.ImageTk': MagicMock(),
            'pyperclip': MagicMock()
        }):
            from pysimpleqr.main import QRCodeGenerator
            
            # Create minimal mock for FreeSimpleGUI
            mock_sg = MagicMock()
            mock_sg.Text = MagicMock()
            mock_sg.InputText = MagicMock()
            mock_sg.Button = MagicMock()
            mock_sg.Image = MagicMock()
            mock_sg.Column = MagicMock()
            mock_sg.Frame = MagicMock()
            mock_sg.Window = MagicMock()
            mock_sg.theme = MagicMock()
            
            import sys
            sys.modules['FreeSimpleGUI'] = mock_sg
            
            generator = QRCodeGenerator()
            
            # Test QR code generation
            test_text = "Hello World"
            qr_image = generator.generate_qr_code(test_text)
            
            assert qr_image is not None
            assert hasattr(qr_image, 'size')
            assert qr_image.size[0] > 0
            assert qr_image.size[1] > 0
    
    def test_resize_image_for_display_method(self):
        """Test image resizing method."""
        with patch.dict('sys.modules', {
            'FreeSimpleGUI': MagicMock(),
            'PIL.ImageTk': MagicMock(),
            'pyperclip': MagicMock()
        }):
            from pysimpleqr.main import QRCodeGenerator
            from PIL import Image
            
            # Create minimal mock for FreeSimpleGUI
            mock_sg = MagicMock()
            mock_sg.Text = MagicMock()
            mock_sg.InputText = MagicMock()
            mock_sg.Button = MagicMock()
            mock_sg.Image = MagicMock()
            mock_sg.Column = MagicMock()
            mock_sg.Frame = MagicMock()
            mock_sg.Window = MagicMock()
            mock_sg.theme = MagicMock()
            
            import sys
            sys.modules['FreeSimpleGUI'] = mock_sg
            
            generator = QRCodeGenerator()
            
            # Test image resizing
            test_image = Image.new('RGB', (300, 300), color='red')
            resized = generator.resize_image_for_display(test_image, 100, 100)
            
            assert resized is not None
            assert resized.size[0] <= 100
            assert resized.size[1] <= 100
    
    def test_qr_code_generator_initialization(self):
        """Test QRCodeGenerator initialization."""
        with patch.dict('sys.modules', {
            'FreeSimpleGUI': MagicMock(),
            'PIL.ImageTk': MagicMock(),
            'pyperclip': MagicMock()
        }):
            from pysimpleqr.main import QRCodeGenerator
            
            # Create comprehensive mock for FreeSimpleGUI
            mock_sg = MagicMock()
            mock_sg.Text = MagicMock(return_value=MagicMock())
            mock_sg.InputText = MagicMock(return_value=MagicMock())
            mock_sg.Button = MagicMock(return_value=MagicMock())
            mock_sg.Image = MagicMock(return_value=MagicMock())
            mock_sg.Column = MagicMock(return_value=MagicMock())
            mock_sg.Frame = MagicMock(return_value=MagicMock())
            mock_sg.Window = MagicMock(return_value=MagicMock())
            mock_sg.theme = MagicMock()
            
            import sys
            sys.modules['FreeSimpleGUI'] = mock_sg
            
            # Test initialization
            generator = QRCodeGenerator()
            
            assert generator is not None
            assert generator.qr_image is None
            assert generator.window is None
            assert hasattr(generator, 'core')
    
    def test_qr_code_generator_edge_cases(self):
        """Test edge cases for QR code generation."""
        with patch.dict('sys.modules', {
            'FreeSimpleGUI': MagicMock(),
            'PIL.ImageTk': MagicMock(),
            'pyperclip': MagicMock()
        }):
            from pysimpleqr.main import QRCodeGenerator
            from PIL import Image
            
            # Create minimal mock for FreeSimpleGUI
            mock_sg = MagicMock()
            mock_sg.Text = MagicMock()
            mock_sg.InputText = MagicMock()
            mock_sg.Button = MagicMock()
            mock_sg.Image = MagicMock()
            mock_sg.Column = MagicMock()
            mock_sg.Frame = MagicMock()
            mock_sg.Window = MagicMock()
            mock_sg.theme = MagicMock()
            
            import sys
            sys.modules['FreeSimpleGUI'] = mock_sg
            
            generator = QRCodeGenerator()
            
            # Test empty text
            qr_empty = generator.generate_qr_code("")
            assert qr_empty is not None
            
            # Test special characters
            qr_special = generator.generate_qr_code("Test áéíóú 中文 🎉")
            assert qr_special is not None
            
            # Test very long text
            long_text = "A" * 1000
            qr_long = generator.generate_qr_code(long_text)
            assert qr_long is not None
            
            # Test resize with zero dimensions
            test_img = Image.new('RGB', (100, 100))
            resized_zero = generator.resize_image_for_display(test_img, 0, 0)
            assert resized_zero.size == (100, 100)
            
            # Test resize with original smaller than max
            small_img = Image.new('RGB', (50, 50))
            resized_small = generator.resize_image_for_display(small_img, 100, 100)
            assert resized_small.size == (50, 50)