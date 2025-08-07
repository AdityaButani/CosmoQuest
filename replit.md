# Questify - AI-Powered Learning Adventure Platform

## Overview

Questify is an educational web application that transforms any topic into an interactive 5-part learning quest. Users enter a subject (e.g., "Photosynthesis", "World War II", "Machine Learning") and the system generates a structured learning journey with explanations, quizzes, and additional resources. The application features a space-themed interface to gamify the learning experience, making education feel like an adventure through knowledge galaxies.

## User Preferences

Preferred communication style: Simple, everyday language.

### Educational Content Requirements (Updated)
- Each quest must cover distinct, non-overlapping subtopics
- Progressive complexity with specialized focus areas per quest
- No repetition of generic themes like "introduction" or "key concepts" across quests
- Content organized with quest-specific headings reflecting unique content areas
- Quiz questions test application and understanding, not just recall
- Varied question formats across quests with no redundancy

## System Architecture

### Frontend Architecture
- **Technology Stack**: HTML templates with Jinja2 templating, Tailwind CSS for styling, and vanilla JavaScript for interactivity
- **Design Pattern**: Traditional server-side rendered web application with progressive enhancement
- **UI Theme**: Space-themed interface with animated star backgrounds, gradient effects, and cosmic imagery
- **Responsive Design**: Mobile-first approach using Tailwind CSS utilities and responsive breakpoints

### Backend Architecture
- **Framework**: Flask (Python) web framework following a simple MVC pattern
- **Session Management**: Server-side sessions for maintaining user quest progress and state
- **API Design**: RESTful endpoints for quest generation and navigation
- **Error Handling**: Comprehensive logging and graceful error responses for API failures

### Data Storage Solutions
- **Primary Storage**: Server-side quest data cache with session-based state management
- **Quest Data Cache**: In-memory storage for large quest content to prevent session cookie size limits
- **Session Management**: Flask sessions store minimal data (topic, progress, unique session ID)
- **Automatic Regeneration**: Quest data regenerated automatically if missing from cache
- **Rationale**: Hybrid approach prevents session cookie overflow while maintaining stateless architecture

### AI Integration Architecture
- **Primary AI Service**: Groq API using LLaMA 3.3 70B model for quest content generation
- **Content Generation**: Structured prompts for creating educational content, explanations, and quiz questions
- **Context Enhancement**: SerperAPI integration for real-time web search to enrich topic understanding
- **Fallback Strategy**: Graceful degradation when API services are unavailable

### Quest Flow System
- **Distinct Content Areas**: Each quest covers completely different, non-overlapping aspects of the topic
- **Specialized Quest Focus**: 
  - Quest 1: Foundations & Core Principles (definitions, history, fundamental principles)
  - Quest 2: Mechanisms & Processes (step-by-step how it works, underlying mechanisms)
  - Quest 3: Advanced Systems & Interactions (complex relationships, specialized techniques)
  - Quest 4: Real-World Applications & Impact (practical uses, industry applications, societal impact)
  - Quest 5: Innovations & Future Directions (latest research, emerging trends, cutting-edge developments)
- **Educational Content**: 250-300 word specialized explanations with quest-specific HTML headings and organization
- **Progressive Knowledge Building**: Each quest assumes knowledge from previous quests while covering unique content areas
- **Advanced Quiz Design**: Questions test application and analysis rather than recall, with quest-specific focus
- **Server-side Storage**: Quest data cached server-side to prevent session cookie size limits
- **Content Quality**: Eliminates generic sections and repetitive themes across quests

## External Dependencies

### AI and Search APIs
- **Groq API**: LLaMA 3.3 70B model for natural language generation and educational content creation
- **SerperAPI**: Google Search API wrapper for gathering real-time context about user topics
- **API Key Management**: Environment variable configuration for secure credential storage

### Frontend Libraries
- **Tailwind CSS**: Utility-first CSS framework loaded via CDN for rapid UI development
- **Font Awesome**: Icon library for space-themed and educational iconography
- **Vanilla JavaScript**: No heavy frontend frameworks, keeping the client-side lightweight

### Python Dependencies
- **Flask**: Micro web framework for HTTP handling and routing
- **Requests**: HTTP client library for external API communications
- **Werkzeug**: WSGI utilities for proxy handling and middleware support

### Infrastructure Requirements
- **Environment Variables**: GROQ_API_KEY and SERPER_API_KEY for service authentication
- **Session Configuration**: Secure session secret key for user state management
- **Logging**: Python logging module for debugging and monitoring API interactions