"""
Smart Arabic text formatter with automatic terminal capability detection.
Provides optimal display methods for Arabic text without requiring font installation.
"""

import os
import sys
import platform
import unicodedata
import click
from typing import Dict, Any, Optional


class SmartArabicFormatter:
    """Intelligent Arabic text formatter that adapts to terminal capabilities."""

    def __init__(self):
        self.terminal_info = self._get_terminal_info()
        self.arabic_support = self._detect_arabic_support()
        self._optimize_terminal()

    def _get_terminal_info(self) -> Dict[str, str]:
        """Collect terminal environment information."""
        return {
            'term': os.environ.get('TERM', ''),
            'term_program': os.environ.get('TERM_PROGRAM', ''),
            'platform': platform.system(),
            'encoding': sys.stdout.encoding or 'utf-8',
            'colorterm': os.environ.get('COLORTERM', ''),
            'shell': os.environ.get('SHELL', '')
        }

    def _detect_arabic_support(self) -> bool:
        """Detect if terminal can properly display Arabic text."""
        # Check encoding support
        encoding = self.terminal_info['encoding'].lower()
        if 'utf' not in encoding:
            return False

        # Check for known Arabic-capable terminals
        term = self.terminal_info['term'].lower()
        term_program = self.terminal_info['term_program'].lower()

        capable_terminals = [
            'xterm', 'gnome', 'konsole', 'iterm', 'terminal', 'alacritty',
            'kitty', 'wezterm', 'hyper', 'tabby'
        ]

        if any(capable in term or capable in term_program for capable in capable_terminals):
            return True

        # Test actual Unicode display capability
        try:
            test_text = "العربية"
            test_text.encode(self.terminal_info['encoding'])
            return True
        except (UnicodeEncodeError, LookupError):
            return False

    def _optimize_terminal(self):
        """Apply terminal-specific optimizations for Arabic display."""
        platform_name = self.terminal_info['platform']

        # Windows-specific optimizations
        if platform_name == 'Windows':
            # Enable UTF-8 code page for better Unicode support
            try:
                os.system('chcp 65001 > nul 2>&1')
            except:
                pass

        # Reconfigure stdout encoding if possible (Python 3.7+)
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            except:
                pass

    def format_verse(self, verse_data: Dict[str, Any], mode: str = 'auto',
                     show_translation: bool = True) -> None:
        """
        Format and display Arabic verse with optimal rendering.

        Args:
            verse_data: Dictionary containing verse information
            mode: Display mode ('auto', 'unicode', 'transliteration', 'both')
            show_translation: Whether to show translation text
        """
        if not verse_data:
            return

        # Determine display mode
        if mode == 'auto':
            mode = 'unicode' if self.arabic_support else 'both'

        # Extract Arabic text
        arabic_text = self._extract_arabic_text(verse_data)
        if not arabic_text:
            click.echo(click.style(
                "No Arabic text found in verse data", fg='yellow'))
            return

        # Display Arabic text based on mode
        if mode in ['unicode', 'both']:
            self._display_unicode_arabic(arabic_text)

        if mode in ['transliteration', 'both']:
            self._display_transliteration(arabic_text)

        # Show verse reference
        self._display_verse_reference(verse_data)

        # Show translation if requested
        if show_translation:
            self._display_translation(verse_data)

    def _extract_arabic_text(self, verse_data: Dict[str, Any]) -> str:
        """Extract Arabic text from various verse data formats."""
        # Try different possible field names for Arabic text
        arabic_fields = ['arabic_text', 'text', 'arabic', 'ayah_text']

        for field in arabic_fields:
            if field in verse_data and verse_data[field]:
                return verse_data[field]

        # Check nested data structure
        if 'data' in verse_data:
            data = verse_data['data']
            if isinstance(data, dict):
                for field in arabic_fields:
                    if field in data and data[field]:
                        return data[field]
            elif isinstance(data, list) and len(data) > 0:
                for field in arabic_fields:
                    if field in data[0] and data[0][field]:
                        return data[0][field]

        return ""

    def _display_unicode_arabic(self, text: str) -> None:
        """Display Arabic text with Unicode enhancements for better rendering."""
        # Normalize Unicode characters (combines diacritics properly)
        normalized = unicodedata.normalize('NFC', text)

        # Add Unicode bidirectional formatting for better RTL display
        rtl_embedding = '\u202B'      # Right-to-Left Embedding
        pop_directional = '\u202C'    # Pop Directional Formatting
        rtl_mark = '\u200F'           # Right-to-Left Mark

        # Enhanced formatting with multiple RTL markers
        enhanced_text = f"{rtl_embedding}{rtl_mark}{normalized}{rtl_mark}{pop_directional}"

        # Display with styling
        click.echo()
        click.echo(click.style("Arabic Text:", fg='cyan', bold=True))
        click.echo(click.style(enhanced_text, fg='green', bold=True))
        click.echo()

    def _display_transliteration(self, text: str) -> None:
        """Display transliterated Arabic text for terminals without Arabic support."""
        transliterated = self._transliterate_arabic(text)

        click.echo(click.style("Transliteration:", fg='cyan', bold=True))
        click.echo(click.style(
            f"[{transliterated}]", fg='yellow', italic=True))
        click.echo()

    def _transliterate_arabic(self, text: str) -> str:
        """Convert Arabic text to Latin transliteration."""
        # Comprehensive Arabic to Latin mapping
        transliteration_map = {
            # Basic letters
            'ا': 'a', 'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h',
            'خ': 'kh', 'د': 'd', 'ذ': 'dh', 'ر': 'r', 'ز': 'z', 'س': 's',
            'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z', 'ع': "'",
            'غ': 'gh', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm',
            'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'y', 'ء': "'",

            # Special forms
            'ة': 'h', 'ى': 'a', 'ئ': "'", 'ؤ': "'", 'إ': 'i', 'أ': 'a',
            'آ': 'aa', 'لا': 'la',

            # Diacritics
            'َ': 'a', 'ُ': 'u', 'ِ': 'i', 'ْ': '', 'ّ': '', 'ً': 'an',
            'ٌ': 'un', 'ٍ': 'in', 'ٰ': 'a', 'ٱ': 'a',

            # Punctuation and spaces
            '،': ',', '؟': '?', '؛': ';', ' ': ' ', '\n': '\n', '\t': '\t',

            # Numbers
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
        }

        result = []
        for char in text:
            transliterated = transliteration_map.get(char, char)
            result.append(transliterated)

        # Clean up the result
        transliterated_text = ''.join(result)

        # Remove consecutive empty strings and clean whitespace
        import re
        transliterated_text = re.sub(r'\s+', ' ', transliterated_text)
        transliterated_text = transliterated_text.strip()

        return transliterated_text

    def _display_verse_reference(self, verse_data: Dict[str, Any]) -> None:
        """Display verse reference information."""
        # Extract reference information
        surah_name = self._extract_field(
            verse_data, ['surah_name', 'englishName'])
        surah_number = self._extract_field(
            verse_data, ['surah_number', 'number'])
        ayah_number = self._extract_field(
            verse_data, ['ayah_number', 'ayah', 'numberInSurah'])

        # Handle nested surah object
        if 'surah' in verse_data and isinstance(verse_data['surah'], dict):
            surah_obj = verse_data['surah']
            if not surah_name:
                surah_name = surah_obj.get('englishName', '')
            if not surah_number:
                surah_number = str(surah_obj.get('number', ''))

        if surah_name or surah_number or ayah_number:
            reference_parts = []

            if surah_name:
                reference_parts.append(f"Surah {surah_name}")

            if surah_number:
                reference_parts.append(f"({surah_number})")

            if ayah_number:
                reference_parts.append(f"Ayah {ayah_number}")

            reference = " ".join(reference_parts)
            click.echo(click.style(
                f"Reference: {reference}", fg='blue', bold=True))

    def _display_translation(self, verse_data: Dict[str, Any]) -> None:
        """Display verse translation if available."""
        translation = self._extract_field(
            verse_data, ['translation', 'text_translation', 'english'])
        translator = self._extract_field(
            verse_data, ['translator', 'edition', 'identifier'])

        if translation:
            click.echo()
            click.echo(click.style("Translation:", fg='cyan', bold=True))

            # Wrap long translations for better readability
            import textwrap
            wrapped_translation = textwrap.fill(
                translation, width=80, initial_indent="  ", subsequent_indent="  ")
            click.echo(click.style(wrapped_translation, fg='white'))

            if translator:
                click.echo(click.style(
                    f"  — {translator}", fg='magenta', dim=True))

    def _extract_field(self, data: Dict[str, Any], field_names: list) -> str:
        """Extract field from data using multiple possible field names."""
        for field_name in field_names:
            if field_name in data and data[field_name]:
                return str(data[field_name])

        # Check nested data
        if 'data' in data:
            nested_data = data['data']
            if isinstance(nested_data, dict):
                for field_name in field_names:
                    if field_name in nested_data and nested_data[field_name]:
                        return str(nested_data[field_name])
            elif isinstance(nested_data, list) and len(nested_data) > 0:
                for field_name in field_names:
                    if field_name in nested_data[0] and nested_data[0][field_name]:
                        return str(nested_data[0][field_name])

        # Check surah nested data
        if 'surah' in data and isinstance(data['surah'], dict):
            surah_data = data['surah']
            for field_name in field_names:
                if field_name in surah_data and surah_data[field_name]:
                    return str(surah_data[field_name])

        return ""

    def get_capabilities_info(self) -> Dict[str, Any]:
        """Get information about terminal capabilities for debugging."""
        return {
            'terminal_info': self.terminal_info,
            'arabic_support': self.arabic_support,
            'recommended_fonts': [
                'Noto Sans Arabic',
                'Amiri',
                'Cairo',
                'Scheherazade New',
                'DejaVu Sans'
            ] if not self.arabic_support else []
        }

    def display_font_recommendations(self) -> None:
        """Display font installation recommendations for better Arabic rendering."""
        if self.arabic_support:
            click.echo(click.style(
                "✅ Your terminal supports Arabic text display!", fg='green', bold=True))
            return

        click.echo(click.style(
            "💡 For optimal Arabic text display, consider installing Arabic fonts:", fg='yellow', bold=True))
        click.echo()

        platform_name = self.terminal_info['platform']

        if platform_name == 'Linux':
            click.echo(click.style("Ubuntu/Debian:", fg='cyan', bold=True))
            click.echo(
                "  sudo apt install fonts-noto fonts-amiri fonts-scheherazade-new")
            click.echo()
            click.echo(click.style("Fedora/RHEL:", fg='cyan', bold=True))
            click.echo(
                "  sudo dnf install google-noto-sans-arabic-fonts amiri-fonts")
            click.echo()
        elif platform_name == 'Darwin':  # macOS
            click.echo(click.style(
                "macOS (with Homebrew):", fg='cyan', bold=True))
            click.echo(
                "  brew install --cask font-noto-sans-arabic font-amiri font-scheherazade-new")
            click.echo()
        elif platform_name == 'Windows':
            click.echo(click.style("Windows:", fg='cyan', bold=True))
            click.echo(
                "  Download fonts from Google Fonts or install via Microsoft Store")
            click.echo()

        click.echo(click.style("Recommended fonts:", fg='green', bold=True))
        fonts = ["• Noto Sans Arabic", "• Amiri", "• Cairo",
                 "• Scheherazade New", "• DejaVu Sans"]
        for font in fonts:
            click.echo(f"  {font}")
