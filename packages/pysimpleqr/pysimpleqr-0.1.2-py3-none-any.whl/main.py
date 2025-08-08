import io
import os
import tempfile
from typing import Optional

import FreeSimpleGUI as sg
from loguru import logger
from PIL import Image, ImageTk

try:
    import win32clipboard
    from io import BytesIO
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

from .qr_core import QRCodeCore


class QRCodeGenerator:
    """A FreeSimpleGUI-based QR code generator application."""
    
    def __init__(self):
        """Initialize the QR code generator."""
        logger.info("Initializing QR Code Generator")
        sg.theme('DarkBlue3')  # Clean, modern theme
        self.qr_image: Optional[Image.Image] = None
        self.window: Optional[sg.Window] = None
        self.core = QRCodeCore()
        
        # QR code specifications
        self.max_qr_length = 2000  # Maximum for QR code version 40
        self.current_text_length = 0
        
    def generate_qr_code(self, text: str) -> Image.Image:
        """Generate a QR code from the given text.
        
        Args:
            text: The text to encode in the QR code
            
        Returns:
            PIL Image of the QR code
        """
        return self.core.generate_qr_code(text)
    
    def resize_image_for_display(self, img: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Resize image to fit within the given dimensions while maintaining aspect ratio.
        
        Args:
            img: The PIL image to resize
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            
        Returns:
            Resized PIL image
        """
        return self.core.resize_image_for_display(img, max_width, max_height)
    
    def escape_urls_in_text(self, text: str) -> str:
        """Escape URLs in text to prevent auto-detection by QR scanners.
        
        Args:
            text: Original text content
            
        Returns:
            Text with URLs escaped
        """
        import re
        
        # Common URL patterns to escape
        url_pattern = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        
        def escape_url(match):
            url = match.group(0)
            return url.replace('.', '[dot]').replace(':', '[:]')
        
        escaped_text = re.sub(url_pattern, escape_url, text)
        return escaped_text

    def resize_to_fit(self, image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Resize image to fit within given dimensions while maintaining aspect ratio."""
        width, height = image.size
        
        # Calculate scaling factor
        width_ratio = max_width / width
        height_ratio = max_height / height
        scale_factor = min(width_ratio, height_ratio)
        
        # Only resize if image is larger than available space
        if scale_factor < 1.0:
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image

    def copy_image_to_clipboard_windows(self, image: Image.Image) -> bool:
        """Copy PIL image to Windows clipboard with proper RGB/RGBA handling.
        
        Args:
            image: PIL Image to copy to clipboard
            
        Returns:
            True if successful, False otherwise
        """
        if not WIN32_AVAILABLE:
            return False
            
        try:
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to BMP format in memory
            output = BytesIO()
            image.save(output, format='BMP')
            data = output.getvalue()[14:]  # Remove BMP header
            output.close()
            
            # Copy to clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_DIB, data)
            win32clipboard.CloseClipboard()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy image to clipboard: {e}")
            if WIN32_AVAILABLE:
                try:
                    win32clipboard.CloseClipboard()
                except:
                    pass
            return False
    
    def update_character_counter(self, text: str):
        """Update the character counter and warning messages.
        
        Args:
            text: Current text content
        """
        length = len(text)
        self.current_text_length = length
        
        if self.window:
            self.window["-CHAR_COUNT-"].update(f"Characters: {length}/{self.max_qr_length}")
            
            if length > self.max_qr_length:
                self.window["-CHAR_WARNING-"].update(
                    f"⚠️ Text too long! Truncated to {self.max_qr_length} chars",
                    visible=True,
                    text_color='#ef4444'
                )
            elif length > int(self.max_qr_length * 0.8):
                remaining = self.max_qr_length - length
                self.window["-CHAR_WARNING-"].update(
                    f"⚠️ {remaining} characters remaining",
                    visible=True,
                    text_color='#f59e0b'
                )
            else:
                self.window["-CHAR_WARNING-"].update(visible=False)
    
    def create_layout(self) -> list:
        """Create the FreeSimpleGUI layout for the application."""
        # Get screen dimensions for responsive sizing
        screen_width, screen_height = sg.Window.get_screen_size()
        
        # Responsive sizing optimized for UX
        input_width = min(70, max(50, screen_width // 18))
        button_width = min(12, max(8, screen_width // 100))
        image_width = 300
        image_height = 300
        
        # Color scheme
        colors = {
            'primary': '#1e3a8a',
            'secondary': '#3b82f6',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'text': '#1f2937',
            'light_bg': '#f8fafc'
        }
        
        layout = [
            # Header with branding
            [sg.Text("🎯 PySimpleQR", font=('Helvetica', 20, 'bold'), 
                     text_color=colors['primary'], justification='center', expand_x=True)],
            [sg.Text("Professional QR Code Generator", font=('Helvetica', 11),
                     text_color=colors['text'], justification='center', expand_x=True)],
            [sg.HorizontalSeparator(color=colors['secondary'])],
            
            # Input section with character counter
            [sg.Frame("Text Input", [
                [sg.Multiline(
                    key="-TEXT-",
                    size=(input_width, 9),
                    font=('Helvetica', 12),
                    expand_x=True,
                    expand_y=True,
                    enable_events=True,
                    tooltip=f"Enter text to encode (max {self.max_qr_length} characters)"
                )],
                [sg.Checkbox("Plain text mode (no URL auto-detection)", 
                            key="-PLAIN_TEXT-", 
                            default=False,
                            tooltip="QR scanners will treat URLs as plain text instead of clickable links")],
                [sg.Checkbox("Escape URLs", 
                            key="-ESCAPE_URLS-", 
                            default=False,
                            tooltip="Replace . with [dot] and : with [:] in URLs to prevent auto-detection")],
                [sg.Text("Characters: 0", key="-CHAR_COUNT-", 
                         font=('Helvetica', 10), text_color=colors['text']),
                 sg.Text("", key="-CHAR_WARNING-", font=('Helvetica', 10, 'bold'),
                         text_color=colors['error'], visible=False)],
            ], expand_x=True, relief=sg.RELIEF_RAISED)],
            
            # Action buttons with modern styling
            [sg.Frame("Actions", [
                [sg.Button("✨ QR it", key="-GENERATE-", 
                          size=(button_width, 1), button_color=('white', colors['success']),
                          font=('Helvetica', 11, 'bold')),
                 sg.Button("💾 Save QR", key="-SAVE-", 
                          size=(button_width, 1), disabled=True,
                          button_color=('white', colors['secondary']),
                          font=('Helvetica', 11)),
                 sg.Button("📋 Copy QR", key="-COPY-", 
                          size=(button_width, 1), disabled=True,
                          button_color=('white', colors['secondary']),
                          font=('Helvetica', 11)),
                 sg.Button("❌ Close", key="-CLOSE-", 
                          size=(button_width, 1),
                          button_color=('white', colors['error']),
                          font=('Helvetica', 11)),
                 sg.Button("🧪 Test", key="-TEST-", 
                          size=(button_width, 1),
                          button_color=('white', '#8b5cf6'),
                          font=('Helvetica', 11))],
            ], expand_x=True, element_justification='center')],
            
            # QR display area
            [sg.Frame("QR Code Preview", [
                [sg.Image(key="-IMAGE-", 
                         size=(image_width, image_height),
                         background_color='white',
                         expand_x=True, expand_y=True,
                         pad=(10, 10))],
                [sg.Text("Generate a QR code to see preview", 
                        key="-PREVIEW_TEXT-",
                        font=('Helvetica', 12),
                        text_color=colors['text'],
                        justification='center',
                        expand_x=True,
                        visible=True)],
            ], expand_x=True, expand_y=True, relief=sg.RELIEF_SUNKEN)],
            
            # Status bar
            [sg.StatusBar("🚀 Ready to generate QR codes", 
                         key="-STATUS-", 
                         size=(60, 1),
                         font=('Helvetica', 10))]
        ]
        
        return layout
    
    def run(self):
        """Run the QR code generator application with enhanced UX."""
        logger.info("Starting QR Code Generator application")
        
        layout = self.create_layout()
        
        # Create window with enhanced UX
        screen_width, screen_height = sg.Window.get_screen_size()
        window_width = min(900, max(600, screen_width // 2))
        window_height = min(850, max(700, int(screen_height // 1.4)))
        
        self.window = sg.Window(
            "🎯 PySimpleQR - Professional QR Generator",
            layout,
            size=(window_width, window_height),
            resizable=True,
            finalize=True,
            icon=None,
            element_padding=(5, 5),
            margins=(20, 20)
        )
        
        # Initialize character counter
        self.update_character_counter("")
        
        # Event loop with enhanced functionality
        while True:
            event, values = self.window.read()
            
            if event in (sg.WIN_CLOSED, "-CLOSE-"):
                logger.info("Closing application")
                break
                
            elif event == "-TEXT-":
                # Handle text changes for character counting
                text = values["-TEXT-"]
                self.update_character_counter(text)
                
            elif event == "-GENERATE-":
                original_text = values["-TEXT-"].strip()
                
                if not original_text:
                    sg.popup_error("📝 Please enter some text to generate a QR code.", 
                                 title="Input Required")
                    continue
                
                # Truncate text if too long
                if len(original_text) > self.max_qr_length:
                    original_text = original_text[:self.max_qr_length]
                    self.window["-TEXT-"].update(original_text)
                    self.update_character_counter(original_text)
                
                try:
                    # Show loading status
                    self.window["-STATUS-"].update("⚡ Generating QR code...")
                    self.window.refresh()
                    
                    # Process text based on options
                    qr_text = original_text
                    if values["-ESCAPE_URLS-"]:
                        qr_text = self.escape_urls_in_text(original_text)
                        # Update the text input with escaped content
                        self.window["-TEXT-"].update(qr_text)
                        self.update_character_counter(qr_text)
                    
                    # Generate QR code
                    self.qr_image = self.generate_qr_code(qr_text)
                    
                    # Resize image to fit 300x300 frame while maintaining aspect ratio
                    display_img = self.resize_to_fit(self.qr_image, 300, 300)
                    
                    # Convert to PhotoImage
                    tk_image = ImageTk.PhotoImage(display_img)
                    
                    # Update UI
                    self.window["-IMAGE-"].update(data=tk_image)
                    self.window["-PREVIEW_TEXT-"].update(visible=False)
                    self.window["-SAVE-"].update(disabled=False)
                    self.window["-COPY-"].update(disabled=False)
                    self.window["-STATUS-"].update(f"✅ QR code generated ({len(text)} chars)")
                    
                    # Prevent garbage collection
                    self.window.TKroot.tk_image = tk_image
                    
                except Exception as e:
                    logger.error(f"Error generating QR code: {e}")
                    sg.popup_error(f"❌ Error generating QR code:\n{str(e)}", 
                                 title="Generation Error")
                    self.window["-STATUS-"].update("❌ Generation failed")
                    
            elif event == "-SAVE-":
                if self.qr_image is None:
                    sg.popup_error("📄 No QR code to save. Please generate one first.",
                                 title="No QR Code")
                    continue
                
                try:
                    filename = sg.popup_get_file(
                        "Save QR Code",
                        save_as=True,
                        default_extension=".png",
                        file_types=[("PNG Files", "*.png"), ("All Files", "*.*")],
                        no_window=True
                    )
                    
                    if filename:
                        if not filename.lower().endswith('.png'):
                            filename += '.png'
                        
                        self.qr_image.save(filename, 'PNG', quality=95)
                        logger.info(f"QR code saved to: {filename}")
                        self.window["-STATUS-"].update(f"💾 Saved: {os.path.basename(filename)}")
                        sg.popup(f"✅ QR code saved successfully!\n📁 {filename}", 
                               title="Save Complete")
                        
                except Exception as e:
                    logger.error(f"Error saving QR code: {e}")
                    sg.popup_error(f"❌ Error saving QR code:\n{str(e)}", 
                                 title="Save Error")
                    
            elif event == "-COPY-":
                if self.qr_image is None:
                    sg.popup_error("📋 No QR code to copy. Please generate one first.",
                                 title="No QR Code")
                    continue
                
                try:
                    success = False
                    if WIN32_AVAILABLE:
                        success = self.copy_image_to_clipboard_windows(self.qr_image)
                    
                    if success:
                        self.window["-STATUS-"].update("📋 QR copied to clipboard!")
                        sg.popup("✅ QR code copied to clipboard!\n📋 Ready to paste anywhere.",
                               title="Copy Complete")
                    else:
                        # Fallback: save to temp file and open folder
                        temp_dir = tempfile.gettempdir()
                        temp_path = os.path.join(temp_dir, "qrcode_clipboard.png")
                        self.qr_image.save(temp_path, 'PNG')
                        
                        sg.popup("📋 Clipboard copy not available.\n"
                               f"💾 QR saved to temp file:\n{temp_path}",
                               title="Alternative Copy")
                        self.window["-STATUS-"].update("📁 QR saved to temp file")
                        
                except Exception as e:
                    logger.error(f"Error copying QR code: {e}")
                    sg.popup_error(f"❌ Error copying QR code:\n{str(e)}",
                                 title="Copy Error")
                    
            elif event == "-TEST-":
                # Generate a test QR code with simple text
                test_text = "Hello QR World! 12345"
                self.window["-TEXT-"].update(test_text)
                self.update_character_counter(test_text)

                try:
                    self.window["-STATUS-"].update("⚡ Generating test QR...")
                    self.window.refresh()

                    # Process test text based on options
                    processed_text = test_text
                    if values["-ESCAPE_URLS-"]:
                        processed_text = self.escape_urls_in_text(test_text)
                        # Update the text input with escaped content
                        self.window["-TEXT-"].update(processed_text)
                        self.update_character_counter(processed_text)

                    # Generate test QR
                    self.qr_image = self.generate_qr_code(processed_text)

                    # Resize image to fit 300x300 frame while maintaining aspect ratio
                    display_img = self.resize_to_fit(self.qr_image, 300, 300)

                    tk_image = ImageTk.PhotoImage(display_img)
                    self.window["-IMAGE-"].update(data=tk_image)
                    self.window["-PREVIEW_TEXT-"].update(visible=False)
                    self.window["-SAVE-"].update(disabled=False)
                    self.window["-COPY-"].update(disabled=False)
                    
                    status_text = "✅ Test QR generated - scan this!"
                    if values["-ESCAPE_URLS-"]:
                        status_text += " (URLs escaped)"
                    self.window["-STATUS-"].update(status_text)

                    # Prevent garbage collection
                    self.window.TKroot.tk_image = tk_image

                except Exception as e:
                    logger.error(f"Error generating test QR: {e}")
                    sg.popup_error(f"❌ Error generating test QR:\n{str(e)}",
                                 title="Test Error")
        
        self.window.close()


def main():
    """Main entry point for the application."""
    try:
        app = QRCodeGenerator()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sg.popup_error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()