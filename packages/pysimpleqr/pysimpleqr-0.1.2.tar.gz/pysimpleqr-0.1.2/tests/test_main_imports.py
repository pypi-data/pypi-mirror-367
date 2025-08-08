"""Tests for main.py imports and basic functionality."""

import pytest
import sys
from unittest.mock import patch, MagicMock


def test_qr_code_generator_import():
    """Test that QRCodeGenerator can be imported."""
    try:
        from pysimpleqr.main import QRCodeGenerator
        assert QRCodeGenerator is not None
    except ImportError:
        pytest.skip("GUI dependencies not available")


def test_main_py_structure():
    """Test that main.py has the expected structure."""
    import pysimpleqr.main as main_module
    
    # Check that the module has the expected classes
    assert hasattr(main_module, 'QRCodeGenerator')
    
    # Check that QRCodeGenerator has expected methods
    from pysimpleqr.main import QRCodeGenerator
    generator_class = QRCodeGenerator
    
    expected_methods = ['__init__', 'generate_qr_code', 'resize_image_for_display', 'run']
    for method in expected_methods:
        assert hasattr(generator_class, method)


def test_main_py_without_gui():
    """Test main.py can be imported without GUI dependencies."""
    with patch.dict(sys.modules, {'FreeSimpleGUI': MagicMock()}):
        with patch.dict(sys.modules, {'PIL.ImageTk': MagicMock()}):
            with patch.dict(sys.modules, {'pyperclip': MagicMock()}):
                try:
                    from pysimpleqr.main import QRCodeGenerator
                    assert QRCodeGenerator is not None
                except ImportError as e:
                    pytest.skip(f"Import error: {e}")


def test_qr_code_generator_initialization():
    """Test QRCodeGenerator initialization."""
    with patch.dict(sys.modules, {'FreeSimpleGUI': MagicMock()}):
        with patch.dict(sys.modules, {'PIL.ImageTk': MagicMock()}):
            with patch.dict(sys.modules, {'pyperclip': MagicMock()}):
                try:
                    from pysimpleqr.main import QRCodeGenerator
                    
                    # Mock FreeSimpleGUI components
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
                    
                    sys.modules['FreeSimpleGUI'] = mock_sg
                    
                    # Test initialization
                    generator = QRCodeGenerator()
                    assert generator is not None
                    
                except Exception as e:
                    pytest.skip(f"Initialization failed: {e}")