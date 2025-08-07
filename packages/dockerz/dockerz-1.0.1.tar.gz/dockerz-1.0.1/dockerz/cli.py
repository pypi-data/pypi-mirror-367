import click
import sys
import os
import shutil
import pkg_resources
from .builder import build_and_push_images

def print_welcome_message():
    """Print a welcome message with usage instructions."""
    click.echo(click.style("\nš Welcome to Dockerz!", fg="green", bold=True))
    click.echo("You can run Dockerz in two ways:")
    click.echo("1. Using the command directly:    dockerz [commands]")
    click.echo("2. Using Python module:           py -m dockerz [commands]")
    click.echo("\nCommands:")
    click.echo("  init     Create a sample services.yaml configuration")
    click.echo("  build    Build Docker images based on services.yaml")
    click.echo("\nFor help, run: dockerz --help")
    click.echo()

def create_sample_config():
    """Create a sample services.yaml file in the current directory."""
    example_path = pkg_resources.resource_filename('dockerz', 'examples/services.yaml')
    if os.path.exists('services.yaml'):
        if not click.confirm('services.yaml already exists. Do you want to overwrite it?'):
            return False
    shutil.copy(example_path, 'services.yaml')
    click.echo(click.style("✓ Created sample services.yaml", fg="green"))
    return True

@click.group()
def cli():
    """Dockerz - Build and push multiple Docker images in parallel."""
    pass

@cli.command()
def init():
    """Initialize a new project with sample configuration."""
    create_sample_config()
    click.echo("\nNext steps:")
    click.echo("1. Edit services.yaml to configure your services")
    click.echo("2. Run 'dockerz build' to build your images")

@cli.command()
@click.option('--config', default='services.yaml', help='Path to services.yaml configuration file.')
@click.option('--max-processes', type=int, help='Maximum number of parallel builds.')
def build(config, max_processes):
    """Build Docker images based on services.yaml configuration."""
    build_and_push_images(config, max_processes)

def main():
    """Main entry point."""
    if len(sys.argv) == 1:  # No arguments provided
        print_welcome_message()
        return
    cli()

if __name__ == "__main__":
    main()
