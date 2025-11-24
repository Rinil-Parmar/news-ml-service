from transformers import pipeline
import torch

class SummarizationService:
    def __init__(self):
        print("🔄 Loading BART summarization model...")
        try:
            device = 0 if torch.cuda.is_available() else -1
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=device
            )
            print("✅ BART model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def summarize(
        self, 
        text: str, 
        max_length: int = 150, 
        min_length: int = 40
    ) -> dict:
        """
        Summarize text using BART model
        Returns: dict with summary and lengths
        """
        if not text or len(text.strip()) < 50:
            return {
                'summary': text,
                'original_length': len(text.split()),
                'summary_length': len(text.split())
            }
        
        original_length = len(text.split())
        
        # Truncate if too long (BART max: 1024 tokens)
        max_input_words = 1000
        if original_length > max_input_words:
            text = ' '.join(text.split()[:max_input_words])
        
        try:
            result = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True
            )
            
            summary = result[0]['summary_text']
            summary_length = len(summary.split())
            
            return {
                'summary': summary,
                'original_length': original_length,
                'summary_length': summary_length
            }
        
        except Exception as e:
            print(f"❌ Summarization error: {e}")
            # Fallback: return first 3 sentences
            sentences = text.split('.')[:3]
            fallback_summary = '.'.join(sentences) + '.'
            
            return {
                'summary': fallback_summary,
                'original_length': original_length,
                'summary_length': len(fallback_summary.split())
            }

# Global instance
summarization_service = SummarizationService()