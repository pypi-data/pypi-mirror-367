"""
Filipino Greetings and Cultural Responses Module.

This module provides culturally appropriate greetings, responses,
and conversational patterns for Filipino cultural integration.
"""

import random
from datetime import datetime
from typing import List, Dict, Optional
import pytz


def get_random_greeting() -> str:
    """
    Get a random Filipino greeting.
    
    Returns:
        Random Filipino greeting
    """
    greetings = [
        "Kumusta!",
        "Kamusta ka?",
        "Hoy! Anong balita?",
        "Hello po!",
        "Hi there, kaibigan!",
        "Musta na?",
        "Oy, kumusta?",
        "Halo! How are you?",
        "Hey, pare/mare!",
        "Greetings, kapatid!"
    ]
    
    return random.choice(greetings)


def get_time_appropriate_greeting() -> str:
    """
    Get a time-appropriate greeting based on Philippine time.
    
    Returns:
        Time-appropriate Filipino greeting
    """
    ph_tz = pytz.timezone('Asia/Manila')
    ph_time = datetime.now(ph_tz)
    hour = ph_time.hour
    
    if 5 <= hour < 12:
        morning_greetings = [
            "Magandang umaga po!",
            "Good morning! Kumusta ang gising?",
            "Morning! Ready na ba tayo?",
            "Umaga na! Kape muna?",
            "Good morning, kapatid!",
            "Magandang umaga! Anong plano today?"
        ]
        return random.choice(morning_greetings)
    
    elif 12 <= hour < 18:
        afternoon_greetings = [
            "Magandang hapon po!",
            "Good afternoon! Kumain na kayo?",
            "Afternoon! Kumusta ang araw?",
            "Hapon na! Busy day?",
            "Good afternoon, kaibigan!",
            "Magandang hapon! Anong ginagawa?"
        ]
        return random.choice(afternoon_greetings)
    
    elif 18 <= hour < 22:
        evening_greetings = [
            "Magandang gabi po!",
            "Good evening! Uwi na kayo?",
            "Gabi na! Dinner time?",
            "Evening! Pagod na ba?",
            "Good evening, kapatid!",
            "Magandang gabi! Rest day na ba?"
        ]
        return random.choice(evening_greetings)
    
    else:
        late_greetings = [
            "Gabi na po! Hindi pa kayo tulog?",
            "Late night! Working pa?",
            "Madaling araw na! Take care!",
            "Puyat session? Ingat po!",
            "Late night coding? Respect!",
            "Gabi pa pero awake pa! Sipag!"
        ]
        return random.choice(late_greetings)


def get_cultural_response(response_type: str, context: Optional[Dict] = None) -> str:
    """
    Get culturally appropriate response based on type and context.
    
    Args:
        response_type: Type of response needed
        context: Additional context for the response
        
    Returns:
        Culturally appropriate Filipino response
    """
    context = context or {}
    
    if response_type == "acknowledgment":
        return _get_acknowledgment_response(context)
    elif response_type == "success":
        return _get_success_response(context)
    elif response_type == "error":
        return _get_error_response(context)
    elif response_type == "working":
        return _get_working_response(context)
    elif response_type == "cost_concern":
        return _get_cost_concern_response(context)
    elif response_type == "completion":
        return _get_completion_response(context)
    else:
        return "Opo, noted po!"


def _get_acknowledgment_response(context: Dict) -> str:
    """Get acknowledgment responses."""
    responses = [
        "Sige po! Got it!",
        "Oo nga! Noted!",
        "Okay lang! Let's do it!",
        "Copy that, boss!",
        "Roger! Understood!",
        "Yep! On it na!",
        "Sige! Tara na!",
        "Opo! Will work on it!",
        "Noted po! Salamat!",
        "Alright! Challenge accepted!"
    ]
    
    return random.choice(responses)


def _get_success_response(context: Dict) -> str:
    """Get success responses."""
    responses = [
        "Yay! Success! 🎉",
        "Ayun! Galing natin! ✨",
        "Success! Proud ako sa atin! 👏",
        "Yun oh! Mission accomplished! 🚀",
        "Galing! We did it! 💪",
        "Success story! Bayanihan power! 🇵🇭",
        "Boom! Achievement unlocked! 🏆",
        "Yesss! Team work wins! 🤝",
        "Salamat sa collaboration! Success! ⭐",
        "Ayos! Perfect execution! 💯"
    ]
    
    return random.choice(responses)


def _get_error_response(context: Dict) -> str:
    """Get error responses."""
    responses = [
        "Ay pasensya na po! May issue.",
        "Naku! May error. Don't worry!",
        "Oops! Technical difficulty lang!",
        "Sorry po! May glitch, kaya natin 'to!",
        "Ay mali! But we can fix this!",
        "Houston, may problema! But no worries!",
        "Error alert! Let's troubleshoot!",
        "Hala! May bug, but we got this!",
        "Issue detected! Solution mode activated!",
        "Pasensya na! Let me try another way!"
    ]
    
    return random.choice(responses)


def _get_working_response(context: Dict) -> str:
    """Get working/processing responses."""
    responses = [
        "Sandali lang po, ginagawa ko na...",
        "Working on it! One moment...",
        "Processing... sandali lang!",
        "Eto na po, wait lang...",
        "Ginagawa ko na! Patience lang!",
        "On it na! Loading...",
        "Working... almost there!",
        "Processing your request po...",
        "Eto na, konting tiis pa...",
        "Hang tight! Working my magic!"
    ]
    
    return random.choice(responses)


def _get_cost_concern_response(context: Dict) -> str:
    """Get cost-conscious responses."""
    cost = context.get('cost', 0)
    
    if cost == 0:
        free_responses = [
            "FREE yan! Walang bayad! 🆓",
            "Zero cost! Libre lang! 💝",
            "No charge! On the house! 🏠",
            "FREE service! Sulit! ✨",
            "Walang gastos! Free lang! 🎁",
            "Complimentary! Libre po! 💚"
        ]
        return random.choice(free_responses)
    
    elif cost < 0.01:
        cheap_responses = [
            f"Super cheap lang! ${cost:.3f} lang! 💰",
            f"Mura lang yan! ${cost:.3f} only! 🪙",
            f"Budget-friendly! ${cost:.3f} lang! 💳",
            f"Sulit! ${cost:.3f} lang naman! ⭐",
            f"Cost-effective! ${cost:.3f}! 📊",
            f"Affordable! ${cost:.3f} lang yan! 💡"
        ]
        return random.choice(cheap_responses)
    
    else:
        expensive_responses = [
            f"May kaunting cost - ${cost:.3f}. Sulit pa rin! 💎",
            f"Premium quality! ${cost:.3f} lang naman! ✨",
            f"Investment sa quality! ${cost:.3f}! 🏆",
            f"Worth it naman! ${cost:.3f}! 👍",
            f"Quality service! ${cost:.3f} cost! ⭐",
            f"Professional grade! ${cost:.3f}! 💼"
        ]
        return random.choice(expensive_responses)


def _get_completion_response(context: Dict) -> str:
    """Get completion responses."""
    responses = [
        "Tapos na po! All done! ✅",
        "Completed! Yay! 🎯",
        "Finished! Check it out! 👀",
        "Done na! How was it? 🤔",
        "Task completed! Success! 🌟",
        "All set! Ready na! 🚀", 
        "Mission accomplished! 🏁",
        "Delivered! Hope you like it! 💝",
        "Complete na! Next task? 📋",
        "Yun lang! What's next? ➡️"
    ]
    
    return random.choice(responses)


def get_filipino_exclamations() -> List[str]:
    """
    Get list of Filipino exclamations and expressions.
    
    Returns:
        List of Filipino exclamations
    """
    return [
        "Ay naku!",
        "Hala!",
        "Naku!",
        "Grabe!",
        "Wow!",
        "Yun oh!",
        "Ayun!",
        "Galing!",
        "Sulit!",
        "Nice!",
        "Salamat!",
        "Thanks!",
        "Awesome!",
        "Cool!",
        "Amazing!",
        "Perfect!",
        "Solid!",
        "Winner!",
        "Champion!",
        "Boss!"
    ]


def get_transition_phrases() -> List[str]:
    """
    Get Filipino transition phrases for conversations.
    
    Returns:
        List of transition phrases
    """
    return [
        "Sige, moving on...",
        "Okay, next naman...",
        "Alright, proceed tayo...",
        "So, ano pa...",
        "Then, tuloy natin...",
        "Now, let's...",
        "Eto na, next step...",
        "Sige, continue...",
        "Okay lang, go tayo...",
        "Tara, next na..."
    ]


def get_collaborative_phrases() -> List[str]:
    """
    Get collaborative phrases reflecting bayanihan spirit.
    
    Returns:
        List of collaborative phrases
    """
    return [
        "Sama-sama natin 'to!",
        "Team work tayo!",
        "Bayanihan spirit!",
        "Together, kaya natin!",
        "Collaboration mode!",
        "Partnership tayo dito!",
        "Tulong-tulong!",
        "Unity lang!",
        "Collective effort!",
        "Damayan system!"
    ]