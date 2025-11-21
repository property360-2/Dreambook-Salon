"""
Fuzzy matching utility for typo tolerance and flexible string matching.
"""
from difflib import SequenceMatcher
import re


class FuzzyMatcher:
    """
    Provides fuzzy matching capabilities for handling typos and variations.
    """

    @staticmethod
    def similarity_ratio(a, b):
        """
        Calculate similarity ratio between two strings (0-1).
        1.0 = identical, 0.0 = completely different
        """
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    @staticmethod
    def find_best_match(query, candidates, threshold=0.75):
        """
        Find the best matching candidate from a list.

        Args:
            query: User input string
            candidates: List of candidate strings to match against
            threshold: Minimum similarity ratio (0-1) to consider a match

        Returns:
            tuple: (best_match, similarity_score) or (None, 0.0) if no match
        """
        best_match = None
        best_score = 0.0

        for candidate in candidates:
            score = FuzzyMatcher.similarity_ratio(query, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_score >= threshold:
            return best_match, best_score
        return None, 0.0

    @staticmethod
    def extract_service_name(message, service_names):
        """
        Extract service name from message with fuzzy matching.
        Handles variations like "facial", "facials", "fасial" (typo).

        Args:
            message: User message
            service_names: List of valid service names

        Returns:
            tuple: (service_name, confidence) or (None, 0.0)
        """
        message_lower = message.lower()

        # First try exact word match (highest confidence)
        for service in service_names:
            if re.search(r'\b' + re.escape(service.lower()) + r'\b', message_lower):
                return service, 1.0

        # Then try fuzzy match on extracted words
        words = re.findall(r'\b\w+\b', message_lower)
        for word in words:
            match, score = FuzzyMatcher.find_best_match(
                word, service_names, threshold=0.7
            )
            if match:
                return match, score

        return None, 0.0

    @staticmethod
    def extract_date_fuzzy(message):
        """
        Extract date from message with fuzzy matching for date patterns.
        Handles common date formats and typos.

        Returns:
            tuple: (date_string, confidence) or (None, 0.0)
        """
        # Common date patterns
        patterns = [
            # MM/DD/YYYY
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'mdy'),
            # DD/MM/YYYY
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'dmy'),
            # Month DD, YYYY
            (r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})', 'word'),
            # DD Month YYYY
            (r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})', 'word'),
            # Tomorrow, Today, Next Monday, etc.
            (r'\b(today|tomorrow|next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b', 'relative'),
        ]

        for pattern, date_type in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(0), 0.9

        return None, 0.0

    @staticmethod
    def levenshtein_distance(s1, s2):
        """
        Calculate Levenshtein distance between two strings.
        Lower distance = more similar.
        """
        if len(s1) < len(s2):
            return FuzzyMatcher.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def normalize_text(text):
        """
        Normalize text for better matching.
        - Lowercase
        - Remove extra whitespace
        - Remove punctuation (except apostrophes in contractions)
        """
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)  # Normalize spaces
        text = re.sub(r"[^\w\s']", '', text)  # Remove punctuation except apostrophes
        return text
