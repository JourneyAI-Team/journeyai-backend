# Session Auto-Titling

## Overview

The JourneyAI application now automatically generates descriptive titles for chat sessions after users have sent exactly 2 messages. This feature helps users quickly identify and navigate between different conversation topics.

## How It Works

1. **Trigger**: When a user sends a message via WebSocket, the system enqueues a session titling check
2. **Condition**: The system only generates a title when:
   - The session has exactly 2 user messages
   - The session still has the default title "New Session"
3. **Generation**: An AI service analyzes the first 2 user messages and generates a concise, descriptive title (3-6 words)
4. **Update**: The session title is automatically updated in the database

## Architecture

### Components

- **Sessions Worker** (`app/workers/sessions/`): New worker dedicated to session-related background tasks
- **Auto-titling Task** (`check_and_title_session`): Analyzes message count and generates titles
- **Integration**: Triggered automatically after each user message via WebSocket handler

### Flow

```
User sends message → WebSocket handler → Save message → Enqueue titling task → Sessions worker → Check message count → Generate title (if needed) → Update session
```

## Configuration

### Worker Setup

The sessions worker is configured in:
- `docker-compose.yaml`: Production environment
- `Procfile`: Local development environment

### AI Service

The title generation uses the same AI service configuration as other parts of the application:
- **Primary**: Groq API (llama3-8b-8192)
- **Fallback**: OpenAI API (chatgpt-4o-latest)
- **Offline Fallback**: First 4 words of the first message

## Examples

### Input Messages
```
Message 1: "Hello, I need help with Python programming"
Message 2: "Specifically, I want to learn about async programming and FastAPI"
```

### Generated Title
```
"Python Async Programming Help"
```

### Input Messages
```
Message 1: "Can you help me create a marketing strategy?"
Message 2: "I'm launching a new SaaS product"
```

### Generated Title
```
"SaaS Marketing Strategy Planning"
```

## Testing

### Manual Testing

1. Start the local development environment:
   ```bash
   make run-local
   ```

2. Run the test script:
   ```bash
   python manual_scripts/test_session_titling.py
   ```

3. Or test via WebSocket:
   - Create a new session
   - Send exactly 2 user messages
   - Verify the session title updates automatically

### Monitoring

The sessions worker logs all titling activities:
- Debug: Message count checks
- Info: Title generation attempts
- Success: Successful title updates
- Error: Failed title generation or updates

## Error Handling

The system includes robust error handling:
- **API Failures**: Falls back to simpler text-based title generation
- **Empty Messages**: Returns default "New Session" title
- **Database Errors**: Logs errors but doesn't break the user experience
- **Worker Failures**: Isolated to the sessions worker, doesn't affect other functionality

## Performance Considerations

- **Lightweight**: Only processes sessions with exactly 2 user messages
- **Asynchronous**: Runs in background without blocking user interactions
- **Efficient**: Uses short AI prompts optimized for quick title generation
- **Cached**: Skips sessions that already have custom titles

## Future Enhancements

Potential improvements could include:
- User preference settings for auto-titling
- Custom title templates per assistant type
- Bulk title generation for existing sessions
- Title regeneration options 