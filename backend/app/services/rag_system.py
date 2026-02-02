"""RAG (Retrieval-Augmented Generation) system for historical crisis lessons"""
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
import hashlib

from ..models import CrisisLesson, HospitalContext, Recommendation
from ..db.vertex_ai_client import vertex_ai_client
from ..db.bigquery_client import bigquery_client
from ..config import settings


class RAGSystem:
    """Retrieval-Augmented Generation system for incorporating historical crisis lessons"""
    
    def __init__(self):
        self.vertex_client = vertex_ai_client
        self.bigquery_client = bigquery_client
        self.embedding_dimension = 768  # Standard embedding dimension for text models
    
    def retrieve_similar_crises(
        self,
        current_context: HospitalContext,
        top_k: int = 5
    ) -> List[CrisisLesson]:
        """
        Retrieves similar historical crisis events using vector embeddings
        
        Args:
            current_context: Current hospital situation context
            top_k: Number of similar crises to retrieve (default 5)
            
        Returns:
            List of relevant CrisisLesson objects with similarity scores
        """
        # Generate embedding for current context
        context_description = self._create_context_description(current_context)
        current_embedding = self.generate_embeddings(context_description)
        
        if current_embedding is None:
            print("Failed to generate embeddings for current context")
            return []
        
        # Retrieve all historical crises from BigQuery
        historical_crises = self._get_historical_crises()
        
        if not historical_crises:
            print("No historical crisis data available")
            return []
        
        # Calculate similarity scores for each historical crisis
        crisis_similarities = []
        for crisis in historical_crises:
            # Generate embedding for historical crisis
            crisis_embedding = self.generate_embeddings(crisis.crisis_description)
            
            if crisis_embedding is not None:
                # Calculate cosine similarity
                similarity = self._cosine_similarity(current_embedding, crisis_embedding)
                crisis.similarity_score = similarity
                crisis_similarities.append((similarity, crisis))
        
        # Sort by similarity (descending) and return top_k
        crisis_similarities.sort(key=lambda x: x[0], reverse=True)
        similar_crises = [crisis for _, crisis in crisis_similarities[:top_k]]
        
        return similar_crises
    
    def generate_embeddings(self, text: str) -> Optional[np.ndarray]:
        """
        Generates vector embeddings for text using Vertex AI
        
        Args:
            text: Text to generate embeddings for
            
        Returns:
            Embedding vector as numpy array, or None if generation fails
        """
        if not self.vertex_client.available:
            print("Vertex AI not available for embeddings")
            return self._generate_fallback_embedding(text)
        
        try:
            # Use Vertex AI to generate embeddings
            # Note: This is a simplified implementation
            # In production, you would use the proper Vertex AI embeddings API
            prompt = f"Generate a semantic embedding for the following hospital crisis description:\n\n{text}"
            
            # For now, we'll create a hash-based embedding as a fallback
            # In production, replace this with actual Vertex AI embeddings API call
            return self._generate_fallback_embedding(text)
            
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return self._generate_fallback_embedding(text)
    
    def _generate_fallback_embedding(self, text: str) -> np.ndarray:
        """
        Generate a deterministic embedding based on text hash
        This is a fallback when Vertex AI is unavailable
        """
        # Create a hash of the text
        text_hash = hashlib.sha256(text.encode()).digest()
        
        # Convert hash to numpy array and normalize
        # Use first 768 bytes (or repeat if needed) to match embedding dimension
        hash_bytes = text_hash * (self.embedding_dimension // len(text_hash) + 1)
        hash_bytes = hash_bytes[:self.embedding_dimension]
        
        # Convert to float array and normalize
        embedding = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32)
        embedding = embedding / 255.0  # Normalize to [0, 1]
        
        # Center and normalize to unit length
        embedding = embedding - 0.5
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def enhance_recommendations(
        self,
        base_recommendations: List[Recommendation],
        historical_lessons: List[CrisisLesson]
    ) -> List[Recommendation]:
        """
        Enhances recommendations with historical insights from similar crises
        
        Args:
            base_recommendations: Original recommendations
            historical_lessons: Similar historical crisis lessons
            
        Returns:
            Enhanced recommendation list with historical context incorporated
        """
        if not historical_lessons:
            # No historical lessons available, return base recommendations
            return base_recommendations
        
        # Extract key lessons from historical crises
        lessons_summary = self._summarize_historical_lessons(historical_lessons)
        
        # Enhance each recommendation with relevant historical context
        enhanced_recommendations = []
        for rec in base_recommendations:
            enhanced_rec = self._enhance_single_recommendation(rec, lessons_summary, historical_lessons)
            enhanced_recommendations.append(enhanced_rec)
        
        return enhanced_recommendations
    
    def _create_context_description(self, context: HospitalContext) -> str:
        """Create a text description of the current hospital context"""
        description = f"""
Hospital Crisis Context:
- Bed Stress Level: {context.current_bed_stress:.1f}%
- Staff Risk Level: {context.current_staff_risk:.1f}%
- Recent Trends: {context.recent_trends}
- Predicted Admissions: {context.predicted_admissions}
- Current Staff: {context.current_staff}

This represents a hospital facing capacity and staffing challenges that require immediate attention.
"""
        return description.strip()
    
    def _get_historical_crises(self) -> List[CrisisLesson]:
        """Retrieve historical crisis data from BigQuery"""
        if not self.bigquery_client.available:
            print("BigQuery not available, returning empty crisis history")
            return []
        
        try:
            # Query crisis history table
            sql = f"""
            SELECT 
                crisis_id,
                date,
                crisis_description,
                bed_stress,
                staff_risk,
                actions_taken,
                outcome,
                lessons_learned
            FROM `{self.bigquery_client.get_table_ref('crisis_history')}`
            ORDER BY date DESC
            LIMIT 100
            """
            
            results = self.bigquery_client.query(sql)
            
            crises = []
            for row in results:
                # Parse actions_taken from JSON string if needed
                actions_taken = row.get('actions_taken', [])
                if isinstance(actions_taken, str):
                    try:
                        actions_taken = json.loads(actions_taken)
                    except:
                        actions_taken = [actions_taken]
                
                crisis = CrisisLesson(
                    crisis_id=row['crisis_id'],
                    date=datetime.combine(row['date'], datetime.min.time()) if not isinstance(row['date'], datetime) else row['date'],
                    crisis_description=row['crisis_description'],
                    bed_stress=float(row['bed_stress']),
                    staff_risk=float(row['staff_risk']),
                    actions_taken=actions_taken,
                    outcome=row['outcome'],
                    lessons_learned=row['lessons_learned']
                )
                crises.append(crisis)
            
            return crises
            
        except Exception as e:
            print(f"Error retrieving historical crises: {e}")
            # Return empty list if table doesn't exist yet
            return []
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    def _summarize_historical_lessons(self, lessons: List[CrisisLesson]) -> str:
        """Summarize key lessons from historical crises"""
        if not lessons:
            return "No historical lessons available"
        
        summary_lines = []
        summary_lines.append("Historical Crisis Lessons:")
        summary_lines.append("")
        
        for i, lesson in enumerate(lessons[:3], 1):  # Top 3 most similar
            similarity_str = f"{lesson.similarity_score:.2f}" if lesson.similarity_score is not None else "N/A"
            summary_lines.append(f"{i}. Crisis from {lesson.date.strftime('%Y-%m-%d')} (Similarity: {similarity_str}):")
            summary_lines.append(f"   Situation: {lesson.crisis_description[:150]}...")
            summary_lines.append(f"   Actions Taken: {', '.join(lesson.actions_taken[:3])}")
            summary_lines.append(f"   Outcome: {lesson.outcome[:100]}...")
            summary_lines.append(f"   Lesson: {lesson.lessons_learned[:150]}...")
            summary_lines.append("")
        
        return "\n".join(summary_lines)
    
    def _enhance_single_recommendation(
        self,
        recommendation: Recommendation,
        lessons_summary: str,
        historical_lessons: List[CrisisLesson]
    ) -> Recommendation:
        """Enhance a single recommendation with historical context"""
        
        # Find relevant historical actions that match this recommendation
        relevant_actions = []
        for lesson in historical_lessons[:3]:  # Top 3 most similar
            for action in lesson.actions_taken:
                # Simple keyword matching to find relevant actions
                if any(keyword in action.lower() for keyword in self._extract_keywords(recommendation.title)):
                    relevant_actions.append((lesson, action))
        
        # Enhance the rationale with historical context
        enhanced_rationale = recommendation.rationale
        
        if relevant_actions:
            enhanced_rationale += "\n\nHistorical Context: "
            for lesson, action in relevant_actions[:2]:  # Include top 2 relevant actions
                enhanced_rationale += f"Similar action taken on {lesson.date.strftime('%Y-%m-%d')}: {action}. "
                enhanced_rationale += f"Outcome: {lesson.outcome[:80]}. "
        
        # Create enhanced recommendation
        enhanced_rec = Recommendation(
            title=recommendation.title,
            description=recommendation.description,
            rationale=enhanced_rationale,
            cost_estimate=recommendation.cost_estimate,
            impact_score=recommendation.impact_score,
            priority=recommendation.priority,
            implementation_time=recommendation.implementation_time
        )
        
        return enhanced_rec
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key words from text for matching"""
        # Simple keyword extraction - remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = text.lower().split()
        keywords = [w for w in words if w not in common_words and len(w) > 3]
        return keywords
    
    def store_crisis_lesson(self, crisis: CrisisLesson) -> bool:
        """
        Store a new crisis lesson in BigQuery for future retrieval
        
        Args:
            crisis: CrisisLesson object to store
            
        Returns:
            True if successful, False otherwise
        """
        if not self.bigquery_client.available:
            print("BigQuery not available, cannot store crisis lesson")
            return False
        
        try:
            # Prepare row data
            row = {
                'crisis_id': crisis.crisis_id,
                'date': crisis.date.strftime('%Y-%m-%d'),
                'crisis_description': crisis.crisis_description,
                'bed_stress': crisis.bed_stress,
                'staff_risk': crisis.staff_risk,
                'actions_taken': json.dumps(crisis.actions_taken),
                'outcome': crisis.outcome,
                'lessons_learned': crisis.lessons_learned,
                'created_at': datetime.now().isoformat()
            }
            
            # Insert into BigQuery
            success = self.bigquery_client.insert_rows('crisis_history', [row])
            
            if success:
                print(f"Successfully stored crisis lesson: {crisis.crisis_id}")
            else:
                print(f"Failed to store crisis lesson: {crisis.crisis_id}")
            
            return success
            
        except Exception as e:
            print(f"Error storing crisis lesson: {e}")
            return False


# Singleton instance
rag_system = RAGSystem()
