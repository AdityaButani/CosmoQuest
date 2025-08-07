# Questify - AI-Powered Learning Adventure Platform

## Overview

Questify is an educational web application that transforms any topic into an interactive 5-part learning quest. Users enter a subject (e.g., "Photosynthesis", "World War II", "Machine Learning") and the system generates a structured learning journey with explanations, quizzes, and additional resources. The application features a space-themed interface to gamify the learning experience, making education feel like an adventure through knowledge galaxies.

## User Preferences

Preferred communication style: Simple, everyday language.

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
- **Primary Storage**: Session-based storage (no persistent database)
- **State Management**: Flask sessions store current quest progress, completed quests, topic context, and generated content
- **Rationale**: Simplified architecture avoiding database complexity for MVP, suitable for stateless quest generation

### AI Integration Architecture
- **Primary AI Service**: Groq API using LLaMA 3.3 70B model for quest content generation
- **Content Generation**: Structured prompts for creating educational content, explanations, and quiz questions
- **Context Enhancement**: SerperAPI integration for real-time web search to enrich topic understanding
- **Fallback Strategy**: Graceful degradation when API services are unavailable

### Quest Flow System
- **Structured Learning Path**: 5-part quest system with progressive difficulty
- **Quiz Integration**: Automated quiz generation after quests 2-5 with varying question types
- **Progress Tracking**: Visual progress indicators and completion status management
- **Content Types**: Mix of explanations, fun facts, visual elements, and interactive assessments

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