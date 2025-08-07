import click
import sys
from .builder import build_and_push_images

def print_welcome_message():
    """Print a welcome message with usage instructions."""
    click.echo(click.style("\nš Welcome to DockerX!", fg="green", bold=True))
    click.echo("You can run DockerX in two ways:")
    click.echo("1. Using the command directly:    dockerx [commands]")
    click.echo("2. Using Python module:           py -m dockerx [commands]")
    click.echo("\nFor help, run: dockerx --help")
    click.echo()

@click.command()
@click.option('--config', default='services.yaml', help='Path to services.yaml configuration file.')
@click.option('--max-processes', type=int, help='Maximum number of parallel builds.')
def main(config, max_processes):
    """Build and optionally push multiple Docker images in parallel."""
    if len(sys.argv) == 1:  # No arguments provided
        print_welcome_message()
        return
    build_and_push_images(config, max_processes)

if __name__ == "__main__":
    main()
