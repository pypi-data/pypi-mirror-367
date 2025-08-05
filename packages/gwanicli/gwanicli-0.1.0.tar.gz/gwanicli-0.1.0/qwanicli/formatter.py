"""
Formatting functions for rendering Quranic verses in various output formats.
Supports both human-readable console output and JSON format.
"""

import json
from typing import Dict, Any, Optional
import re
import os
import shutil
import unicodedata
import textwrap
import arabic_reshaper
from bidi.algorithm import get_display


# ANSI color codes for console styling
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Text colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_WHITE = '\033[47m'


def format_verse(verse_data: Dict[str, Any], json_output: bool = False,
                 use_colors: bool = True, arabic_style: str = 'simple') -> str:
    """
    Format verse data for display.

    Args:
        verse_data: Dictionary containing verse information from API
        json_output: If True, return JSON format; otherwise, human-readable format
        use_colors: Whether to use ANSI colors in console output
        arabic_style: Style for Arabic text formatting ('simple', 'bordered', 'highlighted')

    Returns:
        Formatted string representation of the verse
    """
    if json_output:
        return json.dumps(verse_data, indent=2, ensure_ascii=False)

    # Extract verse information from API response
    # Note: The actual structure depends on the API response format
    verse_info = _extract_verse_info(verse_data)

    return _format_console_output(verse_info, use_colors, arabic_style)


def _extract_verse_info(verse_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and normalize verse information from API response.

    Args:
        verse_data: Raw API response data

    Returns:
        Normalized verse information dictionary
    """
    normalized = {
        'surah_name': 'Unknown',
        'surah_number': 0,
        'ayah_number': 0,
        'arabic_text': '',
        'translation': '',
        'translator': 'Unknown'
    }

    try:
        # Handle normalized response format from our API client
        if 'arabic_text' in verse_data and 'translation' in verse_data:
            normalized.update({
                'arabic_text': verse_data.get('arabic_text', ''),
                'translation': verse_data.get('translation', ''),
                'ayah_number': verse_data.get('ayah_number', 0),
                'translator': verse_data.get('translator', 'Unknown')
            })

            surah_info = verse_data.get('surah', {})
            if surah_info:
                normalized.update({
                    'surah_name': surah_info.get('englishName', 'Unknown'),
                    'surah_number': surah_info.get('number', 0)
                })

        # Handle raw API response structures
        elif 'data' in verse_data:
            data = verse_data['data']

            # Single ayah response
            if isinstance(data, dict):
                normalized.update(_parse_single_ayah(data))

            # Multiple ayahs response
            elif isinstance(data, list) and len(data) > 0:
                # For multiple ayahs, format the first one or combine them
                normalized.update(_parse_multiple_ayahs(data))

        # Direct ayah data (no 'data' wrapper)
        elif 'text' in verse_data or 'arabic_text' in verse_data:
            normalized.update(_parse_single_ayah(verse_data))

    except (KeyError, TypeError, AttributeError) as e:
        # Fallback for unexpected response structure
        normalized['error'] = f"Failed to parse response: {e}"

    return normalized


def _parse_single_ayah(ayah_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a single ayah from API response."""
    parsed = {}

    # Common field mappings (adjust based on actual API)
    field_mappings = {
        'text': 'arabic_text',
        'arabic': 'arabic_text',
        'translation': 'translation',
        'englishName': 'surah_name',
        'name': 'surah_name',
        'number': 'surah_number',
        'ayah': 'ayah_number',
        'numberInSurah': 'ayah_number'
    }

    for api_field, normalized_field in field_mappings.items():
        if api_field in ayah_data:
            parsed[normalized_field] = ayah_data[api_field]

    # Handle nested surah information
    if 'surah' in ayah_data and isinstance(ayah_data['surah'], dict):
        surah_info = ayah_data['surah']
        if 'englishName' in surah_info:
            parsed['surah_name'] = surah_info['englishName']
        if 'number' in surah_info:
            parsed['surah_number'] = surah_info['number']

    # Handle edition/translator information
    if 'edition' in ayah_data and isinstance(ayah_data['edition'], dict):
        edition = ayah_data['edition']
        if 'englishName' in edition:
            parsed['translator'] = edition['englishName']

    return parsed


def _parse_multiple_ayahs(ayahs_data: list) -> Dict[str, Any]:
    """Parse multiple ayahs from API response."""
    if not ayahs_data:
        return {}

    # For now, just return the first ayah
    # TODO: Implement proper handling of multiple ayahs
    first_ayah = ayahs_data[0]
    parsed = _parse_single_ayah(first_ayah)

    # Add indication that there are multiple ayahs
    if len(ayahs_data) > 1:
        parsed['multiple_ayahs'] = True
        parsed['total_ayahs'] = len(ayahs_data)

    return parsed


def _format_console_output(verse_info: Dict[str, Any], use_colors: bool = True, arabic_style: str = 'simple') -> str:
    """
    Format verse information for console display.

    Args:
        verse_info: Normalized verse information
        use_colors: Whether to use ANSI colors
        arabic_style: Style for Arabic text formatting

    Returns:
        Formatted string for console output
    """
    if 'error' in verse_info:
        error_color = Colors.RED if use_colors else ''
        reset = Colors.RESET if use_colors else ''
        return f"{error_color}Error: {verse_info['error']}{reset}"

    lines = []

    # Header with surah and ayah information
    surah_name = verse_info.get('surah_name', 'Unknown')
    surah_number = verse_info.get('surah_number', 0)
    ayah_number = verse_info.get('ayah_number', 0)

    if use_colors:
        header = f"{Colors.BOLD}{Colors.CYAN}Surah {surah_name} ({surah_number}:{ayah_number}){Colors.RESET}"
    else:
        header = f"Surah {surah_name} ({surah_number}:{ayah_number})"

    lines.append(header)

    # Arabic text with improved formatting
    arabic_text = verse_info.get('arabic_text', '')
    if arabic_text:
        formatted_arabic = _format_arabic_text(arabic_text, arabic_style)
        if use_colors:
            # Use a distinctive color for Arabic text and ensure proper RTL display
            arabic_line = f"{Colors.BOLD}{Colors.GREEN}{formatted_arabic}{Colors.RESET}"
        else:
            arabic_line = formatted_arabic
        # Add blank line before Arabic text for better separation
        lines.append('')
        lines.append(arabic_line)
        lines.append('')  # Add blank line after Arabic text

    # Translation
    translation = verse_info.get('translation', '')
    if translation:
        if use_colors:
            translation_line = f"{Colors.DIM}\"{translation}\"{Colors.RESET}"
        else:
            translation_line = f'"{translation}"'
        lines.append(translation_line)

    # Translator information
    translator = verse_info.get('translator', '')
    if translator and translator != 'Unknown':
        if use_colors:
            translator_line = f"{Colors.DIM}— {translator}{Colors.RESET}"
        else:
            translator_line = f"— {translator}"
        lines.append(translator_line)

    # Multiple ayahs indicator
    if verse_info.get('multiple_ayahs'):
        total = verse_info.get('total_ayahs', 0)
        if use_colors:
            note = f"{Colors.YELLOW}Note: Showing first of {total} ayahs{Colors.RESET}"
        else:
            note = f"Note: Showing first of {total} ayahs"
        lines.append(note)

    return '\n'.join(lines)


def _format_arabic_text(text: str, arabic_style: str = 'simple') -> str:
    """Format Arabic text with proper wrapping and styling."""
    if not text:
        return ""

    # Get terminal width for proper text wrapping
    terminal_width = shutil.get_terminal_size().columns
    max_width = min(terminal_width - 10, 80)  # Leave some margin

    # Wrap Arabic text at word boundaries
    wrapped_text = wrap_arabic_text(text, max_width)

    # Apply styling based on the selected style
    if arabic_style == 'bordered':
        # Add a border around the Arabic text
        lines = wrapped_text.split('\n')
        max_line_length = max(len(line.strip())
                              for line in lines) if lines else 0
        border_width = min(max_line_length + 4, terminal_width - 2)

        top_border = '┌' + '─' * (border_width - 2) + '┐'
        bottom_border = '└' + '─' * (border_width - 2) + '┘'

        bordered_lines = [top_border]
        for line in lines:
            # Right-align Arabic text within the border
            padding = border_width - len(line.strip()) - 3
            bordered_line = '│ ' + ' ' * padding + line.strip() + ' │'
            bordered_lines.append(bordered_line)
        bordered_lines.append(bottom_border)

        return '\n'.join(bordered_lines)

    elif arabic_style == 'highlighted':
        # Add highlighting with background color (using ANSI codes)
        lines = wrapped_text.split('\n')
        highlighted_lines = []
        for line in lines:
            if line.strip():
                # Add cyan background and white text
                highlighted_line = f'\033[46m\033[37m {line.strip()} \033[0m'
                highlighted_lines.append(highlighted_line)
            else:
                highlighted_lines.append(line)
        return '\n'.join(highlighted_lines)

    else:  # simple style (default)
        return wrapped_text


def get_terminal_width() -> int:
    """Get the current terminal width, with a sensible default."""
    try:
        return shutil.get_terminal_size().columns
    except (AttributeError, OSError):
        return 80  # Default fallback


def wrap_arabic_text(text: str, width: int) -> str:
    """
    Wrap Arabic text at appropriate break points with proper reshaping and RTL display.

    Args:
        text: Arabic text to wrap
        width: Maximum line width

    Returns:
        Wrapped text with line breaks, properly reshaped and RTL-ordered
    """
    if not text:
        return ""

    if len(text) <= width:
        # For short text, still apply reshaping and RTL
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
        except (ImportError, Exception):
            # Fallback to basic text if reshaping fails
            return text

    try:
        # Reshape the text first for proper letter connections
        reshaped_text = arabic_reshaper.reshape(text)

        # Apply RTL ordering
        bidi_text = get_display(reshaped_text)

        # Use textwrap to handle line breaking at word boundaries
        wrapped_lines = textwrap.fill(bidi_text, width=width).split('\n')

        return '\n'.join(wrapped_lines)

    except (ImportError, Exception):
        # Fallback to the original implementation if reshaping libraries are not available
        # Arabic text flows right-to-left, so we need to be careful about wrapping
        words = text.split(' ')
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = get_display_width(word)

            # If adding this word would exceed the width, start a new line
            if current_length + word_length + len(current_line) > width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                current_line.append(word)
                current_length += word_length

        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)


def get_display_width(text: str) -> int:
    """
    Get the display width of text, accounting for Arabic characters.

    Args:
        text: Text to measure

    Returns:
        Display width in terminal columns
    """
    width = 0
    for char in text:
        # Arabic characters and most RTL characters take 1 column
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2  # Full-width characters
        else:
            width += 1  # Normal width characters
    return width


def format_surah_list(surahs: list, json_output: bool = False, use_colors: bool = True) -> str:
    """
    Format a list of surahs for display.

    Args:
        surahs: List of surah information dictionaries
        json_output: If True, return JSON format
        use_colors: Whether to use ANSI colors

    Returns:
        Formatted string representation
    """
    if json_output:
        return json.dumps(surahs, indent=2, ensure_ascii=False)

    lines = []

    if use_colors:
        header = f"{Colors.BOLD}{Colors.CYAN}Available Surahs:{Colors.RESET}"
    else:
        header = "Available Surahs:"

    lines.append(header)

    for surah in surahs:
        number = surah.get('number', 0)
        name = surah.get('englishName', 'Unknown')
        arabic_name = surah.get('name', '')

        if use_colors:
            line = f"{Colors.GREEN}{number:3d}.{Colors.RESET} {name}"
            if arabic_name:
                line += f" {Colors.DIM}({arabic_name}){Colors.RESET}"
        else:
            line = f"{number:3d}. {name}"
            if arabic_name:
                line += f" ({arabic_name})"

        lines.append(line)

    return '\n'.join(lines)


def format_error(error_message: str, use_colors: bool = True) -> str:
    """
    Format error messages for display.

    Args:
        error_message: Error message string
        use_colors: Whether to use ANSI colors

    Returns:
        Formatted error message
    """
    if use_colors:
        return f"{Colors.RED}Error: {error_message}{Colors.RESET}"
    else:
        return f"Error: {error_message}"


def format_success(message: str, use_colors: bool = True) -> str:
    """
    Format success messages for display.

    Args:
        message: Success message string
        use_colors: Whether to use ANSI colors

    Returns:
        Formatted success message
    """
    if use_colors:
        return f"{Colors.GREEN}{message}{Colors.RESET}"
    else:
        return message


def format_and_print_ayah(verse: Dict[str, Any], width: int = 80) -> None:
    """
    Format and print a Quranic verse with proper Arabic text reshaping and RTL display.

    This function handles the complete process of formatting Arabic text for terminal display:
    1. Reshapes Arabic letters for proper connection
    2. Applies RTL (right-to-left) text ordering
    3. Wraps text at specified width
    4. Prints formatted output to console

    Args:
        verse: Dictionary containing verse information with keys:
            - "surah_name" (str): Name of the surah
            - "surah_number" (int): Number of the surah (1-114)
            - "ayah_number" (int): Number of the ayah within the surah
            - "text" (str): Arabic text of the verse
            - "translation" (str): English translation of the verse
        width: Maximum line width for text wrapping (default: 80)

    Returns:
        None: Prints formatted output directly to console

    Example:
        verse = {
            "surah_name": "Al-Fatiha",
            "surah_number": 1,
            "ayah_number": 1,
            "text": "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
            "translation": "In the name of Allah, the Most Gracious, the Most Merciful"
        }
        format_and_print_ayah(verse, 60)
    """
    # Extract verse information
    surah_name = verse.get("surah_name", "Unknown")
    surah_number = verse.get("surah_number", 0)
    ayah_number = verse.get("ayah_number", 0)
    arabic_text = verse.get("text", "")
    translation = verse.get("translation", "")

    # Print header
    header = f"Surah {surah_name} ({surah_number}:{ayah_number})"
    print(header)

    # Process Arabic text if available
    if arabic_text:
        try:
            # Step 1: Reshape Arabic text for proper letter connections
            reshaped_text = arabic_reshaper.reshape(arabic_text)

            # Step 2: Apply RTL (right-to-left) ordering
            bidi_text = get_display(reshaped_text)

            # Step 3: Wrap text at specified width
            wrapped_text = textwrap.fill(bidi_text, width=width)

            # Print the properly formatted Arabic text
            print(wrapped_text)

        except ImportError:
            # Fallback if reshaping libraries are not available
            print(
                "Warning: Arabic reshaping libraries not available, using basic display")
            wrapped_text = textwrap.fill(arabic_text, width=width)
            print(wrapped_text)
        except Exception as e:
            # Fallback for any other processing errors
            print(
                f"Warning: Error processing Arabic text ({e}), using basic display")
            wrapped_text = textwrap.fill(arabic_text, width=width)
            print(wrapped_text)

    # Print English translation in quotes
    if translation:
        print(f'"{translation}"')


def format_and_print_ayah_from_api(verse_data: Dict[str, Any], width: int = 80) -> None:
    """
    Format and print a Quranic verse from API response data with proper Arabic reshaping.

    This is a convenience function that adapts the API response format to work with
    format_and_print_ayah(). It extracts the necessary fields from the API response
    and formats them for display.

    Args:
        verse_data: API response data containing verse information
        width: Maximum line width for text wrapping (default: 80)

    Returns:
        None: Prints formatted output directly to console

    Example:
        # API response data
        api_data = {
            'arabic_text': 'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ',
            'translation': 'In the name of Allah...',
            'surah': {'englishName': 'Al-Fatiha', 'number': 1},
            'ayah_number': 1
        }
        format_and_print_ayah_from_api(api_data, 60)
    """
    # Extract and normalize verse information from API response
    verse_info = _extract_verse_info(verse_data)

    # Convert to the format expected by format_and_print_ayah
    formatted_verse = {
        "surah_name": verse_info.get("surah_name", "Unknown"),
        "surah_number": verse_info.get("surah_number", 0),
        "ayah_number": verse_info.get("ayah_number", 0),
        "text": verse_info.get("arabic_text", ""),
        "translation": verse_info.get("translation", "")
    }

    # Use the main formatting function
    format_and_print_ayah(formatted_verse, width)
