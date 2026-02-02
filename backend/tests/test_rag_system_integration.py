"""Integration tests for RAG system enhancement of recommendations"""
import pytest
from datetime import datetime, timedelta
from app.models import (
    HospitalRecord, Recommendation, CrisisLesson, HospitalContext
)
from app.services.rag_system import rag_system
from app.services.prediction_engine import PredictionEngine


class TestRAGSystemIntegration:
    """Integration tests for RAG system"""
    
    def test_rag_enhancement_includes_historical_context(self):
        """
        Test that recommendations include historical context when available
        Requirements: 5.5
        """
        # Create sample historical crisis lessons
        crisis1 = CrisisLesson(
            crisis_id="crisis_001",
            date=datetime.now() - timedelta(days=90),
            crisis_description="High bed occupancy with staff shortage during flu season. Bed stress at 88%, staff risk at 82%.",
            bed_stress=88.0,
            staff_risk=82.0,
            actions_taken=[
                "Called in additional nursing staff",
                "Activated surge capacity protocol",
                "Expedited discharge planning"
            ],
            outcome="Successfully managed crisis. Bed stress reduced to 75% within 48 hours.",
            lessons_learned="Early activation of surge protocols and staff augmentation prevented complete overload. Discharge planning was key to freeing capacity."
        )
        
        crisis2 = CrisisLesson(
            crisis_id="crisis_002",
            date=datetime.now() - timedelta(days=120),
            crisis_description="Moderate bed stress with critical staff shortage. Bed stress at 75%, staff risk at 90%.",
            bed_stress=75.0,
            staff_risk=90.0,
            actions_taken=[
                "Emergency staff augmentation",
                "Implemented real-time capacity dashboard",
                "Coordinated with external facilities"
            ],
            outcome="Crisis resolved within 72 hours. Staff risk reduced to 60%.",
            lessons_learned="Real-time monitoring enabled faster decision-making. External coordination helped distribute patient load."
        )
        
        # Create base recommendations (without historical context)
        base_recommendations = [
            Recommendation(
                title="Emergency Staff Augmentation",
                description="Call in additional nursing staff immediately",
                rationale="High staff risk requires immediate action to prevent overload",
                cost_estimate=12000.0,
                impact_score=90.0,
                priority=1,
                implementation_time="4 hours"
            ),
            Recommendation(
                title="Activate Surge Capacity",
                description="Open additional beds in overflow areas",
                rationale="High bed stress requires capacity expansion",
                cost_estimate=8000.0,
                impact_score=85.0,
                priority=2,
                implementation_time="6 hours"
            ),
            Recommendation(
                title="Enhance Discharge Planning",
                description="Expedite discharge planning for stable patients",
                rationale="Free up existing beds to reduce stress",
                cost_estimate=5000.0,
                impact_score=70.0,
                priority=3,
                implementation_time="2 days"
            )
        ]
        
        # Enhance recommendations with historical lessons
        enhanced_recommendations = rag_system.enhance_recommendations(
            base_recommendations,
            [crisis1, crisis2]
        )
        
        # Verify that recommendations were enhanced
        assert len(enhanced_recommendations) == 3, "Should return exactly 3 recommendations"
        
        # Check that at least one recommendation has enhanced rationale with historical context
        has_historical_context = False
        for rec in enhanced_recommendations:
            if "Historical Context:" in rec.rationale or "Similar action taken" in rec.rationale:
                has_historical_context = True
                break
        
        assert has_historical_context, "At least one recommendation should include historical context"
        
        # Verify that enhanced recommendations maintain original structure
        for rec in enhanced_recommendations:
            assert rec.title, "Title should not be empty"
            assert rec.description, "Description should not be empty"
            assert rec.rationale, "Rationale should not be empty"
            assert rec.cost_estimate > 0, "Cost estimate should be positive"
            assert 0 <= rec.impact_score <= 100, "Impact score should be 0-100"
            assert rec.priority in [1, 2, 3], "Priority should be 1, 2, or 3"
            assert rec.implementation_time, "Implementation time should not be empty"
    
    def test_rag_enhancement_without_historical_data(self):
        """
        Test that recommendations work correctly when no historical data is available
        Requirements: 5.5
        """
        # Create base recommendations
        base_recommendations = [
            Recommendation(
                title="Staff Optimization",
                description="Optimize staff scheduling",
                rationale="Improve efficiency",
                cost_estimate=5000.0,
                impact_score=65.0,
                priority=1,
                implementation_time="24 hours"
            ),
            Recommendation(
                title="Capacity Planning",
                description="Review capacity allocation",
                rationale="Prevent future issues",
                cost_estimate=3000.0,
                impact_score=55.0,
                priority=2,
                implementation_time="1 week"
            ),
            Recommendation(
                title="Process Improvement",
                description="Streamline admission process",
                rationale="Reduce bottlenecks",
                cost_estimate=4000.0,
                impact_score=60.0,
                priority=3,
                implementation_time="2 weeks"
            )
        ]
        
        # Enhance with empty historical lessons
        enhanced_recommendations = rag_system.enhance_recommendations(
            base_recommendations,
            []
        )
        
        # Should return original recommendations unchanged
        assert len(enhanced_recommendations) == 3
        assert enhanced_recommendations[0].title == base_recommendations[0].title
        assert enhanced_recommendations[0].rationale == base_recommendations[0].rationale
    
    def test_retrieve_similar_crises(self):
        """
        Test that similar crises can be retrieved based on current context
        Requirements: 5.5
        """
        # Create current hospital context
        context = HospitalContext(
            current_bed_stress=85.0,
            current_staff_risk=78.0,
            recent_trends="Increasing bed occupancy",
            predicted_admissions=250,
            current_staff=35
        )
        
        # Retrieve similar crises (may be empty if no data in BigQuery)
        similar_crises = rag_system.retrieve_similar_crises(context, top_k=5)
        
        # Should return a list (may be empty)
        assert isinstance(similar_crises, list)
        
        # If crises are returned, verify structure
        for crisis in similar_crises:
            assert isinstance(crisis, CrisisLesson)
            assert crisis.crisis_id
            assert isinstance(crisis.date, datetime)
            assert crisis.crisis_description
            assert 0 <= crisis.bed_stress <= 100
            assert 0 <= crisis.staff_risk <= 100
            assert isinstance(crisis.actions_taken, list)
            assert crisis.outcome
            assert crisis.lessons_learned
            # Similarity score should be set during retrieval
            if crisis.similarity_score is not None:
                assert 0 <= crisis.similarity_score <= 1
    
    def test_generate_embeddings(self):
        """
        Test that embeddings can be generated for text
        Requirements: 5.5
        """
        text = "Hospital facing high bed occupancy and staff shortage"
        
        embedding = rag_system.generate_embeddings(text)
        
        # Should return a numpy array
        assert embedding is not None
        assert len(embedding) == rag_system.embedding_dimension
        
        # Embeddings should be normalized (unit length or close to it)
        import numpy as np
        norm = np.linalg.norm(embedding)
        assert 0.5 <= norm <= 1.5, "Embedding should be approximately normalized"
    
    def test_embeddings_consistency(self):
        """
        Test that same text produces same embeddings (deterministic)
        Requirements: 5.5
        """
        text = "Critical staff shortage with moderate bed stress"
        
        embedding1 = rag_system.generate_embeddings(text)
        embedding2 = rag_system.generate_embeddings(text)
        
        # Should produce identical embeddings for same text
        import numpy as np
        assert np.allclose(embedding1, embedding2), "Same text should produce same embeddings"
    
    def test_prediction_engine_uses_rag(self):
        """
        Test that PredictionEngine integrates with RAG system
        Requirements: 5.5
        """
        engine = PredictionEngine()
        
        # Create sample historical data
        historical_data = []
        base_date = datetime.now() - timedelta(days=30)
        for i in range(30):
            record = HospitalRecord(
                date=base_date + timedelta(days=i),
                admissions=100 + (i % 10),
                beds_occupied=200 + (i % 20),
                staff_on_duty=30 + (i % 5),
                overload_flag=(i % 10 == 0)
            )
            historical_data.append(record)
        
        # Generate recommendations (should use RAG internally)
        recommendations = engine.generate_recommendations(
            bed_stress=85.0,
            staff_risk=75.0,
            historical_context=historical_data
        )
        
        # Should return exactly 3 recommendations
        assert len(recommendations) == 3
        
        # Verify recommendation structure
        for rec in recommendations:
            assert isinstance(rec, Recommendation)
            assert rec.validate(), "Recommendation should be valid"
            assert rec.title
            assert rec.description
            assert rec.rationale
            assert rec.cost_estimate >= 0
            assert 0 <= rec.impact_score <= 100
            assert rec.priority in [1, 2, 3]
    
    def test_crisis_lesson_validation(self):
        """
        Test that CrisisLesson model validates correctly
        Requirements: 5.5
        """
        # Valid crisis lesson
        valid_crisis = CrisisLesson(
            crisis_id="test_001",
            date=datetime.now(),
            crisis_description="Test crisis",
            bed_stress=85.0,
            staff_risk=75.0,
            actions_taken=["Action 1", "Action 2"],
            outcome="Positive outcome",
            lessons_learned="Important lessons",
            similarity_score=0.85
        )
        
        assert valid_crisis.validate() is True
        
        # Invalid crisis lesson (bed_stress out of range)
        invalid_crisis = CrisisLesson(
            crisis_id="test_002",
            date=datetime.now(),
            crisis_description="Test crisis",
            bed_stress=150.0,  # Invalid: > 100
            staff_risk=75.0,
            actions_taken=["Action 1"],
            outcome="Outcome",
            lessons_learned="Lessons"
        )
        
        assert invalid_crisis.validate() is False
    
    def test_hospital_context_validation(self):
        """
        Test that HospitalContext model validates correctly
        Requirements: 5.5
        """
        # Valid context
        valid_context = HospitalContext(
            current_bed_stress=85.0,
            current_staff_risk=75.0,
            recent_trends="Increasing",
            predicted_admissions=200,
            current_staff=35
        )
        
        assert valid_context.validate() is True
        
        # Invalid context (negative staff)
        invalid_context = HospitalContext(
            current_bed_stress=85.0,
            current_staff_risk=75.0,
            recent_trends="Increasing",
            predicted_admissions=200,
            current_staff=-5  # Invalid: negative
        )
        
        assert invalid_context.validate() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
