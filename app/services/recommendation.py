from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import numpy as np

class RecommendationService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
        print("✅ Recommendation service initialized")
    
    async def recommend_articles(
        self,
        preferences: List[str],
        articles: List[Dict],
        user_events: List[Dict],
        top_k: int = 20
    ) -> List[Dict]:
        """
        Recommend articles based on:
        1. User preferences (TF-IDF similarity)
        2. User interactions (like = 1.5x boost, read = 1.2x boost)
        3. Hidden articles are filtered out
        """
        
        if not articles:
            return []
        
        # Parse user events
        hidden_ids = set()
        liked_ids = set()
        read_ids = set()
        
        for event in user_events:
            article_id = event.get('articleId')
            action = event.get('action', '').lower()
            
            if action == 'hide':
                hidden_ids.add(article_id)
            elif action == 'like':
                liked_ids.add(article_id)
            elif action == 'read':
                read_ids.add(article_id)
        
        # Filter out hidden articles
        filtered_articles = [
            article for article in articles 
            if article['id'] not in hidden_ids
        ]
        
        if not filtered_articles:
            return []
        
        # Build corpus from article titles + descriptions
        corpus = []
        for article in filtered_articles:
            title = article.get('title', '')
            desc = article.get('description', '')
            text = f"{title} {desc}".strip()
            corpus.append(text if text else "unknown")
        
        # User query from preferences
        user_query = ' '.join(preferences)
        
        try:
            # Compute TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            query_vector = self.vectorizer.transform([user_query])
            
            # Cosine similarity
            similarities = cosine_similarity(query_vector, tfidf_matrix)[0]
            
            # Apply boosts based on user interactions
            for idx, article in enumerate(filtered_articles):
                article_id = article['id']
                
                if article_id in liked_ids:
                    similarities[idx] *= 1.5  # 50% boost for liked
                elif article_id in read_ids:
                    similarities[idx] *= 1.2  # 20% boost for read
            
            # Get top K indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Build recommendations with scores
            recommendations = []
            for idx in top_indices:
                article = filtered_articles[idx].copy()
                article['score'] = float(similarities[idx])
                recommendations.append(article)
            
            return recommendations
        
        except Exception as e:
            print(f"❌ Recommendation error: {e}")
            # Fallback: return recent articles
            for i, article in enumerate(filtered_articles[:top_k]):
                article['score'] = 0.5
            return filtered_articles[:top_k]

# Global instance
recommendation_service = RecommendationService()