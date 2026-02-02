# Implementation Plan: Hospital Stress Early Warning System

## Overview

This implementation plan breaks down the Hospital Stress Early Warning System into discrete coding tasks. The system will be built incrementally, starting with core data infrastructure, then prediction capabilities, API endpoints, frontend dashboard, and finally alerts and advanced features. Each task builds on previous work to ensure continuous integration and validation.

## Tasks

- [x] 1. Set up project structure and infrastructure
  - Create backend FastAPI project with proper directory structure (app/, tests/, config/)
  - Create Next.js 15 frontend project with App Router
  - Set up BigQuery dataset and tables (logs, predictions, alerts)
  - Configure Google Cloud authentication and Vertex AI access
  - Set up Redis for caching
  - Create Docker configuration for backend
  - Set up environment variable management
  - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [x] 2. Implement data models and validation
  - [x] 2.1 Create core data model classes in Python
    - Implement HospitalRecord, BedForecast, DailyPrediction, StaffRiskScore, Recommendation, AlertData, ScenarioRequest, ScenarioResult, ValidationResult, DashboardData dataclasses
    - Add validation methods to each model
    - _Requirements: 1.1, 1.2_

  - [x] 2.2 Write property test for data model validation
    - **Property 1: CSV Upload Round Trip**
    - **Validates: Requirements 1.1**

  - [x] 2.3 Write unit tests for edge cases
    - Test boundary values for admissions, beds, staff counts
    - Test invalid data type handling
    - _Requirements: 1.2_

- [x] 3. Implement CSV upload handler
  - [x] 3.1 Create UploadHandler class with CSV parsing
    - Implement validate_csv() method with schema checking
    - Implement parse_csv() method using pandas
    - Implement check_file_size() method (50MB limit)
    - Implement store_records() method with BigQuery client
    - Handle duplicate date entries with most-recent-wins logic
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 3.2 Write property test for invalid CSV rejection
    - **Property 2: Invalid CSV Rejection**
    - **Validates: Requirements 1.2**

  - [x] 3.3 Write property test for duplicate handling
    - **Property 3: Duplicate Date Deduplication**
    - **Validates: Requirements 1.4**

  - [x] 3.4 Write unit tests for file size validation
    - Test files at 49MB, 50MB, 51MB boundaries
    - _Requirements: 1.3_

- [x] 4. Implement synthetic data generation
  - [x] 4.1 Create synthetic data generator
    - Generate 6 months of realistic hospital data
    - Include weekday/weekend patterns
    - Include seasonal variations
    - Include random overload events
    - _Requirements: 1.6_

  - [x] 4.2 Write unit test for synthetic data generation
    - Verify 6 months of data is generated when no data exists
    - _Requirements: 1.6_

- [x] 5. Checkpoint - Ensure data layer tests pass
  - Run all data layer tests
  - Verify BigQuery connection and data storage
  - Ask the user if questions arise

- [-] 6. Implement prediction engine core
  - [x] 6.1 Create PredictionEngine class with Vertex AI integration
    - Set up Vertex AI client with Gemini model
    - Implement forecast_bed_demand() method with 7-day forecasting
    - Implement calculate_confidence() method based on data quality
    - Handle missing data with forward-fill interpolation
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 12.1_

  - [ ] 6.2 Write property test for forecast length consistency
    - **Property 4: Forecast Length Consistency**
    - **Validates: Requirements 2.1**

  - [ ] 6.3 Write property test for missing data handling
    - **Property 5: Graceful Handling of Missing Data**
    - **Validates: Requirements 2.2**

  - [ ] 6.4 Write property test for prediction structure
    - **Property 6: Prediction Structure Completeness**
    - **Validates: Requirements 2.3**

  - [ ] 6.5 Write property test for bed stress calculation
    - **Property 7: Bed Stress Calculation Accuracy**
    - **Validates: Requirements 2.4**

  - [ ] 6.6 Write property test for high risk flagging
    - **Property 8: High Risk Flagging Threshold**
    - **Validates: Requirements 2.5**

  - [ ] 6.7 Write property test for interpolation
    - **Property 26: Forward-Fill Interpolation**
    - **Validates: Requirements 12.1**

- [-] 7. Implement staff risk assessment
  - [x] 7.1 Add calculate_staff_risk() method to PredictionEngine
    - Calculate risk score (0-100) based on admissions and staffing
    - Learn from historical overload patterns
    - Include confidence score calculation
    - _Requirements: 3.1, 3.3, 3.5_

  - [x] 7.2 Write property test for staff risk score range
    - **Property 9: Staff Risk Score Range**
    - **Validates: Requirements 3.1**

  - [x] 7.3 Write property test for critical risk classification
    - **Property 10: Critical Risk Classification**
    - **Validates: Requirements 3.3**

  - [x] 7.4 Write property test for risk score structure
    - **Property 11: Risk Score Structure Completeness**
    - **Validates: Requirements 3.5**

- [-] 8. Implement recommendation generation
  - [x] 8.1 Add generate_recommendations() method to PredictionEngine
    - Use chain-of-thought prompting with Vertex AI
    - Generate exactly 3 prioritized recommendations
    - Include cost estimates and impact scores
    - Rank by impact-to-cost ratio
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 8.2 Write property test for recommendation count
    - **Property 13: Recommendation Count Consistency**
    - **Validates: Requirements 5.1**

  - [ ] 8.3 Write property test for recommendation structure
    - **Property 14: Recommendation Structure Completeness**
    - **Validates: Requirements 5.2, 5.3**

  - [ ] 8.4 Write property test for recommendation ordering
    - **Property 15: Recommendation Priority Ordering**
    - **Validates: Requirements 5.4**

- [x] 9. Implement RAG system for historical lessons
  - [x] 9.1 Create RAGSystem class
    - Implement retrieve_similar_crises() using vector embeddings
    - Implement generate_embeddings() with Vertex AI
    - Implement enhance_recommendations() to incorporate lessons
    - Store crisis history in BigQuery
    - _Requirements: 5.5_

  - [x] 9.2 Write integration test for RAG enhancement
    - Test that recommendations include historical context when available
    - _Requirements: 5.5_

- [x] 10. Implement what-if scenario simulator
  - [x] 10.1 Add simulate_scenario() method to PredictionEngine
    - Accept sick_rate (0-50%) and admission_surge (-30% to +100%) parameters
    - Recalculate bed demand and staff risk with adjusted parameters
    - Return baseline vs scenario comparison
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 10.2 Write property test for scenario recalculation
    - **Property 12: Scenario Recalculation Responsiveness**
    - **Validates: Requirements 4.1**

  - [x] 10.3 Write unit tests for parameter boundaries
    - Test sick_rate at 0%, 50%, and out-of-range values
    - Test admission_surge at -30%, +100%, and out-of-range values
    - _Requirements: 4.2, 4.3_

- [-] 11. Implement prediction caching
  - [ ] 11.1 Add Redis caching layer to PredictionEngine
    - Cache predictions with 15-minute TTL
    - Cache dashboard data with 30-second TTL
    - Cache staff risk with 10-minute TTL
    - Implement cache key generation based on input parameters
    - Invalidate cache on new data uploads
    - _Requirements: 13.5_

  - [ ] 11.2 Write property test for prediction caching
    - **Property 28: Prediction Caching**
    - **Validates: Requirements 13.5**

- [ ] 12. Checkpoint - Ensure prediction engine tests pass
  - Run all prediction engine tests
  - Verify Vertex AI integration works
  - Verify caching behavior
  - Ask the user if questions arise

- [x] 13. Implement alert service
  - [x] 13.1 Create AlertService class
    - Implement check_thresholds() method
    - Implement send_email_alert() with SendGrid or similar
    - Implement send_slack_alert() with webhook integration
    - Implement format_alert_message() with hospital letterhead template
    - Add retry logic for failed deliveries (3 attempts)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 13.2 Write property test for threshold-based alerting
    - **Property 16: Threshold-Based Alert Triggering**
    - **Validates: Requirements 6.1, 6.2**

  - [x] 13.3 Write property test for conditional Slack notification
    - **Property 17: Conditional Slack Notification**
    - **Validates: Requirements 6.3**

  - [x] 13.4 Write property test for alert template application
    - **Property 18: Alert Template Application**
    - **Validates: Requirements 6.4**

  - [x] 13.5 Write property test for alert content completeness
    - **Property 19: Alert Content Completeness**
    - **Validates: Requirements 6.5**

  - [x] 13.6 Write unit tests for alert retry logic
    - Test email delivery failures and retries
    - Test Slack webhook failures
    - _Requirements: 6.1, 6.2, 6.3_

- [ ] 14. Implement FastAPI endpoints
  - [ ] 14.1 Create API Gateway with FastAPI
    - Implement POST /upload-logs endpoint
    - Implement POST /predict-beds endpoint
    - Implement POST /staff-risk endpoint
    - Implement GET /dashboard-data endpoint
    - Implement POST /recommendations endpoint
    - Implement POST /send-alert endpoint
    - Implement POST /simulate-scenario endpoint
    - Add request validation with Pydantic models
    - Add error handling and proper HTTP status codes
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8_

  - [ ] 14.2 Write property test for API error responses
    - **Property 24: API Error Response Format**
    - **Validates: Requirements 11.7**

  - [ ] 14.3 Write property test for API success responses
    - **Property 25: API Success Response Format**
    - **Validates: Requirements 11.8**

  - [ ] 14.4 Write unit tests for each API endpoint
    - Test /upload-logs with valid and invalid CSV
    - Test /predict-beds with various data scenarios
    - Test /staff-risk with different staffing levels
    - Test /dashboard-data response structure
    - Test /recommendations with high-risk scenarios
    - Test /send-alert with different configurations
    - Test /simulate-scenario with parameter variations
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

- [ ] 15. Implement health check endpoints
  - [ ] 15.1 Add health check endpoints
    - Implement GET /health for liveness probe
    - Implement GET /ready for readiness probe
    - Check BigQuery connectivity
    - Check Vertex AI availability
    - Check Redis connectivity
    - _Requirements: 14.5_

  - [ ] 15.2 Write unit test for health checks
    - Test health endpoint returns 200 when all services available
    - Test ready endpoint returns 503 when services unavailable
    - _Requirements: 14.5_

- [ ] 16. Checkpoint - Ensure backend API tests pass
  - Run all API endpoint tests
  - Test API with Postman or similar tool
  - Verify error handling and status codes
  - Ask the user if questions arise

- [ ] 17. Implement authentication with NextAuth
  - [ ] 17.1 Set up NextAuth with Google OAuth
    - Configure Google OAuth provider
    - Create auth configuration in Next.js
    - Implement session management
    - Add protected route middleware
    - Set 24-hour session timeout
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 17.2 Write unit tests for authentication flows
    - Test unauthenticated access redirects to login
    - Test successful authentication creates session
    - Test session expiration redirects to login
    - Test logout invalidates session
    - _Requirements: 7.1, 7.3, 7.5_

- [ ] 18. Implement frontend dashboard layout
  - [ ] 18.1 Create dashboard page with Shadcn/UI components
    - Create layout with 4 status tiles (Bed Stress, Staff Risk, Alerts, Recommendations)
    - Add 7-day forecast chart using recharts or similar
    - Add trend indicators (up/down arrows)
    - Implement dark mode toggle
    - Add polling mechanism (30-second refresh)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ] 18.2 Write property test for dashboard data structure
    - **Property 20: Dashboard Data Structure**
    - **Validates: Requirements 8.2**

  - [ ] 18.3 Write property test for trend indicator calculation
    - **Property 21: Trend Indicator Calculation**
    - **Validates: Requirements 8.5**

  - [ ] 18.4 Write unit tests for dashboard components
    - Test status tiles render correctly
    - Test chart displays 7 days of data
    - Test trend indicators show correct direction
    - Test dark mode toggle
    - _Requirements: 8.1, 8.5_

- [ ] 19. Implement CSV upload interface
  - [ ] 19.1 Create drag-drop CSV upload component
    - Add file drop zone with visual feedback
    - Validate file type and size on client side
    - Show upload progress
    - Display success/error messages
    - Refresh dashboard after successful upload
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ] 19.2 Write unit tests for upload component
    - Test file validation
    - Test upload success handling
    - Test upload error handling
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 20. Implement what-if simulator interface
  - [ ] 20.1 Create interactive simulator with sliders
    - Add sick_rate slider (0-50%)
    - Add admission_surge slider (-30% to +100%)
    - Display baseline vs scenario comparison side-by-side
    - Update predictions in real-time as sliders move
    - Show impact summary
    - _Requirements: 4.1, 4.2, 4.3, 4.5_

  - [ ] 20.2 Write unit tests for simulator component
    - Test slider value updates
    - Test scenario recalculation triggers
    - Test comparison display
    - _Requirements: 4.1, 4.5_

- [ ] 21. Implement natural language chat interface
  - [ ] 21.1 Create chat component with conversation history
    - Add message input and send button
    - Display conversation history
    - Maintain context across messages
    - Show loading state during AI processing
    - Handle ambiguous queries with clarifying questions
    - _Requirements: 9.1, 9.2, 9.3, 9.5_

  - [ ] 21.2 Write property test for conversation context
    - **Property 22: Conversation Context Preservation**
    - **Validates: Requirements 9.5**

  - [ ] 21.3 Write unit tests for chat component
    - Test message sending
    - Test conversation history display
    - Test loading states
    - _Requirements: 9.1, 9.5_

- [ ] 22. Implement onboarding wizard
  - [ ] 22.1 Create 5-step onboarding wizard
    - Step 1: CSV upload
    - Step 2: Roster connection (placeholder for future integration)
    - Step 3: Threshold configuration
    - Step 4: Test prediction
    - Step 5: Enable alerts
    - Add progress indicator
    - Save progress on each step
    - Allow skip and resume later
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ] 22.2 Write property test for progress persistence
    - **Property 23: Onboarding Progress Persistence**
    - **Validates: Requirements 10.5**

  - [ ] 22.3 Write unit tests for onboarding wizard
    - Test first-time user sees wizard
    - Test wizard completion marks onboarding done
    - Test skip functionality
    - Test progress saving and restoration
    - _Requirements: 10.1, 10.3, 10.4, 10.5_

- [ ] 23. Implement landing page
  - [ ] 23.1 Create public landing page
    - Add hero section with value proposition
    - Add feature highlights
    - Add demo video or screenshots
    - Add call-to-action button (Sign in with Google)
    - Make responsive for mobile
    - _Requirements: 7.1_

  - [ ] 23.2 Write unit tests for landing page
    - Test page renders correctly
    - Test sign-in button redirects to auth
    - _Requirements: 7.1_

- [ ] 24. Checkpoint - Ensure frontend tests pass
  - Run all frontend component tests
  - Test user flows manually in browser
  - Verify responsive design on mobile
  - Ask the user if questions arise

- [ ] 25. Implement confidence score degradation logic
  - [ ] 25.1 Add data quality assessment to PredictionEngine
    - Calculate data completeness percentage
    - Calculate data sparsity metrics
    - Adjust confidence scores based on quality
    - _Requirements: 12.4_

  - [ ] 25.2 Write property test for confidence degradation
    - **Property 27: Confidence Score Degradation**
    - **Validates: Requirements 12.4**

- [ ] 26. Implement data quality warnings
  - [ ] 26.1 Add warning system for insufficient data
    - Display warning when < 30 days of data
    - Display warning when data quality is low
    - Show warnings in dashboard UI
    - _Requirements: 12.2_

  - [ ] 26.2 Write unit test for data quality warnings
    - Test warning appears with < 30 days of data
    - Test warning includes accuracy disclaimer
    - _Requirements: 12.2_

- [ ] 27. Implement fallback to synthetic data
  - [ ] 27.1 Add synthetic data fallback logic
    - Detect when date ranges have no data
    - Generate synthetic data for missing ranges
    - Log fallback usage
    - _Requirements: 12.5_

  - [ ] 27.2 Write unit test for synthetic data fallback
    - Test synthetic data is used when no data exists for date range
    - _Requirements: 12.5_

- [ ] 28. Add comprehensive error handling
  - [ ] 28.1 Implement error handling across all components
    - Add try-catch blocks with specific error types
    - Implement retry logic for transient failures
    - Add user-friendly error messages
    - Log errors with context for debugging
    - _Requirements: 1.2, 1.3, 6.1, 6.2, 6.3_

  - [ ] 28.2 Write unit tests for error scenarios
    - Test file size exceeded error
    - Test invalid CSV schema error
    - Test BigQuery connection failure
    - Test Vertex AI service failure
    - Test email delivery failure
    - Test Slack webhook failure
    - _Requirements: 1.2, 1.3_

- [ ] 29. Set up deployment configurations
  - [ ] 29.1 Configure Vercel deployment for frontend
    - Create vercel.json configuration
    - Set environment variables
    - Configure build settings
    - Set up preview deployments
    - _Requirements: 14.1_

  - [ ] 29.2 Configure Cloud Run deployment for backend
    - Create Dockerfile
    - Set up Cloud Build configuration
    - Configure auto-scaling settings
    - Set environment variables
    - Configure health checks
    - _Requirements: 14.2, 14.5_

  - [ ] 29.3 Write deployment verification tests
    - Test health endpoints after deployment
    - Test API endpoints are accessible
    - Test frontend loads correctly
    - _Requirements: 14.5_

- [ ] 30. Final integration testing
  - [ ] 30.1 Test complete end-to-end flows
    - Test: Sign in → Upload CSV → View predictions → Receive alert
    - Test: Run what-if simulation → Compare scenarios
    - Test: Ask natural language query → Get response
    - Test: Complete onboarding wizard → Access dashboard
    - _Requirements: All_

  - [ ] 30.2 Write integration tests for critical paths
    - Test upload-to-prediction flow
    - Test high-risk-to-alert flow
    - Test scenario simulation flow
    - _Requirements: 1.1, 2.1, 6.1_

- [ ] 31. Final checkpoint - Production readiness
  - Run full test suite (unit + property + integration)
  - Verify all API endpoints work correctly
  - Verify frontend loads and functions properly
  - Test with realistic data volumes
  - Review error handling and logging
  - Ask the user if ready for production deployment

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: data layer → prediction engine → API → frontend
- All property tests should be tagged with: `Feature: hospital-stress-warning, Property {number}: {property_text}`
