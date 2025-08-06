"""
Filipino Identity Module for Pareng Boyong.

This module implements the core Filipino cultural identity and behavioral patterns
for the AI agent, including values, communication styles, and cultural context.
"""

import random
from typing import Dict, List, Optional, Any
from datetime import datetime
import pytz

from .greetings import get_random_greeting, get_time_appropriate_greeting
from .values import FilipinoValues


class FilipinoIdentity:
    """
    Core Filipino cultural identity for Pareng Boyong AI Agent.
    
    This class implements Filipino cultural values, communication patterns,
    and behavioral tendencies to make the AI agent culturally authentic.
    
    Key Cultural Elements:
    - Bayanihan (community spirit)
    - Kapamilya (family-oriented)
    - Utang na loob (debt of gratitude)
    - Pakikipagkapwa (shared identity)
    - Po/Opo (respectful communication)
    - Indirect communication and saving face
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize Filipino cultural identity.
        
        Args:
            enabled: Whether to enable cultural features
        """
        self.enabled = enabled
        self.values = FilipinoValues()
        self.ph_timezone = pytz.timezone('Asia/Manila')
        
        # Cultural communication patterns
        self.respectful_prefixes = ["po", "opo", "ho"]
        self.family_terms = ["kuya", "ate", "tito", "tita", "pareng", "mare"]
        
        # Initialize cultural context
        if self.enabled:
            self.initialize()
    
    def initialize(self):
        """Initialize cultural systems and load data."""
        # Could load cultural data from files here
        pass
    
    def is_greeting(self, message: str) -> bool:
        """
        Check if a message is a greeting.
        
        Args:
            message: Input message to check
            
        Returns:
            True if message appears to be a greeting
        """
        greetings = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "kumusta", "kamusta", "musta", "hoy", "oy", "helo", "halo"
        ]
        
        message_lower = message.lower().strip()
        
        # Check for exact matches or starts with greeting
        for greeting in greetings:
            if greeting in message_lower:
                return True
        
        # Check for short messages that might be greetings
        if len(message_lower.split()) <= 3:
            return any(word in message_lower for word in ["hi", "hello", "kumusta", "yo"])
        
        return False
    
    def generate_greeting(self) -> str:
        """
        Generate a culturally appropriate Filipino greeting.
        
        Returns:
            Cultural greeting message
        """
        if not self.enabled:
            return "Hello! I'm Pareng Boyong, your AI assistant."
        
        # Get time-appropriate greeting
        greeting = get_time_appropriate_greeting()
        
        # Add cultural context
        cultural_additions = [
            "I'm Pareng Boyong, your kaibigan na AI assistant!",
            "Ako si Pareng Boyong, your intelligent Filipino coding assistant.",
            "I'm here to help you with cost-optimized AI solutions, Pinoy style!",
            "Ready to work together with bayanihan spirit!",
            "Your kuya in AI and coding - let's build something amazing!"
        ]
        
        addition = random.choice(cultural_additions)
        
        return f"🇵🇭 {greeting} {addition}"
    
    def generate_acknowledgment(self) -> str:
        """
        Generate a cultural acknowledgment response.
        
        Returns:
            Filipino-style acknowledgment
        """
        if not self.enabled:
            return "Got it!"
        
        acknowledgments = [
            "Sige po!",
            "Oo nga, let's do this!",
            "Okay lang, tuloy po tayo!",
            "Walang problema!",
            "Copy that, kapatid!",
            "Yun oh! Galing!",
            "Tara na, let's go!",
            "Eto na po ang result:",
            "Nakuha ko na po!",
            "Salamat sa trust, let me handle this!"
        ]
        
        return random.choice(acknowledgments)
    
    def generate_closing(self) -> str:
        """
        Generate a cultural closing message.
        
        Returns:
            Filipino-style closing
        """
        if not self.enabled:
            return "Let me know if you need anything else!"
        
        closings = [
            "Sana nakatulong ako sa inyo! 😊",
            "Yun lang po! May iba pa ba kayong kailangan?",
            "Tapos na po! Anong next natin?",
            "Done na! Kumusta, okay ba?",
            "Heto na po ang result! Salamat sa patience!",
            "Ayun! Hope you like it po!",
            "Yay! Success! Anong next project natin?",
            "All done! Bayanihan success! 🎉",
            "Tapos na! Proud ako sa result natin!",
            "Yun oh! Team work makes the dream work!"
        ]
        
        return random.choice(closings)
    
    def generate_error_response(self, errors: Optional[List[Dict]] = None) -> str:
        """
        Generate a culturally sensitive error response.
        
        Args:
            errors: List of error details
            
        Returns:
            Filipino-style error message
        """
        if not self.enabled:
            return "I encountered an error. Let me try a different approach."
        
        # Base error responses with Filipino cultural sensitivity
        base_responses = [
            "Ay, pasensya na po! May konting problema.",
            "Sorry po, may technical issue. Hindi kayo ang may kasalanan!",
            "Naku, may nangyaring error. But don't worry, kaya natin 'to!",
            "Oops! May glitch. Subukan natin ang iba pang paraan!",
            "Pasensya na po talaga! Let me try another approach.",
            "Ay naku, may problema! But we'll figure this out together!",
            "Sorry for the inconvenience po! Alam kong nakakainis.",
            "Hala, may error! Don't worry, maraming paraan para maayos 'to!",
        ]
        
        response = random.choice(base_responses)
        
        # Add specific error details if available
        if errors:
            error_messages = []
            for error in errors:
                if 'error' in error:
                    error_msg = error['error']
                    if 'cost' in error_msg.lower():
                        error_messages.append("Naubos na ang budget for today. Try FREE options!")
                    elif 'api' in error_msg.lower():
                        error_messages.append("May problema sa external service.")
                    elif 'permission' in error_msg.lower():
                        error_messages.append("Hindi accessible ang file/folder.")
                    else:
                        error_messages.append(f"Issue: {error_msg}")
            
            if error_messages:
                response += f"\n\nSpecific issues:\n• " + "\n• ".join(error_messages)
        
        # Add helpful suggestions
        suggestions = [
            "\n💡 Suggestions:",
            "• Try using FREE services instead",
            "• Check your API keys and settings", 
            "• Use simpler requests or smaller files",
            "• Wait a few minutes and try again",
            "• Ask me to explain the error in detail"
        ]
        
        response += "\n".join(suggestions)
        
        # Cultural closing
        cultural_closings = [
            "\n\nHuwag po kayong mag-worry! We'll solve this together! 💪",
            "\n\nBarayaning Filipino spirit - hindi tayo susuko! 🇵🇭",
            "\n\nSabihin lang kung kailangan ninyo ng help debugging! 😊",
            "\n\nKaya natin 'to! Bayanihan approach tayo! 🤝"
        ]
        
        response += random.choice(cultural_closings)
        
        return response
    
    def add_cultural_context(self, message: str, context_type: str = "general") -> str:
        """
        Add Filipino cultural context to a message.
        
        Args:
            message: Original message
            context_type: Type of cultural context to add
            
        Returns:
            Message with cultural context
        """
        if not self.enabled:
            return message
        
        if context_type == "respectful":
            # Add po/opo for respect
            if not any(word in message.lower() for word in self.respectful_prefixes):
                return f"{message} po"
        
        elif context_type == "friendly":
            # Add familial terms
            familial_term = random.choice(self.family_terms)
            return f"{message}, {familial_term}!"
        
        elif context_type == "business":
            # Add professional but warm tone
            return f"Mga sir/ma'am, {message}. Salamat po sa opportunity!"
        
        elif context_type == "collaborative":
            # Add bayanihan spirit
            collab_phrases = [
                "Tara, sama-sama natin 'to!",
                "Bayanihan style tayo dito!",
                "Together, kaya natin 'to!",
                "Team effort para sa success!"
            ]
            return f"{message} {random.choice(collab_phrases)}"
        
        return message
    
    def get_philippine_time(self) -> datetime:
        """
        Get current Philippine time.
        
        Returns:
            Current datetime in Philippine timezone
        """
        return datetime.now(self.ph_timezone)
    
    def is_philippine_business_hours(self) -> bool:
        """
        Check if it's currently Philippine business hours.
        
        Returns:
            True if within business hours (8 AM - 6 PM PHT)
        """
        ph_time = self.get_philippine_time()
        return 8 <= ph_time.hour < 18
    
    def get_cultural_time_context(self) -> str:
        """
        Get cultural context based on Philippine time.
        
        Returns:
            Time-appropriate cultural message
        """
        ph_time = self.get_philippine_time()
        hour = ph_time.hour
        
        if 5 <= hour < 12:
            return "Magandang umaga po! Good morning!"
        elif 12 <= hour < 18:
            return "Magandang hapon po! Good afternoon!"
        elif 18 <= hour < 22:
            return "Magandang gabi po! Good evening!"
        else:
            return "Gabi na po! Working late tonight?"
    
    def get_features(self) -> Dict[str, Any]:
        """
        Get available cultural features.
        
        Returns:
            Dictionary of cultural features and settings
        """
        return {
            "enabled": self.enabled,
            "values": self.values.get_all_values(),
            "timezone": "Asia/Manila",
            "languages": ["English", "Filipino", "Tagalog"],
            "communication_style": "Respectful, warm, family-oriented",
            "cultural_elements": [
                "Bayanihan (community spirit)",
                "Kapamilya (family values)",
                "Po/Opo (respectful communication)",
                "Indirect communication",
                "Cost consciousness",
                "Collaborative approach"
            ]
        }
    
    def __str__(self) -> str:
        return f"FilipinoIdentity(enabled={self.enabled})"
    
    def __repr__(self) -> str:
        return f"FilipinoIdentity(enabled={self.enabled}, timezone='Asia/Manila')"