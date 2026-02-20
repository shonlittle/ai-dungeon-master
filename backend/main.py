"""FastAPI application for AI Dungeon Master backend."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from grok_provider import grok
from models import DMRequest, DMResponse, VoiceRequest, VoiceResponse
from voice_provider import voice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Dungeon Master API",
    description="Backend for AI-powered Dungeon Master storytelling",
    version="1.0.0",
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/dm", response_model=DMResponse)
async def generate_dm_response(request: DMRequest) -> DMResponse:
    """
    Generate DM narration for the current turn.

    Args:
        request: DMRequest with game state and optional player action

    Returns:
        DMResponse with narration, scene summary, suggested
        actions, and state updates
    """
    try:
        logger.info(
            f"DM request: turn {request.state.turn_count}, "
            f"action: {request.player_action}"
        )

        # Call Grok LLM to generate response
        dm_response = await grok.generate_dm_response(
            request.state, request.player_action
        )

        logger.info("DM response generated successfully")
        return dm_response

    except ValueError as e:
        logger.error(f"Invalid response from LLM: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse LLM response: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error generating DM response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate DM response: {str(e)}",
        )


@app.post("/api/voice", response_model=VoiceResponse)
async def generate_voice_narration(request: VoiceRequest) -> VoiceResponse:
    """
    Generate voice narration for the DM's text.

    Args:
        request: VoiceRequest with text to narrate

    Returns:
        VoiceResponse with base64-encoded audio data
    """
    try:
        logger.info(f"Voice request: {len(request.text)} characters")

        # Generate voice narration
        audio_base64 = await voice.generate_voice(request.text)

        logger.info("Voice narration generated successfully")
        return VoiceResponse(
            audio_base64=audio_base64,
            content_type="audio/mp3",
        )

    except Exception as e:
        logger.error(f"Error generating voice: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate voice narration: {str(e)}",
        )


@app.get("/api/game-start")
async def get_game_start():
    """Get initial game setup information."""
    return {
        "message": "Welcome to AI Dungeon Master!",
        "initial_hp": 20,
        "default_class": "Rogue",
        "available_classes": ["Rogue", "Wizard", "Warrior", "Cleric"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info",
    )
