import requests
import os
from typing import Dict, List
import asyncio
import aiohttp
import re
from textstat import flesch_kincaid_grade

class AIService:
    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        
        # Model endpoints
        self.summarization_model = f"{self.hf_api_url}/facebook/bart-large-cnn"
        self.classification_model = f"{self.hf_api_url}/martin-ha/toxic-comment-model"
        
        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
    
    async def summarize_text(self, text: str, max_length: int = 150) -> str:
        """Generate article summary using Hugging Face API"""
        if not text or len(text.strip()) < 100:
            return text[:200] + "..." if len(text) > 200 else text
        
        try:
            # Truncate text to fit model limits
            truncated_text = text[:1000]
            
            payload = {
                "inputs": truncated_text,
                "parameters": {
                    "max_length": max_length,
                    "min_length": 50,
                    "do_sample": False
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.summarization_model,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list) and len(result) > 0:
                            return result[0].get('summary_text', '')
                    else:
                        print(f"Summarization API error: {response.status}")
                        return await self._fallback_summarize(text, max_length)
                        
        except Exception as e:
            print(f"Error in summarization: {e}")
            return await self._fallback_summarize(text, max_length)
    
    async def _fallback_summarize(self, text: str, max_length: int) -> str:
        """Fallback summarization using simple extraction"""
        try:
            # Simple extractive summarization
            sentences = text.split('.')
            # Take first 3 sentences
            summary_sentences = sentences[:3]
            summary = '. '.join(summary_sentences).strip()
            
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            return summary if summary else text[:200] + "..."
            
        except Exception as e:
            print(f"Fallback summarization error: {e}")
            return text[:200] + "..."
    
    async def detect_fake_news(self, title: str, content: str) -> Dict:
        """Detect fake news using content analysis and heuristics"""
        try:
            # Combine title and content
            text_to_analyze = f"{title}. {content[:500]}"
            
            # Use multiple approaches for better accuracy
            credibility_score = await self._analyze_credibility(text_to_analyze)
            
            return {
                "score": credibility_score,
                "confidence": 0.75  # Moderate confidence for heuristic approach
            }
            
        except Exception as e:
            print(f"Error in fake news detection: {e}")
            return {"score": 0.6, "confidence": 0.3}
    
    async def _analyze_credibility(self, text: str) -> float:
        """Analyze text credibility using multiple factors"""
        score = 0.7  # Base score
        
        # Factor 1: Suspicious language patterns
        suspicious_words = [
            'shocking', 'unbelievable', 'secret', 'they dont want you to know',
            'miracle', 'conspiracy', 'breaking', 'exclusive', 'viral',
            'you wont believe', 'doctors hate', 'one weird trick'
        ]
        
        text_lower = text.lower()
        suspicious_count = sum(1 for word in suspicious_words if word in text_lower)
        score -= suspicious_count * 0.05
        
        # Factor 2: ALL CAPS usage (indicates sensationalism)
        caps_words = len([word for word in text.split() if word.isupper() and len(word) > 2])
        caps_ratio = caps_words / max(len(text.split()), 1)
        score -= caps_ratio * 0.3
        
        # Factor 3: Excessive punctuation
        exclamation_count = text.count('!')
        question_count = text.count('?')
        excessive_punct = (exclamation_count + question_count) / max(len(text), 1)
        score -= excessive_punct * 20
        
        # Factor 4: Reading level (very simple = potentially misleading)
        try:
            reading_level = flesch_kincaid_grade(text)
            if reading_level < 6:  # Very simple text
                score -= 0.1
            elif reading_level > 16:  # Very complex text
                score -= 0.05
        except:
            pass
        
        # Factor 5: Emotional language detection
        emotional_words = [
            'outraged', 'furious', 'devastating', 'alarming', 'terrifying',
            'amazing', 'incredible', 'fantastic', 'horrific', 'scandalous'
        ]
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        score -= emotional_count * 0.03
        
        # Factor 6: Source credibility indicators
        credible_indicators = [
            'according to', 'research shows', 'study found', 'experts say',
            'data indicates', 'survey revealed', 'analysis suggests'
        ]
        credible_count = sum(1 for phrase in credible_indicators if phrase in text_lower)
        score += credible_count * 0.05
        
        # Ensure score is within bounds
        return max(0.1, min(1.0, score))
    
    async def classify_content_toxicity(self, text: str) -> Dict:
        """Classify content toxicity (bonus feature)"""
        try:
            payload = {"inputs": text[:500]}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.classification_model,
                    headers=self.headers,
                    json=payload,
                    timeout=20
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list) and len(result) > 0:
                            return {
                                "is_toxic": result[0].get('label') == 'TOXIC',
                                "confidence": result[0].get('score', 0.5)
                            }
                    
            return {"is_toxic": False, "confidence": 0.5}
            
        except Exception as e:
            print(f"Toxicity classification error: {e}")
            return {"is_toxic": False, "confidence": 0.1}