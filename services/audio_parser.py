"""
Audio Transcript Parser
Converts natural language transcript to structured user profile data
Uses regex and keyword matching (no LLM)
"""
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AudioParser:
    """Parse transcript text into structured user profile"""
    
    # Indian states mapping (with common variations)
    STATES = {
        'andhra pradesh': 'Andhra Pradesh', 'andhra': 'Andhra Pradesh',
        'arunachal pradesh': 'Arunachal Pradesh', 'arunachal': 'Arunachal Pradesh',
        'assam': 'Assam',
        'bihar': 'Bihar',
        'chhattisgarh': 'Chhattisgarh',
        'goa': 'Goa',
        'gujarat': 'Gujarat',
        'haryana': 'Haryana',
        'himachal pradesh': 'Himachal Pradesh', 'himachal': 'Himachal Pradesh',
        'jharkhand': 'Jharkhand',
        'karnataka': 'Karnataka',
        'kerala': 'Kerala',
        'madhya pradesh': 'Madhya Pradesh', 'madhya': 'Madhya Pradesh', 'mp': 'Madhya Pradesh',
        'maharashtra': 'Maharashtra',
        'manipur': 'Manipur',
        'meghalaya': 'Meghalaya',
        'mizoram': 'Mizoram',
        'nagaland': 'Nagaland',
        'odisha': 'Odisha', 'orissa': 'Odisha',
        'punjab': 'Punjab',
        'rajasthan': 'Rajasthan',
        'sikkim': 'Sikkim',
        'tamil nadu': 'Tamil Nadu', 'tamilnadu': 'Tamil Nadu', 'tn': 'Tamil Nadu',
        'telangana': 'Telangana',
        'tripura': 'Tripura',
        'uttar pradesh': 'Uttar Pradesh', 'uttar': 'Uttar Pradesh', 'up': 'Uttar Pradesh',
        'uttarakhand': 'Uttarakhand',
        'west bengal': 'West Bengal', 'bengal': 'West Bengal', 'wb': 'West Bengal',
    }
    
    # Occupation keywords
    OCCUPATIONS = {
        'farmer': ['farmer', 'farming', 'agriculture', 'cultivator', 'kisan'],
        'student': ['student', 'studying', 'college', 'school'],
        'business': ['business', 'businessman', 'businesswoman', 'entrepreneur', 'shop owner'],
        'teacher': ['teacher', 'professor', 'educator'],
        'doctor': ['doctor', 'physician', 'medical'],
        'engineer': ['engineer', 'engineering'],
        'worker': ['worker', 'labour', 'labor', 'labourer'],
        'self-employed': ['self employed', 'self-employed', 'freelancer'],
        'unemployed': ['unemployed', 'jobless', 'no job'],
    }
    
    # Category keywords
    CATEGORIES = {
        'General': ['general', 'gen'],
        'OBC': ['obc', 'other backward class', 'backward class'],
        'SC': ['sc', 'scheduled caste'],
        'ST': ['st', 'scheduled tribe', 'tribal'],
        'EWS': ['ews', 'economically weaker section'],
    }
    
    def parse_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Parse transcript into structured profile
        
        Args:
            transcript: Transcript text
            
        Returns:
            Structured profile dictionary
        """
        transcript_lower = transcript.lower()
        
        profile = {
            'name': self._extract_name(transcript),
            'age': self._extract_age(transcript_lower),
            'income': self._extract_income(transcript_lower),
            'state': self._extract_state(transcript_lower),
            'occupation': self._extract_occupation(transcript_lower),
            'category': self._extract_category(transcript_lower),
            'land_size': self._extract_land_size(transcript_lower),
        }
        
        logger.info(f"Parsed profile: {profile}")
        return profile
    
    def _extract_name(self, transcript: str) -> Optional[str]:
        """Extract name from transcript"""
        # Patterns: "I am [name]", "My name is [name]", "This is [name]"
        patterns = [
            r'(?:my name is|i am|this is|i\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:here|speaking)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, transcript)
            if match:
                name = match.group(1).strip()
                # Validate name (2-50 characters, letters and spaces only)
                if 2 <= len(name) <= 50 and re.match(r'^[A-Za-z\s]+$', name):
                    return name
        
        return None
    
    def _extract_age(self, transcript: str) -> Optional[int]:
        """Extract age from transcript"""
        # Patterns: "52 year old", "age is 52", "I am 52"
        patterns = [
            r'(\d{1,3})\s*(?:year|yr)s?\s*old',
            r'age\s*(?:is|:)?\s*(\d{1,3})',
            r'i\s*(?:am|\'m)\s*(\d{1,3})\s*(?:year|yr)?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, transcript)
            if match:
                age = int(match.group(1))
                # Validate age (0-150)
                if 0 <= age <= 150:
                    return age
        
        return None
    
    def _extract_income(self, transcript: str) -> Optional[int]:
        """Extract income from transcript"""
        # Patterns: "3 lakh", "300000", "3 lakhs", "income is 3 lakh"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:lakh|lac)s?',  # Lakhs
            r'(\d+(?:\.\d+)?)\s*(?:crore|cr)s?',  # Crores
            r'income\s*(?:is|:)?\s*(?:rs\.?|₹)?\s*(\d+)',  # Direct income
            r'(?:earn|earning|make|making)\s*(?:rs\.?|₹)?\s*(\d+)',  # Earning
        ]
        
        for pattern in patterns:
            match = re.search(pattern, transcript)
            if match:
                value = float(match.group(1))
                
                # Convert lakhs/crores to actual number
                if 'lakh' in pattern or 'lac' in pattern:
                    return int(value * 100000)
                elif 'crore' in pattern or 'cr' in pattern:
                    return int(value * 10000000)
                else:
                    return int(value)
        
        return None
    
    def _extract_state(self, transcript: str) -> Optional[str]:
        """Extract state from transcript"""
        # Check for state names in transcript
        for state_key, state_name in self.STATES.items():
            if state_key in transcript:
                return state_name
        
        return None
    
    def _extract_occupation(self, transcript: str) -> Optional[str]:
        """Extract occupation from transcript"""
        # Check for occupation keywords
        for occupation, keywords in self.OCCUPATIONS.items():
            for keyword in keywords:
                if keyword in transcript:
                    return occupation
        
        return None
    
    def _extract_category(self, transcript: str) -> Optional[str]:
        """Extract category from transcript"""
        # Check for category keywords
        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                if keyword in transcript:
                    return category
        
        return None
    
    def _extract_land_size(self, transcript: str) -> Optional[float]:
        """Extract land size from transcript"""
        # Patterns: "2 hectares", "2 acres", "land is 2 hectares"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:hectare|hectares|ha)',
            r'(\d+(?:\.\d+)?)\s*(?:acre|acres)',
            r'land\s*(?:is|:)?\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, transcript)
            if match:
                value = float(match.group(1))
                
                # Convert acres to hectares if needed
                if 'acre' in pattern:
                    return round(value * 0.404686, 2)
                else:
                    return value
        
        return None
    
    def validate_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean profile data
        
        Args:
            profile: Parsed profile
            
        Returns:
            Validated profile with only non-null values
        """
        # Remove None values
        validated = {k: v for k, v in profile.items() if v is not None}
        
        # Ensure required fields have defaults if missing
        if 'age' not in validated:
            validated['age'] = 0
        if 'income' not in validated:
            validated['income'] = 0
        if 'land_size' not in validated:
            validated['land_size'] = 0
        
        return validated
