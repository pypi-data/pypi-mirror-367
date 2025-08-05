"""
HTTP client for accessing Quran API endpoints.
Provides methods for fetching random verses and specific surahs.
"""

import requests
from typing import Dict, Any, Optional, Union
import json


class ApiError(Exception):
    """Custom exception for API-related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class QuranApiClient:
    """Client for interacting with the Al-Quran Cloud API."""

    def __init__(self, base_url: str = "https://api.alquran.cloud/v1"):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API endpoint
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GwaniCLI/0.1.0',
            'Accept': 'application/json'
        })

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a HTTP request to the API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Parsed JSON response data

        Raises:
            ApiError: If the request fails or returns non-200 status
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get(
                        'message', f'HTTP {response.status_code}')
                except json.JSONDecodeError:
                    error_message = f'HTTP {response.status_code}: {response.text[:100]}'

                # Provide more specific error messages based on status code
                if response.status_code == 404:
                    raise ApiError(
                        "The requested verse or surah was not found. Please check your input.")
                elif response.status_code == 403:
                    raise ApiError(
                        "Access to the Quran API was denied. Please try again later.")
                elif response.status_code == 429:
                    raise ApiError(
                        "Too many requests. Please wait a moment before trying again.")
                elif response.status_code >= 500:
                    raise ApiError(
                        "The Quran API is temporarily unavailable. Please try again later.")
                else:
                    raise ApiError(f"API request failed: {error_message}",
                                   status_code=response.status_code,
                                   response_data=error_data if 'error_data' in locals() else None)

            return response.json()

        except requests.exceptions.Timeout:
            raise ApiError(
                "The request took too long to complete. Please check your internet connection and try again.")
        except requests.exceptions.ConnectionError:
            raise ApiError(
                "Unable to connect to the Quran API. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise ApiError(
                f"Network request failed. Please check your internet connection and try again.")
        except json.JSONDecodeError:
            raise ApiError(
                "Received invalid data from the Quran API. Please try again.")

    def get_random_ayah(self, translation: str = "en.sahih") -> Dict[str, Any]:
        """
        Fetch a random Quranic verse with translation.

        Args:
            translation: Translation identifier (e.g., 'en.sahih', 'en.pickthall')

        Returns:
            Dictionary containing verse data with Arabic text and translation

        Raises:
            ApiError: If the API request fails
        """
        import random

        try:
            # Generate random surah and ayah numbers
            # Use known surah lengths for more accurate random selection
            surah_lengths = self._get_surah_lengths()
            surah_num = random.randint(1, 114)
            # Fallback to longest surah
            max_ayah = surah_lengths.get(surah_num, 286)
            ayah_num = random.randint(1, max_ayah)

            return self.get_ayah_from_surah(surah_num, ayah_num, translation)

        except Exception as e:
            raise ApiError(f"Failed to fetch random ayah: {str(e)}")

    def get_ayah_from_surah(self, surah: Union[str, int], ayah: Optional[int] = None,
                            translation: str = "en.sahih") -> Dict[str, Any]:
        """
        Fetch specific verse(s) from a surah.

        Args:
            surah: Surah number (1-114) or name
            ayah: Specific ayah number (optional, if None returns entire surah)
            translation: Translation identifier

        Returns:
            Dictionary containing verse data

        Raises:
            ApiError: If the API request fails
        """
        try:
            # Convert surah name to number if needed
            surah_num = self._resolve_surah_identifier(surah)

            if ayah is not None:
                # Get specific ayah with both Arabic and translation
                endpoint = f"ayah/{surah_num}:{ayah}/editions/quran-uthmani,{translation}"
            else:
                # Get entire surah
                endpoint = f"surah/{surah_num}/{translation}"

            response_data = self._make_request(endpoint)

            # Process and normalize the response structure
            return self._normalize_response(response_data, ayah is not None)

        except Exception as e:
            if isinstance(e, ApiError):
                raise
            raise ApiError(f"Failed to fetch ayah from surah: {str(e)}")

    def _resolve_surah_identifier(self, identifier: Union[str, int]) -> int:
        """
        Convert surah name or number to a valid surah number.

        Args:
            identifier: Surah name or number

        Returns:
            Surah number (1-114)

        Raises:
            ApiError: If the identifier is invalid
        """
        if isinstance(identifier, int):
            if 1 <= identifier <= 114:
                return identifier
            else:
                raise ApiError(
                    f"Invalid surah number: {identifier}. Must be between 1 and 114.")

        # TODO: Implement surah name to number mapping
        # For now, try to convert string to int
        try:
            surah_num = int(identifier)
            if 1 <= surah_num <= 114:
                return surah_num
            else:
                raise ApiError(
                    f"Invalid surah number: {surah_num}. Must be between 1 and 114.")
        except ValueError:
            # Handle surah name mapping
            surah_names = self._get_surah_name_mapping()

            normalized_name = identifier.lower().replace(
                '-', '').replace('_', '').replace(' ', '')
            for name, num in surah_names.items():
                if normalized_name in name.replace('-', '').replace(' ', ''):
                    return num

            raise ApiError(f"Unknown surah name: {identifier}")

    def _get_surah_name_mapping(self) -> Dict[str, int]:
        """Get mapping of surah names to numbers."""
        return {
            'fatiha': 1, 'al-fatiha': 1, 'alfatiha': 1, 'opening': 1,
            'baqara': 2, 'al-baqara': 2, 'albaqara': 2, 'cow': 2,
            'ali-imran': 3, 'aliimran': 3, 'family of imran': 3,
            'nisa': 4, 'an-nisa': 4, 'annisa': 4, 'women': 4,
            'maida': 5, 'al-maida': 5, 'almaida': 5, 'table': 5,
            'anam': 6, 'al-anam': 6, 'alanam': 6, 'cattle': 6,
            'araf': 7, 'al-araf': 7, 'alaraf': 7, 'heights': 7,
            'anfal': 8, 'al-anfal': 8, 'alanfal': 8, 'spoils': 8,
            'tawba': 9, 'at-tawba': 9, 'attawba': 9, 'repentance': 9,
            'yunus': 10, 'jonah': 10,
            'hud': 11,
            'yusuf': 12, 'joseph': 12,
            'rad': 13, 'ar-rad': 13, 'arrad': 13, 'thunder': 13,
            'ibrahim': 14, 'abraham': 14,
            'hijr': 15, 'al-hijr': 15, 'alhijr': 15,
            'nahl': 16, 'an-nahl': 16, 'annahl': 16, 'bee': 16,
            'isra': 17, 'al-isra': 17, 'alisra': 17, 'night journey': 17,
            'kahf': 18, 'al-kahf': 18, 'alkahf': 18, 'cave': 18,
            'maryam': 19, 'mary': 19,
            'taha': 20, 'ta-ha': 20,
            'anbiya': 21, 'al-anbiya': 21, 'alanbiya': 21, 'prophets': 21,
            'hajj': 22, 'al-hajj': 22, 'alhajj': 22, 'pilgrimage': 22,
            'muminun': 23, 'al-muminun': 23, 'almuminun': 23, 'believers': 23,
            'nur': 24, 'an-nur': 24, 'annur': 24, 'light': 24,
            'furqan': 25, 'al-furqan': 25, 'alfurqan': 25, 'criterion': 25,
        }

    def _get_surah_lengths(self) -> Dict[int, int]:
        """Get the number of ayahs in each surah."""
        return {
            1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
            11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
            21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
            31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
            41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
            51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
            61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
            71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
            81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
            91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
            101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
            111: 5, 112: 4, 113: 5, 114: 6
        }

    def _normalize_response(self, response_data: Dict[str, Any], is_single_ayah: bool) -> Dict[str, Any]:
        """
        Normalize API response to a consistent format.

        Args:
            response_data: Raw API response
            is_single_ayah: Whether this is a single ayah response

        Returns:
            Normalized response data
        """
        if response_data.get('code') != 200:
            raise ApiError(
                f"API error: {response_data.get('status', 'Unknown error')}")

        data = response_data.get('data', {})

        if is_single_ayah and isinstance(data, list):
            # Multi-edition response (Arabic + Translation)
            if len(data) >= 2:
                arabic_data = data[0]  # First is Arabic
                translation_data = data[1]  # Second is translation

                return {
                    'arabic_text': arabic_data.get('text', ''),
                    'translation': translation_data.get('text', ''),
                    'surah': arabic_data.get('surah', {}),
                    'ayah_number': arabic_data.get('numberInSurah', 0),
                    'translator': translation_data.get('edition', {}).get('englishName', ''),
                    'edition_info': translation_data.get('edition', {}),
                    'meta': {
                        'juz': arabic_data.get('juz'),
                        'page': arabic_data.get('page'),
                        'ruku': arabic_data.get('ruku')
                    }
                }
            else:
                # Single edition response
                single_data = data[0] if data else {}
                return {
                    'arabic_text': single_data.get('text', '') if single_data.get('edition', {}).get('type') == 'quran' else '',
                    'translation': single_data.get('text', '') if single_data.get('edition', {}).get('type') == 'translation' else '',
                    'surah': single_data.get('surah', {}),
                    'ayah_number': single_data.get('numberInSurah', 0),
                    'translator': single_data.get('edition', {}).get('englishName', ''),
                    'edition_info': single_data.get('edition', {}),
                    'meta': {
                        'juz': single_data.get('juz'),
                        'page': single_data.get('page'),
                        'ruku': single_data.get('ruku')
                    }
                }
        else:
            # Handle other response formats (surah, etc.)
            return response_data

    def get_available_translations(self) -> Dict[str, Any]:
        """
        Get list of available translations.

        Returns:
            Dictionary containing available translation options
        """
        # TODO: Implement if API provides translation list endpoint
        endpoint = "edition/type/translation"
        return self._make_request(endpoint)

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
