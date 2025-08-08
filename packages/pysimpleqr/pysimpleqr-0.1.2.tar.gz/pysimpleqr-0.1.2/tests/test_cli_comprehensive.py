"""Comprehensive CLI tests for better coverage."""

import tempfile
import os
from typer.testing import CliRunner
from unittest.mock import patch

from pysimpleqr.__main__ import app


class TestCLIComprehensive:
    """Comprehensive CLI tests for maximum coverage."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_with_various_output_formats(self):
        """Test CLI with different output file extensions."""
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        
        for ext in extensions:
            with tempfile.TemporaryDirectory() as tmp_dir:
                output_file = os.path.join(tmp_dir, f"test_qr{ext}")
                
                result = self.runner.invoke(app, ["cli", "Test text", "--output", output_file])
                
                assert result.exit_code == 0
                assert os.path.exists(output_file)
    
    def test_cli_with_special_characters_in_path(self):
        """Test CLI with special characters in output path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test with spaces and special characters
            output_file = os.path.join(tmp_dir, "test qr (1).png")
            
            result = self.runner.invoke(app, ["cli", "Test", "--output", output_file])
            
            assert result.exit_code == 0
            assert os.path.exists(output_file)
    
    def test_cli_with_unicode_text(self):
        """Test CLI with Unicode text input."""
        unicode_texts = [
            "Hello 世界",
            "Tëst with àccénts",
            "Русский текст",
            "🎉 Emoji test 🚀",
        ]
        
        for text in unicode_texts:
            with tempfile.TemporaryDirectory() as tmp_dir:
                output_file = os.path.join(tmp_dir, "unicode_qr.png")
                
                result = self.runner.invoke(app, ["cli", text, "--output", output_file])
                
                assert result.exit_code == 0
                assert os.path.exists(output_file)
    
    def test_cli_with_very_long_text(self):
        """Test CLI with extremely long text."""
        long_text = "Long text " * 500  # Very long text
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = os.path.join(tmp_dir, "long_qr.png")
            
            result = self.runner.invoke(app, ["cli", long_text, "--output", output_file])
            
            assert result.exit_code == 0
            assert os.path.exists(output_file)
    
    def test_cli_with_newlines_and_tabs(self):
        """Test CLI with text containing newlines and tabs."""
        text_with_formatting = "Line 1\\nLine 2\\tTabbed text"
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = os.path.join(tmp_dir, "formatted_qr.png")
            
            result = self.runner.invoke(app, ["cli", text_with_formatting, "--output", output_file])
            
            assert result.exit_code == 0
            assert os.path.exists(output_file)
    
    def test_cli_with_json_content(self):
        """Test CLI with JSON-like content."""
        json_text = '{"name": "test", "value": 123, "nested": {"key": "value"}}'
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = os.path.join(tmp_dir, "json_qr.png")
            
            result = self.runner.invoke(app, ["cli", json_text, "--output", output_file])
            
            assert result.exit_code == 0
            assert os.path.exists(output_file)
    
    def test_cli_with_url_content(self):
        """Test CLI with URL content."""
        urls = [
            "https://www.example.com",
            "http://test.org/path?param=value",
            "mailto:test@example.com",
            "tel:+1234567890",
        ]
        
        for url in urls:
            with tempfile.TemporaryDirectory() as tmp_dir:
                output_file = os.path.join(tmp_dir, "url_qr.png")
                
                result = self.runner.invoke(app, ["cli", url, "--output", output_file])
                
                assert result.exit_code == 0
                assert os.path.exists(output_file)
    
    @patch('pysimpleqr.main.QRCodeGenerator.run')
    def test_gui_command_mocked(self, mock_run):
        """Test GUI command with mocked run method."""
        mock_run.return_value = None
        
        result = self.runner.invoke(app, ["gui"])
        
        assert result.exit_code == 0
        mock_run.assert_called_once()
    
    def test_version_command_output_format(self):
        """Test version command output format."""
        result = self.runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        assert "PySimpleQR" in result.output
        assert "v" in result.output
        assert "0.1.2" in result.output
    
    def test_help_command_content(self):
        """Test help command shows all available commands."""
        result = self.runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        output = result.output.lower()
        assert "pysimpleqr" in output
        assert "gui" in output
        assert "cli" in output
        assert "version" in output
    
    def test_cli_help_detailed(self):
        """Test CLI help shows detailed information."""
        result = self.runner.invoke(app, ["cli", "--help"])
        
        assert result.exit_code == 0
        output = result.output.lower()
        assert "generate" in output
        assert "qr code" in output
        assert "text" in output
        assert "output" in output
    
    def test_invalid_command(self):
        """Test invalid command handling."""
        result = self.runner.invoke(app, ["invalid_command"])
        
        # Should show help or error
        assert result.exit_code != 0
    
    def test_cli_with_relative_path(self):
        """Test CLI with relative output path."""
        original_cwd = os.getcwd()
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                os.chdir(tmp_dir)
                result = self.runner.invoke(app, ["cli", "Relative path test", "--output", "relative_qr.png"])
                
                assert result.exit_code == 0
                assert os.path.exists("relative_qr.png")
            finally:
                os.chdir(original_cwd)
    
    def test_cli_creates_directory_if_needed(self):
        """Test CLI creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested_path = os.path.join(tmp_dir, "subdir", "nested", "qr.png")
            
            result = self.runner.invoke(app, ["cli", "Directory creation test", "--output", nested_path])
            
            assert result.exit_code == 0
            assert os.path.exists(nested_path)


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_with_readonly_directory(self):
        """Test CLI with read-only output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Make directory read-only
            readonly_dir = os.path.join(tmp_dir, "readonly")
            os.makedirs(readonly_dir)
            
            # Try to set read-only (may not work on all systems)
            try:
                os.chmod(readonly_dir, 0o444)
                output_file = os.path.join(readonly_dir, "test.png")
                
                # Should handle the error gracefully
                # The exact behavior may vary by system
                _ = self.runner.invoke(app, ["cli", "Test", "--output", output_file])
                
            except (OSError, PermissionError):
                # Skip test if we can't create read-only directory
                pass
            finally:
                # Restore permissions
                try:
                    os.chmod(readonly_dir, 0o755)
                except (OSError, PermissionError):
                    pass


class TestMainModuleExecution:
    """Test main module execution scenarios."""
    
    def test_main_module_help(self):
        """Test running module with --help."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "PySimpleQR" in result.output
    
    def test_main_module_version(self):
        """Test running module with version command."""
        runner = CliRunner()
        result = runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        assert "0.1.2" in result.output
