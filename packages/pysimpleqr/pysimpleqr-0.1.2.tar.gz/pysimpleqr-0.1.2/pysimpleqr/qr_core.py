"""Core QR code generation functionality without GUI dependencies."""

import io
import os

import qrcode
from PIL import Image
from loguru import logger


class QRCodeCore:
    """Core QR code generation functionality without GUI dependencies."""
    
    @staticmethod
    def generate_qr_code(text: str) -> Image.Image:
        """Generate a QR code from the given text.
        
        Args:
            text: The text to encode in the QR code
            
        Returns:
            PIL Image of the QR code
        """
        logger.info(f"Generating QR code for text: {text[:50]}...")
        
        # Try different error correction levels and versions to handle long text
        error_corrections = [
            qrcode.constants.ERROR_CORRECT_L,  # ~7% correction
            qrcode.constants.ERROR_CORRECT_M,  # ~15% correction  
            qrcode.constants.ERROR_CORRECT_Q,  # ~25% correction
            qrcode.constants.ERROR_CORRECT_H   # ~30% correction
        ]
        
        for error_correction in error_corrections:
            try:
                qr = qrcode.QRCode(
                    version=None,  # Let it auto-determine the version
                    error_correction=error_correction,
                    box_size=10,
                    border=4,
                )
                qr.add_data(text, optimize=0)
                qr.make(fit=True)
                
                # Create PIL image
                img = qr.make_image(fill_color="black", back_color="white")
                logger.info(f"QR code generated with error correction level: {error_correction}")
                return img
                
            except ValueError as e:
                logger.warning(f"Failed with error correction {error_correction}: {e}")
                continue
        
        # If all error correction levels fail, the text is too long
        # Truncate the text and try again with the lowest error correction
        max_chars = 2000  # Conservative estimate for QR code capacity
        if len(text) > max_chars:
            truncated_text = text[:max_chars] + "... [truncated]"
            logger.warning(f"Text too long ({len(text)} chars), truncating to {len(truncated_text)} chars")
            
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(truncated_text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            return img
        else:
            # If text is not too long but still fails, raise the error
            raise ValueError(f"Unable to generate QR code for text of length {len(text)}")
    
    @staticmethod
    def resize_image_for_display(img: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Resize image to fit within the given dimensions while maintaining aspect ratio.
        
        Args:
            img: The PIL image to resize
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            
        Returns:
            Resized PIL image
        """
        if max_width <= 0 or max_height <= 0:
            logger.warning("Invalid dimensions provided, returning original image")
            return img
            
        width, height = img.size
        
        # Calculate scaling factor
        width_ratio = max_width / width
        height_ratio = max_height / height
        scale_factor = min(width_ratio, height_ratio, 1.0)
        
        if scale_factor < 1.0:
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            logger.info(f"Resizing image from {width}x{height} to {new_width}x{new_height}")
            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
    
    @staticmethod
    def save_qr_code(img: Image.Image, filename: str) -> bool:
        """Save QR code image to file.
        
        Args:
            img: The PIL image to save
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if the path is writable
            directory = os.path.dirname(filename)
            if directory:
                # Test if directory can be created/accessed
                os.makedirs(directory, exist_ok=True)
                # Check if directory is actually writable
                if not os.access(directory, os.W_OK):
                    raise PermissionError(f"No write permission to directory: {directory}")
            
            # Test if we can write to the file
            with open(filename, 'wb') as f:
                pass
            
            # If we get here, we can write the image
            img.save(filename, 'PNG')
            logger.info(f"QR code saved to: {filename}")
            return True
        except (OSError, PermissionError, IOError) as e:
            logger.error(f"Error saving QR code: {e}")
            return False
    
    @staticmethod
    def get_qr_code_bytes(img: Image.Image) -> bytes:
        """Get QR code image as bytes.
        
        Args:
            img: The PIL image
            
        Returns:
            Image bytes in PNG format
        """
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()