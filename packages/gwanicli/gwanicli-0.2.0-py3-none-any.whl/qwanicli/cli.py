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
from .smart_formatter import SmartArabicFormatter
from .utils import setup_logging, handle_error


@click.group()
@click.version_option(version=__version__, prog_name="gwani")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--arabic-mode', type=click.Choice(['auto', 'unicode', 'transliteration', 'both']),
              default='auto', help='Arabic text display mode')
@click.pass_context
def gwani(ctx, verbose, arabic_mode):
    """GwaniCLI - Access Quranic verses and translations from the command line."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['arabic_mode'] = arabic_mode
    setup_logging(verbose)


@gwani.command()
@click.option('--translation', '-t', help='Translation to use (e.g., en.pickthall)')
@click.option('--no-cache', is_flag=True, help='Skip cache and fetch fresh data')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.option('--arabic-style', type=click.Choice(['simple', 'bordered', 'highlighted']),
              default='simple', help='Arabic text display style (for legacy formatter)')
@click.pass_context
def random(ctx, translation: Optional[str], no_cache: bool, json_output: bool, arabic_style: str):
    """Get a random Quranic verse with translation."""
    try:
        config = Config()
        client = QuranApiClient()

        # Use provided translation or default from config
        translation = translation or config.get('translation')
        arabic_mode = ctx.obj.get('arabic_mode', 'auto')

        # Use cache wrapper if caching is enabled
        if not no_cache:
            cache = Cache()
            cache_wrapper = CacheWrapper(client, cache)
            verse_data = cache_wrapper.get_random_ayah(translation)
        else:
            verse_data = client.get_random_ayah(translation)

        # Use smart formatter for better Arabic display
        if json_output:
            output = format_verse(
                verse_data, json_output=json_output, arabic_style=arabic_style)
            click.echo(output)
        else:
            formatter = SmartArabicFormatter()
            formatter.format_verse(verse_data, mode=arabic_mode)

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
              default='simple', help='Arabic text display style (for legacy formatter)')
@click.pass_context
def surah(ctx, surah_identifier: str, ayah: Optional[int], translation: Optional[str],
          no_cache: bool, json_output: bool, arabic_style: str):
    """Get ayahs from a specific surah by number or name."""
    try:
        config = Config()
        client = QuranApiClient()

        # Use provided translation or default from config
        translation = translation or config.get('translation')
        arabic_mode = ctx.obj.get('arabic_mode', 'auto')

        # Use cache wrapper if caching is enabled
        if not no_cache:
            cache = Cache()
            cache_wrapper = CacheWrapper(client, cache)
            if ayah:
                verse_data = cache_wrapper.get_ayah_from_surah(
                    surah_identifier, ayah, translation)
            else:
                verse_data = cache_wrapper.get_ayah_from_surah(
                    surah_identifier, None, translation)
        else:
            if ayah:
                verse_data = client.get_ayah_from_surah(
                    surah_identifier, ayah, translation)
            else:
                verse_data = client.get_ayah_from_surah(
                    surah_identifier, None, translation)

        # Use smart formatter for better Arabic display
        if json_output:
            output = format_verse(
                verse_data, json_output=json_output, arabic_style=arabic_style)
            click.echo(output)
        else:
            formatter = SmartArabicFormatter()
            # Handle multiple verses for surah display
            if isinstance(verse_data, list):
                for i, verse in enumerate(verse_data):
                    if i > 0:
                        click.echo("─" * 60)
                    formatter.format_verse(verse, mode=arabic_mode)
            else:
                formatter.format_verse(verse_data, mode=arabic_mode)

    except ApiError as e:
        handle_error(f"Failed to fetch surah: {str(e)}")
    except Exception as e:
        if ctx.obj and ctx.obj.get('verbose'):
            handle_error(
                f"Unexpected error while fetching surah: {str(e)}", show_traceback=True)
        else:
            handle_error(
                f"Unable to fetch surah. Please try again or use --verbose for more details.")


@gwani.command()
@click.pass_context
def fonts(ctx):
    """Check Arabic text display capabilities and show font recommendations."""
    formatter = SmartArabicFormatter()

    click.echo(click.style(
        "🔍 Arabic Text Display Capabilities", fg='cyan', bold=True))
    click.echo("=" * 50)

    # Show terminal info
    capabilities = formatter.get_capabilities_info()
    terminal_info = capabilities['terminal_info']

    click.echo(click.style("Terminal Information:", fg='blue', bold=True))
    click.echo(f"  • Terminal: {terminal_info['term']}")
    click.echo(f"  • Program: {terminal_info['term_program']}")
    click.echo(f"  • Platform: {terminal_info['platform']}")
    click.echo(f"  • Encoding: {terminal_info['encoding']}")
    click.echo()

    # Show Arabic support status
    if capabilities['arabic_support']:
        click.echo(click.style(
            "✅ Arabic Support: Enabled", fg='green', bold=True))
        click.echo("Your terminal can display Arabic text properly!")
    else:
        click.echo(click.style(
            "⚠️  Arabic Support: Limited", fg='yellow', bold=True))
        click.echo("Your terminal has limited Arabic text support.")

    click.echo()

    # Show test text in different modes
    click.echo(click.style("📝 Test Display:", fg='blue', bold=True))
    test_verse = {
        'arabic_text': 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
        'translation': 'In the name of Allah, the Entirely Merciful, the Especially Merciful.',
        'surah_name': 'Al-Fatihah',
        'surah_number': 1,
        'ayah_number': 1
    }

    click.echo(click.style("Unicode mode:", fg='cyan'))
    formatter.format_verse(test_verse, mode='unicode', show_translation=False)

    click.echo(click.style("Transliteration mode:", fg='cyan'))
    formatter.format_verse(
        test_verse, mode='transliteration', show_translation=False)

    # Show font recommendations
    formatter.display_font_recommendations()


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
