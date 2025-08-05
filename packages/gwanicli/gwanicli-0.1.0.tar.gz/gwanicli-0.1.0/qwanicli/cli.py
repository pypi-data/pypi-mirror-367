"""
Main CLI entry point for GwaniCLI.
Provides commands for accessing Quranic verses, translations, and configuration.
"""

import click
import json
from typing import Optional

from . import __version__
from .api_client import QuranApiClient, ApiError
from .config import Config
from .cache import Cache, CacheWrapper
from .formatter import format_verse
from .utils import setup_logging, handle_error


@click.group()
@click.version_option(version=__version__, prog_name="gwani")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def gwani(ctx, verbose):
    """GwaniCLI - Access Quranic verses and translations from the command line."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    setup_logging(verbose)


@gwani.command()
@click.option('--translation', '-t', help='Translation to use (e.g., en.pickthall)')
@click.option('--no-cache', is_flag=True, help='Skip cache and fetch fresh data')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.option('--arabic-style', type=click.Choice(['simple', 'bordered', 'highlighted']),
              default='simple', help='Arabic text display style')
@click.pass_context
def random(ctx, translation: Optional[str], no_cache: bool, json_output: bool, arabic_style: str):
    """Get a random Quranic verse with translation."""
    try:
        config = Config()
        client = QuranApiClient()

        # Use provided translation or default from config
        translation = translation or config.get('translation')

        # Use cache wrapper if caching is enabled
        if not no_cache:
            cache = Cache()
            cache_wrapper = CacheWrapper(client, cache)
            verse_data = cache_wrapper.get_random_ayah(translation)
        else:
            verse_data = client.get_random_ayah(translation)

        output = format_verse(
            verse_data, json_output=json_output, arabic_style=arabic_style)
        click.echo(output)

    except ApiError as e:
        handle_error(f"Failed to fetch random verse: {str(e)}")
    except Exception as e:
        if ctx.obj and ctx.obj.get('verbose'):
            handle_error(
                f"Unexpected error while fetching random verse: {str(e)}", show_traceback=True)
        else:
            handle_error(
                f"Unable to fetch random verse. Please try again or use --verbose for more details.")


@gwani.command()
@click.argument('surah_identifier')
@click.option('--ayah', '-a', type=int, help='Specific ayah number')
@click.option('--translation', '-t', help='Translation to use (e.g., en.pickthall)')
@click.option('--no-cache', is_flag=True, help='Skip cache and fetch fresh data')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.option('--arabic-style', type=click.Choice(['simple', 'bordered', 'highlighted']),
              default='simple', help='Arabic text display style')
@click.pass_context
def surah(ctx, surah_identifier: str, ayah: Optional[int], translation: Optional[str],
          no_cache: bool, json_output: bool, arabic_style: str):
    """Get verses from a specific surah by number or name."""
    try:
        config = Config()
        client = QuranApiClient()

        # Use provided translation or default from config
        translation = translation or config.get('translation')

        # Use cache wrapper if caching is enabled
        if not no_cache:
            cache = Cache()
            cache_wrapper = CacheWrapper(client, cache)
            verse_data = cache_wrapper.get_ayah_from_surah(
                surah_identifier, ayah, translation)
        else:
            verse_data = client.get_ayah_from_surah(
                surah_identifier, ayah, translation)

        output = format_verse(
            verse_data, json_output=json_output, arabic_style=arabic_style)
        click.echo(output)

    except ApiError as e:
        handle_error(
            f"Failed to fetch verse from surah {surah_identifier}: {str(e)}")
    except Exception as e:
        if ctx.obj and ctx.obj.get('verbose'):
            handle_error(
                f"Unexpected error while fetching surah {surah_identifier}: {str(e)}", show_traceback=True)
        else:
            handle_error(
                f"Unable to fetch verse from surah {surah_identifier}. Please check your input or use --verbose for more details.")


@gwani.group()
def config():
    """Manage GwaniCLI configuration settings."""
    pass


@config.command()
@click.argument('key')
@click.argument('value', required=False)
def set(key: str, value: Optional[str]):
    """Set a configuration value."""
    try:
        config = Config()

        if value is None:
            click.echo("❌ Value required for key '{}'.".format(key))
            return

        if key not in ['translation', 'cache_ttl']:
            click.echo("❌ Unknown configuration key '{}'.".format(key))
            click.echo("💡 Supported keys: translation, cache_ttl")
            return

        # Convert cache_ttl to int if needed
        if key == 'cache_ttl':
            try:
                value = int(value)
            except ValueError:
                click.echo("❌ cache_ttl must be a number (seconds).")
                click.echo("💡 Example: gwani config set cache_ttl 86400")
                return

        config.set(key, value)
        click.echo("✅ Set {} = {}".format(key, value))

    except Exception as e:
        handle_error(f"Failed to save configuration: {str(e)}")


@config.command()
@click.argument('key')
def get(key: str):
    """Get a configuration value."""
    try:
        config = Config()

        if key not in ['translation', 'cache_ttl']:
            click.echo("❌ Unknown configuration key '{}'.".format(key))
            click.echo("💡 Supported keys: translation, cache_ttl")
            return

        value = config.get(key)
        click.echo("{} = {}".format(key, value))

    except Exception as e:
        handle_error(f"Failed to read configuration: {str(e)}")


@gwani.command()
def version():
    """Show version information."""
    click.echo(f"GwaniCLI version {__version__}")


if __name__ == "__main__":
    gwani()
