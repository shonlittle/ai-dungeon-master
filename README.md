# AI Dungeon Master

An immersive AI-powered storytelling adventure game that uses Grok LLM for intelligent narration and text-to-speech for voice narration. Step into a dynamic fantasy world where every decision shapes your story.

## Features

- **AI-Powered Storytelling**: Uses Grok LLM to generate unique, cinematic narratives
- **Voice Narration**: Text-to-speech integration for immersive audio experience
- **Dynamic Game State**: Character progression with HP, inventory, and location tracking
- **Interactive Gameplay**: Choose from suggested actions or type custom commands
- **Minimal Dependencies**: Lightweight, fast, and easy to deploy
- **Type-Safe**: Full TypeScript support for both frontend and backend
- **Docker Ready**: Complete Docker Compose setup for easy deployment

## Tech Stack

**Backend:**

- FastAPI (Python)
- Pydantic for validation
- Async/await for non-blocking I/O

**Frontend:**

- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- React Hooks for state management

**Infrastructure:**

- Docker & Docker Compose
- Port 8002 (Backend)
- Port 3000 (Frontend)

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Grok API Key (from OpenRouter or xAI)

### Using Docker Compose (Recommended)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/shonlittle/ai-dungeon-master.git
   cd ai-dungeon-master
   ```

2. **Create `.env` file in the root directory:**

   ```bash
   cp backend/.env.example backend/.env
   ```

3. **Add your API credentials to `backend/.env`:**

   ```
   LLM_PROVIDER=xai
   LLM_MODEL=grok-4-fast-non-reasoning
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   XAI_API_KEY=your_xai_api_key_here
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8002
   ```

4. **Start the application:**

   ```bash
   docker-compose up --build
   ```

5. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend API Docs: http://localhost:8002/docs

### Local Development (Without Docker)

#### Backend Setup

1. **Navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Create Python virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**

   ```bash
   cp .env.example .env
   ```

5. **Add your API credentials:**

   ```
   LLM_PROVIDER=xai
   LLM_MODEL=grok-4-fast-non-reasoning
   OPENROUTER_API_KEY=your_key_here
   XAI_API_KEY=your_key_here
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8002
   ```

6. **Run the backend:**
   ```bash
   python main.py
   ```

#### Frontend Setup

1. **In a new terminal, navigate to frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Create `.env.local` file:**

   ```bash
   echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8002" > .env.local
   ```

4. **Run the frontend:**

   ```bash
   npm run dev
   ```

5. **Open http://localhost:3000 in your browser**

## How It Works

### Game Flow

```
1. User enters character name and class
2. Frontend creates initial GameState
3. Requests /api/dm endpoint with game state
4. Backend calls Grok LLM with DM prompt
5. Grok returns JSON with narration + actions
6. Frontend requests /api/voice for audio narration
7. Audio plays while user reads/listens
8. User selects action or types custom command
9. Loop repeats with updated game state
```

### Game State Structure

```typescript
interface GameState {
  campaign_seed: string; // Random ID for campaign continuity
  player_name: string; // Character name
  player_class: string; // Class: Rogue, Wizard, Warrior, Cleric
  inventory: string[]; // Items collected
  hp: number; // Health points (0-20)
  location: string; // Current location
  last_scene: string; // Previous scene summary
  turn_count: number; // Turn number
}
```

### API Endpoints

#### `POST /api/dm`

Generates DM narration for the current turn.

**Request:**

```json
{
  "state": {
    "campaign_seed": "abc123",
    "player_name": "Aragorn",
    "player_class": "Warrior",
    "inventory": ["Sword"],
    "hp": 18,
    "location": "Forest",
    "last_scene": "Entered the dark forest",
    "turn_count": 5
  },
  "player_action": "Attack the goblin"
}
```

**Response:**

```json
{
  "dm_narration": "The goblin lunges at you with surprising speed...",
  "scene_summary": "A fierce battle in the forest",
  "suggested_actions": [
    "Roll for initiative",
    "Use a special ability",
    "Attempt to flee"
  ],
  "state_updates": {
    "hp_delta": -2,
    "inventory_add": ["Goblin's gold coin"],
    "inventory_remove": [],
    "location": "Dark Forest clearing",
    "last_scene": "Defeated a goblin"
  },
  "game_over": false
}
```

#### `POST /api/voice`

Generates voice narration for text.

**Request:**

```json
{
  "text": "The goblin lunges at you with surprising speed..."
}
```

**Response:**

```json
{
  "audio_base64": "//NExAAqgI...",
  "content_type": "audio/mp3"
}
```

#### `GET /api/game-start`

Returns initial game setup information.

**Response:**

```json
{
  "message": "Welcome to AI Dungeon Master!",
  "initial_hp": 20,
  "default_class": "Rogue",
  "available_classes": ["Rogue", "Wizard", "Warrior", "Cleric"]
}
```

## Customizing the DM Prompt

The DM prompt is located in `backend/grok_provider.py` in the `_build_dm_prompt` method. You can customize:

- **Tone**: Change the personality (humorous, dark, epic, etc.)
- **Story Focus**: Adjust the narrative style
- **Game Difficulty**: Modify HP deltas and challenge level
- **Setting**: Change the fantasy world context

Example customization:

```python
system_msg = """You are a witty, sarcastic Dungeon Master for a comedic RPG.
Your tone is irreverent, funny, and sometimes absurd. Include pop culture references
and break the fourth wall occasionally."""
```

## Integrating Real Grok Voice API

The voice provider is currently using mock audio. To integrate the real Grok Voice API:

1. **Update `backend/voice_provider.py`:**
   - Replace the `api_url` with the actual Grok Voice endpoint
   - Implement the actual request payload format
   - Handle the response accordingly

2. **Current placeholder:**

   ```python
   # TODO: Replace with actual Grok Voice endpoint
   self.api_url = "https://api.x.ai/v1/audio/speech"
   ```

3. **Expected implementation pattern:**
   ```python
   async def _call_voice_api(self, text: str) -> str:
       payload = {
           "text": text,
           "voice": "alloy",
           "model": "grok-voice-1"
       }
       # Make request and handle response
   ```

## Integrating Real OpenRouter/xAI Endpoint

The LLM calls are configured to use OpenRouter by default. To ensure proper integration:

1. **Verify credentials in `backend/.env`:**

   ```
   OPENROUTER_API_KEY=your_key_here
   ```

2. **The backend automatically selects the endpoint** based on the `LLM_PROVIDER` setting

3. **If using xAI directly:**
   ```
   LLM_PROVIDER=xai
   XAI_API_KEY=your_xai_key_here
   ```

## Error Handling

Both frontend and backend include comprehensive error handling:

- **Validation**: Pydantic on backend, TypeScript types on frontend
- **Retry Logic**: LLM response JSON parsing with automatic retry
- **User Feedback**: Toast-like error messages in the UI
- **Graceful Degradation**: Mock audio and responses work without real API keys

## Troubleshooting

### Backend issues

- **Port 8002 already in use:** Change port in `docker-compose.yml`
- **Module not found:** Run `pip install -r requirements.txt` in backend
- **API key errors:** Verify credentials in `backend/.env`

### Frontend issues

- **API connection refused:** Ensure backend is running on port 8002
- **Module not found:** Run `npm install` in frontend directory
- **Port 3000 in use:** Run `npm run dev -- -p 3001` for different port

### Docker issues

- **Build failures:** Check Docker logs with `docker-compose logs backend` or `docker-compose logs frontend`
- **Slow startup:** First run downloads and installs dependencies; subsequent runs are faster
- **Memory issues:** Increase Docker's memory allocation in Docker Desktop settings

## Project Structure

```
ai-dungeon-master/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── grok_provider.py     # LLM integration
│   ├── voice_provider.py    # Voice/TTS integration
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend container
│   ├── .env.example         # Example environment variables
│   └── .flake8              # Python linting config
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main game component
│   │   ├── layout.tsx       # Root layout
│   │   └── globals.css      # Global styles
│   ├── lib/
│   │   ├── types.ts         # TypeScript type definitions
│   │   └── gameClient.ts    # API client
│   ├── package.json         # Node dependencies
│   ├── tsconfig.json        # TypeScript config
│   ├── tailwind.config.ts   # Tailwind CSS config
│   ├── Dockerfile           # Frontend container
│   ├── .env.local           # Local environment variables
│   └── next.config.js       # Next.js config
│
├── docker-compose.yml       # Docker Compose orchestration
└── README.md                # This file
```

## Development Tips

### Testing without API Keys

Both services have fallback mock implementations:

- **Backend**: Without API keys, returns a pre-written adventure scene
- **Frontend**: Works with mock responses, great for UI testing
- **Voice**: Generates minimal valid MP3 frames for testing

### Code Quality

- **Backend**: Uses flake8 for Python linting
- **Frontend**: Uses TypeScript for type safety

Check code quality:

```bash
# Backend
cd backend && python -m flake8 .

# Frontend
cd frontend && npm run lint
```

### Performance Tips

- **Disable audio playback** for faster testing (use "Skip" button)
- **Use mocked responses** for UI development
- **Profile with browser DevTools** to identify slow components

## Contributing

Contributions are welcome! Areas for improvement:

- More sophisticated game world generation
- Persistent game saves
- Multiplayer support
- Advanced character customization
- Different game genres (sci-fi, horror, mystery)

## License

MIT - Feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [Next.js](https://nextjs.org/)
- Powered by [Grok LLM](https://x.ai/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
