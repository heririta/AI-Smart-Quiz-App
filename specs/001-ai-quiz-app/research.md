# Research Findings: AI Smart Quiz App

**Date**: 2025-10-19
**Purpose**: Technical research to inform implementation decisions

## Framework Decision: Streamlit

**Decision**: Use Streamlit as the primary framework
**Rationale**:
- Rapid development capabilities perfect for single-page quiz application
- Built-in session state management (`st.session_state`)
- Native chart integration with Plotly
- Excellent audio handling with in-memory playback
- Single-app architecture aligns with constitution

**Alternatives considered**:
- Flask: More flexibility but slower development
- Dash: Superior charts but steeper learning curve
- **Chosen**: Streamlit for best balance of speed and functionality

## Text-to-Speech Integration

**Decision**: Use OpenAI TTS API with in-memory streaming
**Rationale**:
- High-quality voices (alloy, echo, fable, onyx, nova, shimmer)
- Streaming support eliminates permanent file storage
- Robust error handling and retry mechanisms
- Rate limiting protection built-in

**Key Implementation**:
```python
def text_to_speech_stream(text, voice="alloy"):
    with client.audio.speech.with_streaming_response.create(
        model="tts-1", voice=voice, input=text
    ) as response:
        audio_buffer = io.BytesIO()
        response.stream_to_file(audio_buffer)
        return audio_buffer.getvalue()
```

## Audio Processing Strategy

**Decision**: Pure in-memory audio handling
**Rationale**:
- No permanent file storage meets requirement
- Streamlit's `st.audio()` supports direct byte playback
- Better performance and security
- Simplified cleanup and resource management

## Database Architecture

**Decision**: SQLite with direct connection
**Rationale**:
- Local-first data management per constitution
- No external database dependencies
- Built-in Python support (`sqlite3` module)
- Perfect for single-app architecture

## Chart & Visualization

**Decision**: Plotly Express with Streamlit integration
**Rationale**:
- Native Streamlit support
- Rich interactive charts
- Real-time data updates
- Excellent for analytics dashboard

## Error Handling & Resilience

**Decision**: Comprehensive error handling with rate limiting
**Rationale**:
- External API dependencies require robust fallbacks
- User experience protection during API failures
- Graceful degradation when TTS unavailable
- Rate limiting prevents API abuse

## Security Considerations

**Decision**: Streamlit secrets for API key management
**Rationale**:
- Secure API key storage
- No hardcoded credentials
- Environment-based configuration
- Production-ready security approach

## Performance Optimization

**Decision**: Session state management with efficient caching
**Rationale**:
- Streamlit's built-in session state optimization
- In-memory quiz state tracking
- Minimal database queries
- Responsive user experience

## Dependencies Summary

**Core Dependencies**:
- `streamlit>=1.28.0` - Main framework
- `openai>=1.68.0` - TTS API integration
- `pydantic>=2.0.0` - Data validation
- `plotly>=5.0.0` - Charts and visualization
- `pandas>=2.0.0` - Data handling for CSV import/export

**Optional Dependencies**:
- `pydub>=0.25.1` - Advanced audio processing (if needed)
- `python-dotenv>=1.0.0` - Environment variable management