"""
Filipino Language Processing Module for Pareng Boyong.

This module handles Filipino/Tagalog language processing, detection,
and cultural context enhancement for AI responses.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class Language(Enum):
    """Supported languages."""
    ENGLISH = "english"
    FILIPINO = "filipino"
    TAGALOG = "tagalog"
    MIXED = "mixed"


class LanguageProcessor:
    """
    Filipino language processor for cultural and linguistic integration.
    
    Handles:
    - Language detection (English, Filipino, Tagalog, Mixed)
    - Cultural context enhancement
    - Respectful communication patterns (po/opo)
    - Filipino phrase integration
    - Code-switching between English and Filipino
    """
    
    def __init__(self):
        """Initialize language processor."""
        self._filipino_words = self._load_filipino_vocabulary()
        self._respectful_patterns = self._load_respectful_patterns()
        self._cultural_phrases = self._load_cultural_phrases()
    
    def _load_filipino_vocabulary(self) -> List[str]:
        """Load common Filipino/Tagalog words for detection."""
        return [
            # Common greetings
            "kumusta", "kamusta", "musta", "magandang", "maayong",
            
            # Respectful terms
            "po", "opo", "ho", "sir", "ma'am", "ate", "kuya", "tito", "tita",
            
            # Common words
            "salamat", "maraming", "walang", "hindi", "oo", "tama", "mali",
            "pwede", "kaya", "gusto", "ayaw", "mahal", "libre",
            
            # Cultural terms
            "bayanihan", "kapamilya", "malasakit", "pakikipagkapwa",
            "utang", "loob", "hiya", "galang", "amor", "propio",
            
            # Time and social
            "umaga", "hapon", "gabi", "araw", "bukas", "kahapon",
            "pamilya", "kaibigan", "kapatid", "nanay", "tatay",
            
            # Actions and expressions
            "gumawa", "ginawa", "gagawin", "subukan", "tingnan",
            "pakinggan", "sabihin", "tanong", "sagot", "tulong",
            
            # Expressions
            "talaga", "naman", "kasi", "pero", "tapos", "sige", "ayos",
            "galing", "sulit", "libre", "mahal", "mura", "okay"
        ]
    
    def _load_respectful_patterns(self) -> Dict[str, List[str]]:
        """Load respectful communication patterns."""
        return {
            "greetings": [
                "Magandang {time} po!",
                "Good {time} po!",
                "{time} po, kumusta?",
                "Kumusta po kayo?"
            ],
            "responses": [
                "Opo, {response}",
                "Salamat po, {response}",
                "{response} po",
                "Sige po, {response}"
            ],
            "requests": [
                "Pwede po bang {request}?",
                "Maari po ba na {request}?",
                "Sana po {request}",
                "Request po: {request}"
            ],
            "apologies": [
                "Pasensya na po, {reason}",
                "Sorry po, {reason}",
                "Paumanhin po, {reason}",
                "Patawad po, {reason}"
            ]
        }
    
    def _load_cultural_phrases(self) -> Dict[str, List[str]]:
        """Load cultural phrases for different contexts."""
        return {
            "agreement": [
                "Oo nga po!", "Tama kayo!", "Exactly!", "Korek!",
                "Ganun talaga!", "Totoo yan!", "Right on!", "Yep!"
            ],
            "encouragement": [
                "Kaya mo yan!", "Go lang!", "Push mo lang!",
                "Walang surrender!", "Laban lang!", "You got this!"
            ],
            "appreciation": [
                "Salamat talaga!", "Thank you so much!",
                "Napaka-helpful!", "Grabe, ang galing!",
                "Sulit na sulit!", "Worth it talaga!"
            ],
            "collaboration": [
                "Sama-sama natin!", "Team up tayo!",
                "Bayanihan style!", "Tulungan nalang!",
                "Unity lang!", "Collective effort!"
            ],
            "cost_consciousness": [
                "Sulit yan!", "Mura lang!", "Free pa!",
                "Budget-friendly!", "Tipid mode!", "Affordable!"
            ],
            "quality_assurance": [
                "Quality guaranteed!", "Galing nito!",
                "High-class!", "Premium quality!",
                "World-class!", "Solid quality!"
            ]
        }
    
    def detect_language(self, text: str) -> Language:
        """
        Detect the primary language of the text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Detected language
        """
        if not text:
            return Language.ENGLISH
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return Language.ENGLISH
        
        # Count Filipino words
        filipino_count = sum(1 for word in words if word in self._filipino_words)
        filipino_ratio = filipino_count / len(words)
        
        # Language detection logic
        if filipino_ratio >= 0.3:
            return Language.FILIPINO
        elif filipino_ratio >= 0.1:
            return Language.MIXED
        else:
            return Language.ENGLISH
    
    def process_message(self, message: str, cultural_context: bool = True) -> Dict[str, Any]:
        """
        Process message with Filipino cultural and linguistic context.
        
        Args:
            message: Input message
            cultural_context: Whether to add cultural context
            
        Returns:
            Processed message with metadata
        """
        language = self.detect_language(message)
        
        processed = {
            "original": message,
            "content": message,
            "language": language.value,
            "cultural_elements": [],
            "respectful_level": self._assess_respectful_level(message),
            "context_suggestions": []
        }
        
        if cultural_context:
            # Add cultural enhancements
            processed["cultural_elements"] = self._extract_cultural_elements(message)
            processed["context_suggestions"] = self._suggest_cultural_context(message, language)
        
        return processed
    
    def _assess_respectful_level(self, text: str) -> str:
        """Assess the level of respectfulness in the text."""
        text_lower = text.lower()
        
        # High respect indicators
        if any(word in text_lower for word in ["po", "opo", "sir", "ma'am"]):
            return "high"
        
        # Medium respect indicators
        if any(word in text_lower for word in ["please", "salamat", "pakisuyo"]):
            return "medium"
        
        # Basic politeness
        if any(word in text_lower for word in ["thank", "sorry", "excuse"]):
            return "basic"
        
        return "casual"
    
    def _extract_cultural_elements(self, text: str) -> List[str]:
        """Extract Filipino cultural elements from text."""
        elements = []
        text_lower = text.lower()
        
        # Check for cultural values
        if "bayanihan" in text_lower or "sama-sama" in text_lower:
            elements.append("bayanihan_spirit")
        
        if any(word in text_lower for word in ["family", "pamilya", "kapamilya"]):
            elements.append("family_oriented")
        
        if any(word in text_lower for word in ["po", "opo", "respect"]):
            elements.append("respectful_communication")
        
        if any(word in text_lower for word in ["help", "tulong", "assist"]):
            elements.append("malasakit")
        
        return elements
    
    def _suggest_cultural_context(self, message: str, language: Language) -> List[str]:
        """Suggest cultural context enhancements."""
        suggestions = []
        
        if language == Language.ENGLISH:
            suggestions.append("consider_filipino_terms")
        
        if "help" in message.lower():
            suggestions.append("apply_malasakit")
            suggestions.append("offer_bayanihan_support")
        
        if any(word in message.lower() for word in ["error", "problem", "issue"]):
            suggestions.append("use_gentle_approach")
            suggestions.append("preserve_user_dignity")
        
        if any(word in message.lower() for word in ["success", "done", "completed"]):
            suggestions.append("celebrate_together")
            suggestions.append("express_gratitude")
        
        return suggestions
    
    def enhance_response(self, response: str, context: Dict[str, Any]) -> str:
        """
        Enhance response with Filipino cultural and linguistic elements.
        
        Args:
            response: Original response
            context: Context information
            
        Returns:
            Enhanced response with cultural elements
        """
        if not context.get("cultural_mode", True):
            return response
        
        enhanced = response
        
        # Add respectful elements if needed
        respectful_level = context.get("respectful_level", "casual")
        if respectful_level in ["high", "medium"]:
            enhanced = self._add_respectful_elements(enhanced)
        
        # Add cultural phrases based on context
        if context.get("success"):
            enhanced = self._add_success_phrases(enhanced)
        elif context.get("error"):
            enhanced = self._add_supportive_phrases(enhanced)
        elif context.get("collaboration"):
            enhanced = self._add_collaborative_phrases(enhanced)
        
        # Add cost consciousness if relevant
        if context.get("cost_related"):
            enhanced = self._add_cost_phrases(enhanced, context.get("cost_amount", 0))
        
        return enhanced
    
    def _add_respectful_elements(self, response: str) -> str:
        """Add respectful elements to response."""
        if not any(word in response.lower() for word in ["po", "opo"]):
            # Add 'po' at appropriate places
            if response.endswith('.'):
                return f"{response[:-1]} po."
            elif response.endswith('!'):
                return f"{response[:-1]} po!"
            else:
                return f"{response} po"
        return response
    
    def _add_success_phrases(self, response: str) -> str:
        """Add success-related cultural phrases."""
        import random
        phrases = self._cultural_phrases["appreciation"]
        phrase = random.choice(phrases)
        return f"{response} {phrase}"
    
    def _add_supportive_phrases(self, response: str) -> str:
        """Add supportive phrases for errors."""
        import random
        phrases = self._cultural_phrases["encouragement"]
        phrase = random.choice(phrases)
        return f"{response} {phrase}"
    
    def _add_collaborative_phrases(self, response: str) -> str:
        """Add collaborative phrases."""
        import random
        phrases = self._cultural_phrases["collaboration"]
        phrase = random.choice(phrases)
        return f"{response} {phrase}"
    
    def _add_cost_phrases(self, response: str, cost: float) -> str:
        """Add cost-related cultural phrases."""
        import random
        
        if cost == 0:
            phrases = ["Free pa!", "Walang bayad!", "Libre lang!"]
        elif cost < 0.01:
            phrases = self._cultural_phrases["cost_consciousness"]
        else:
            phrases = self._cultural_phrases["quality_assurance"]
        
        phrase = random.choice(phrases)
        return f"{response} {phrase}"
    
    def get_cultural_greeting(self, time_context: str = "general") -> str:
        """Get culturally appropriate greeting."""
        from .greetings import get_time_appropriate_greeting
        return get_time_appropriate_greeting()
    
    def translate_key_terms(self, text: str, direction: str = "to_filipino") -> str:
        """
        Translate key terms between English and Filipino.
        
        Args:
            text: Text to translate terms in
            direction: "to_filipino" or "to_english"
            
        Returns:
            Text with key terms translated
        """
        translations = {
            "to_filipino": {
                "hello": "kumusta",
                "thank you": "salamat",
                "please": "pakisuyo",
                "sorry": "pasensya",
                "yes": "oo",
                "no": "hindi",
                "good": "mabuti",
                "help": "tulong",
                "friend": "kaibigan",
                "family": "pamilya",
                "work": "trabaho",
                "money": "pera",
                "free": "libre",
                "expensive": "mahal",
                "cheap": "mura"
            },
            "to_english": {v: k for k, v in {
                "hello": "kumusta",
                "thank you": "salamat", 
                "please": "pakisuyo",
                "sorry": "pasensya",
                "yes": "oo",
                "no": "hindi",
                "good": "mabuti",
                "help": "tulong",
                "friend": "kaibigan",
                "family": "pamilya",
                "work": "trabaho",
                "money": "pera",
                "free": "libre",
                "expensive": "mahal",
                "cheap": "mura"
            }.items()}
        }
        
        translation_dict = translations.get(direction, {})
        
        for english, filipino in translation_dict.items():
            text = re.sub(r'\b' + re.escape(english) + r'\b', filipino, text, flags=re.IGNORECASE)
            
        return text
    
    def __str__(self) -> str:
        return f"LanguageProcessor(vocabulary={len(self._filipino_words)} words)"
    
    def __repr__(self) -> str:
        return f"LanguageProcessor(filipino_words={len(self._filipino_words)}, patterns={len(self._respectful_patterns)})"