"""Tests for CLI commands."""

import tempfile
import os
import pytest
from typer.testing import CliRunner

from pysimpleqr.__main__ import app


class TestCLICommands:
    """Test cases for CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_version_command(self):
        """Test version command output."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "PySimpleQR v0.1.2" in result.output
    
    def test_cli_command_basic(self):
        """Test CLI command with basic text."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = os.path.join(tmp_dir, "test_qr.png")
            
            result = self.runner.invoke(app, ["cli", "Hello World", "--output", output_file])
            
            assert result.exit_code == 0
            assert "QR code generated successfully" in result.output
            assert os.path.exists(output_file)
    
    def test_cli_command_default_output(self):
        """Test CLI command with default output filename."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)
                result = self.runner.invoke(app, ["cli", "Test text"])
                
                assert result.exit_code == 0
                assert "QR code generated successfully: qr.png" in result.output
                assert os.path.exists("qr.png")
            finally:
                os.chdir(original_cwd)
    
    def test_cli_command_empty_text(self):
        """Test CLI command with empty text."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = os.path.join(tmp_dir, "empty_qr.png")
            
            result = self.runner.invoke(app, ["cli", "", "--output", output_file])
            
            assert result.exit_code == 0
            assert f"QR code generated successfully: {output_file}" in result.output
            assert os.path.exists(output_file)
    
    def test_cli_command_long_text(self):
        """Test CLI command with long text."""
        long_text = "A" * 1000
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = os.path.join(tmp_dir, "long_qr.png")
            
            result = self.runner.invoke(app, ["cli", long_text, "--output", output_file])
            
            assert result.exit_code == 0
            assert f"QR code generated successfully: {output_file}" in result.output
            assert os.path.exists(output_file)
    
    def test_cli_command_special_characters(self):
        """Test CLI command with special characters."""
        special_text = "Hello\nWorld! Special chars: áéíóú 你好世界"
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = os.path.join(tmp_dir, "special_qr.png")
            
            result = self.runner.invoke(app, ["cli", special_text, "--output", output_file])
            
            assert result.exit_code == 0
            assert f"QR code generated successfully: {output_file}" in result.output
            assert os.path.exists(output_file)
    
    def test_help_command(self):
        """Test help command output."""
        result = self.runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "PySimpleQR - A simple QR code generator" in result.output
        assert "gui" in result.output
        assert "cli" in result.output
        assert "version" in result.output
    
    def test_cli_help(self):
        """Test CLI command help."""
        result = self.runner.invoke(app, ["cli", "--help"])
        
        assert result.exit_code == 0
        assert "Generate a QR code from command line" in result.output
        assert "TEXT" in result.output
        assert "--output" in result.output
    
    def test_gui_help(self):
        """Test GUI command help."""
        result = self.runner.invoke(app, ["gui", "--help"])
        
        assert result.exit_code == 0
        assert "Launch the FreeSimpleGUI QR code generator" in result.output


class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_full_workflow(self):
        """Test complete CLI workflow."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = os.path.join(tmp_dir, "integration_qr.png")
            
            # Test CLI command
            result = self.runner.invoke(app, ["cli", "Integration test", "--output", output_file])
            
            assert result.exit_code == 0
            assert os.path.exists(output_file)
            
            # Verify the file is a valid image
            from PIL import Image
            img = Image.open(output_file)
            assert img.size[0] > 0
            assert img.size[1] > 0
            
            # Close the image to release file handle
            img.close()
    
    def test_multiple_commands_sequence(self):
        """Test running multiple commands in sequence."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test version
            version_result = self.runner.invoke(app, ["version"])
            assert version_result.exit_code == 0
            
            # Test CLI with different texts
            texts = ["Text 1", "Text 2", "Text 3"]
            for i, text in enumerate(texts):
                output_file = os.path.join(tmp_dir, f"qr_{i}.png")
                result = self.runner.invoke(app, ["cli", text, "--output", output_file])
                assert result.exit_code == 0
                assert os.path.exists(output_file)


if __name__ == "__main__":
    pytest.main([__file__])