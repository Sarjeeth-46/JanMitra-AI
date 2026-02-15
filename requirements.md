# Requirements Document: JanMitra AI Platform

## Introduction

The JanMitra AI Platform is a government scheme eligibility platform designed to bridge the gap between rural citizens and 1000+ fragmented government welfare schemes across India. The platform addresses critical challenges including complex eligibility criteria, low digital literacy, limited scheme awareness, and high unclaimed benefit leakage (estimated at 30-40% of allocated subsidies). With 65% of India's population residing in rural areas, the platform aims to democratize access to government benefits through intelligent automation, voice-first interfaces, and document intelligence.

## Problem Statement

India operates over 1000 government welfare schemes across central, state, and district levels, yet rural citizens face significant barriers in accessing these benefits:

- **Fragmentation**: Schemes are scattered across multiple departments with inconsistent application processes
- **Complex Eligibility**: Multi-dimensional criteria (income, caste, age, occupation, land ownership) create confusion
- **Low Awareness**: 60-70% of eligible rural households are unaware of applicable schemes
- **Digital Literacy Barrier**: Only 38% rural digital literacy limits online access
- **High Leakage**: 30-40% of allocated subsidies remain unclaimed due to information asymmetry
- **Document Burden**: Manual form-filling and document submission deter applications

**Quantified Impact**:
- Target Population: 900M+ rural citizens (65% of India's population)
- Unclaimed Subsidies: ₹2-3 lakh crore annually (30-40% leakage rate)
- Eligible Non-Beneficiaries: 200M+ households unaware of applicable schemes

## Glossary

- **JanMitra_Platform**: The complete AI-powered government scheme eligibility system
- **Policy_Ingestion_Service**: Component that processes scheme PDF documents into structured rules
- **Eligibility_Engine**: Core reasoning system that matches user profiles against scheme criteria
- **Voice_Interface**: Multilingual speech-to-text and text-to-speech interaction layer
- **Document_Intelligence_Service**: Component that extracts structured data from identity and income documents
- **Recommendation_Engine**: System that ranks and prioritizes schemes for users
- **Rule_Schema**: Standardized JSON format for representing scheme eligibility criteria
- **User_Profile**: Structured representation of citizen demographics, income, and documents
- **Scheme**: Government welfare program with defined eligibility criteria and benefits
- **CSC_Operator**: Common Service Center operator assisting rural citizens
- **PII**: Personally Identifiable Information requiring secure handling
- **Match_Score**: Numerical relevance score (0-100) indicating scheme applicability

## Requirements

### Requirement 1: Policy Document Ingestion

**User Story:** As a government administrator, I want to upload scheme policy documents, so that eligibility rules are automatically extracted and made available for matching.

#### Acceptance Criteria

1. WHEN a PDF policy document is uploaded, THE Policy_Ingestion_Service SHALL extract text content with 95% accuracy
2. WHEN extracted text contains eligibility criteria, THE Policy_Ingestion_Service SHALL identify rule clauses using natural language processing
3. WHEN rule clauses are identified, THE Policy_Ingestion_Service SHALL convert them into Rule_Schema format with structured conditions
4. WHEN Rule_Schema is generated, THE Policy_Ingestion_Service SHALL validate schema completeness and flag missing mandatory fields
5. WHEN validation passes, THE Policy_Ingestion_Service SHALL store the Rule_Schema in the Rule Store with versioning
6. IF PDF extraction fails, THEN THE Policy_Ingestion_Service SHALL return a descriptive error with page numbers indicating failure points
7. WHEN a scheme document is updated, THE Policy_Ingestion_Service SHALL create a new version while preserving historical rules

### Requirement 2: Eligibility Computation Engine

**User Story:** As a rural citizen, I want the system to automatically determine which schemes I qualify for, so that I don't miss eligible benefits.

#### Acceptance Criteria

1. WHEN a User_Profile is submitted, THE Eligibility_Engine SHALL evaluate it against all active scheme rules within 3 seconds
2. WHEN evaluating eligibility, THE Eligibility_Engine SHALL apply constraint-based filtering to eliminate non-matching schemes
3. WHEN multiple conditions exist in a rule, THE Eligibility_Engine SHALL correctly interpret AND, OR, and NOT logical operators
4. WHEN a scheme has nested conditions, THE Eligibility_Engine SHALL traverse the decision graph to a maximum depth of 10 levels
5. WHEN eligibility is determined, THE Eligibility_Engine SHALL compute a Match_Score between 0 and 100 for each qualifying scheme
6. WHEN a User_Profile is missing required fields, THE Eligibility_Engine SHALL identify which schemes cannot be evaluated and list missing data
7. THE Eligibility_Engine SHALL process eligibility checks for 1000 concurrent users without degradation

### Requirement 3: Multilingual Voice Interface

**User Story:** As a low-literacy rural user, I want to interact with the platform using voice in my native language, so that I can access schemes without typing.

#### Acceptance Criteria

1. WHEN a user speaks in Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, or Odia, THE Voice_Interface SHALL transcribe speech to text with 90% accuracy
2. WHEN transcribed text is received, THE Voice_Interface SHALL identify user intent (check eligibility, ask question, provide information) with 85% accuracy
3. WHEN user intent is ambiguous, THE Voice_Interface SHALL ask clarifying questions in the user's selected language
4. WHEN the system generates a response, THE Voice_Interface SHALL convert text to natural speech in the user's language with human-like prosody
5. WHEN a conversation spans multiple turns, THE Voice_Interface SHALL maintain dialogue context for up to 10 exchanges
6. WHEN background noise exceeds 60 decibels, THE Voice_Interface SHALL apply noise cancellation before transcription
7. THE Voice_Interface SHALL support code-switching between English and regional languages within a single conversation

### Requirement 4: Document Intelligence

**User Story:** As a user with physical documents, I want to upload photos of my Aadhaar and income certificate, so that the system auto-fills my profile without manual typing.

#### Acceptance Criteria

1. WHEN an Aadhaar card image is uploaded, THE Document_Intelligence_Service SHALL extract name, date of birth, gender, and address with 98% accuracy
2. WHEN an income certificate image is uploaded, THE Document_Intelligence_Service SHALL extract annual income, issuing authority, and validity date
3. WHEN extracted data contains inconsistencies, THE Document_Intelligence_Service SHALL flag fields for manual verification
4. WHEN multiple document types are uploaded, THE Document_Intelligence_Service SHALL cross-validate data across documents for consistency
5. WHEN extracted data is validated, THE Document_Intelligence_Service SHALL populate the User_Profile automatically
6. IF document quality is poor (blur, low resolution), THEN THE Document_Intelligence_Service SHALL request a clearer image with specific guidance
7. WHEN PII is extracted, THE Document_Intelligence_Service SHALL mask sensitive fields in logs and apply encryption at rest

### Requirement 5: Scheme Ranking and Recommendation

**User Story:** As a user who qualifies for multiple schemes, I want to see the most relevant schemes first, so that I can prioritize high-value applications.

#### Acceptance Criteria

1. WHEN multiple schemes match a User_Profile, THE Recommendation_Engine SHALL rank them by Match_Score in descending order
2. WHEN computing Match_Score, THE Recommendation_Engine SHALL consider benefit amount, application complexity, and approval probability
3. WHEN a scheme requires additional documents, THE Recommendation_Engine SHALL list missing documents with examples
4. WHEN displaying a scheme, THE Recommendation_Engine SHALL provide step-by-step application guidance in the user's language
5. WHEN a user has previously applied to a scheme, THE Recommendation_Engine SHALL exclude it from recommendations
6. WHEN a scheme deadline is within 30 days, THE Recommendation_Engine SHALL prioritize it with an urgency indicator
7. THE Recommendation_Engine SHALL explain why a scheme was recommended using interpretable criteria

### Requirement 6: User Profile Management

**User Story:** As a registered user, I want to save my profile information securely, so that I don't need to re-enter data on subsequent visits.

#### Acceptance Criteria

1. WHEN a user creates a profile, THE JanMitra_Platform SHALL collect name, age, gender, income, caste category, occupation, and location
2. WHEN profile data is saved, THE JanMitra_Platform SHALL encrypt PII using AES-256 encryption
3. WHEN a user updates their profile, THE JanMitra_Platform SHALL maintain an audit log of changes with timestamps
4. WHEN a user requests profile deletion, THE JanMitra_Platform SHALL permanently remove all PII within 30 days
5. WHEN a user logs in, THE JanMitra_Platform SHALL authenticate using Aadhaar-based OTP or mobile OTP
6. THE JanMitra_Platform SHALL enforce role-based access control with separate permissions for users, CSC operators, and administrators
7. WHEN a profile is inactive for 2 years, THE JanMitra_Platform SHALL archive it and notify the user before deletion

### Requirement 7: Scalability and Performance

**User Story:** As a platform operator, I want the system to handle peak loads during scheme announcement periods, so that users experience no downtime.

#### Acceptance Criteria

1. THE JanMitra_Platform SHALL support 100 million registered users with horizontal scaling
2. WHEN concurrent user load reaches 100,000, THE JanMitra_Platform SHALL maintain response times under 3 seconds for 95% of requests
3. WHEN traffic spikes occur, THE JanMitra_Platform SHALL auto-scale compute resources within 2 minutes
4. THE JanMitra_Platform SHALL achieve 99.9% uptime measured monthly
5. WHEN database queries exceed 1000 QPS, THE JanMitra_Platform SHALL use read replicas to distribute load
6. THE JanMitra_Platform SHALL cache frequently accessed scheme rules with a 95% cache hit rate
7. WHEN system errors occur, THE JanMitra_Platform SHALL log errors with correlation IDs for debugging

### Requirement 8: Security and Compliance

**User Story:** As a data protection officer, I want user data to be handled securely and compliantly, so that we meet GDPR and DPDP Act requirements.

#### Acceptance Criteria

1. WHEN PII is stored, THE JanMitra_Platform SHALL encrypt data at rest using KMS-managed keys
2. WHEN PII is transmitted, THE JanMitra_Platform SHALL use TLS 1.3 encryption
3. WHEN a user accesses the platform, THE JanMitra_Platform SHALL enforce rate limiting of 100 requests per minute per user
4. WHEN suspicious activity is detected, THE JanMitra_Platform SHALL trigger alerts and temporarily suspend the account
5. THE JanMitra_Platform SHALL maintain audit logs of all data access for 7 years
6. WHEN a user provides consent, THE JanMitra_Platform SHALL record consent type, timestamp, and purpose with immutable logging
7. THE JanMitra_Platform SHALL conduct automated vulnerability scans weekly and remediate critical issues within 48 hours

### Requirement 9: CSC Operator Support

**User Story:** As a CSC operator, I want to assist multiple users efficiently, so that I can serve more citizens per day.

#### Acceptance Criteria

1. WHEN a CSC operator logs in, THE JanMitra_Platform SHALL provide a dashboard showing daily assisted users and pending applications
2. WHEN an operator assists a user, THE JanMitra_Platform SHALL allow profile creation on behalf of the user with operator attribution
3. WHEN an operator submits an application, THE JanMitra_Platform SHALL generate a reference number and SMS confirmation to the user
4. THE JanMitra_Platform SHALL provide operator training modules with video tutorials in regional languages
5. WHEN an operator completes 100 successful applications, THE JanMitra_Platform SHALL award a performance badge
6. THE JanMitra_Platform SHALL track operator performance metrics including application success rate and user satisfaction
7. WHEN an operator encounters an error, THE JanMitra_Platform SHALL provide contextual help and escalation options

### Requirement 10: Reporting and Analytics

**User Story:** As a government administrator, I want to view scheme utilization analytics, so that I can identify underutilized programs and improve outreach.

#### Acceptance Criteria

1. WHEN an administrator accesses the dashboard, THE JanMitra_Platform SHALL display scheme-wise application counts, approval rates, and benefit disbursement
2. WHEN filtering by geography, THE JanMitra_Platform SHALL show district-level and state-level utilization heatmaps
3. WHEN analyzing user demographics, THE JanMitra_Platform SHALL provide breakdowns by age, gender, income bracket, and caste category
4. THE JanMitra_Platform SHALL identify schemes with less than 20% utilization and flag them for review
5. WHEN generating reports, THE JanMitra_Platform SHALL export data in CSV and PDF formats
6. THE JanMitra_Platform SHALL anonymize PII in all exported reports
7. WHEN trends are detected, THE JanMitra_Platform SHALL send automated insights to administrators monthly

### Requirement 11: Offline Capability

**User Story:** As a user in a low-connectivity area, I want to access basic scheme information offline, so that I can learn about schemes without internet.

#### Acceptance Criteria

1. WHEN the mobile app is installed, THE JanMitra_Platform SHALL download a local database of top 100 schemes by state
2. WHEN offline, THE JanMitra_Platform SHALL allow users to browse scheme descriptions and eligibility criteria
3. WHEN offline, THE JanMitra_Platform SHALL allow users to fill profile forms with local storage
4. WHEN connectivity is restored, THE JanMitra_Platform SHALL sync offline data to the server within 5 minutes
5. WHEN scheme data is updated, THE JanMitra_Platform SHALL push incremental updates to minimize data usage
6. THE JanMitra_Platform SHALL indicate offline mode with a clear visual indicator
7. WHEN critical features require connectivity, THE JanMitra_Platform SHALL display a message explaining the limitation

### Requirement 12: Notification System

**User Story:** As a user, I want to receive timely notifications about new schemes and application status, so that I don't miss deadlines.

#### Acceptance Criteria

1. WHEN a new scheme matching a User_Profile is published, THE JanMitra_Platform SHALL send a notification within 24 hours
2. WHEN an application status changes, THE JanMitra_Platform SHALL notify the user via SMS and in-app notification
3. WHEN a scheme deadline is 7 days away, THE JanMitra_Platform SHALL send a reminder notification
4. WHEN a user opts out of notifications, THE JanMitra_Platform SHALL respect the preference and stop sending non-critical alerts
5. THE JanMitra_Platform SHALL support notification delivery via SMS, WhatsApp, and push notifications
6. WHEN a notification is sent, THE JanMitra_Platform SHALL log delivery status and retry failed deliveries up to 3 times
7. THE JanMitra_Platform SHALL allow users to configure notification preferences by category (new schemes, deadlines, status updates)

