import typer
from loguru import logger

from .qr_core import QRCodeCore
from .main import QRCodeGenerator

app = typer.Typer(help="PySimpleQR - A simple QR code generator")

@app.command()
def gui():
    """Launch the FreeSimpleGUI QR code generator."""
    logger.info("Starting GUI mode")
    qr_app = QRCodeGenerator()
    qr_app.run()

@app.command()
def cli(text: str, output: str = "qr.png"):
    """Generate a QR code from command line.
    
    Args:
        text: The text to encode in the QR code
        output: Output filename for the QR code image (default: qr.png)
    """
    logger.info(f"Generating QR code for text: {text[:50]}...")
    logger.info(f"Output file: {output}")
    
    try:
        qr_core = QRCodeCore()
        qr_image = qr_core.generate_qr_code(text)
        success = qr_core.save_qr_code(qr_image, output)
        if success:
            logger.success(f"QR code saved to: {output}")
            typer.echo(f"QR code generated successfully: {output}")
        else:
            raise Exception("Failed to save QR code")
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def version():
    """Show version information."""
    typer.echo("PySimpleQR v0.1.2")

if __name__ == "__main__":
    app()
