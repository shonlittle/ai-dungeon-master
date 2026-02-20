"""Pydantic models for request/response validation."""

from typing import List, Optional

from pydantic import BaseModel, Field


class StateUpdates(BaseModel):
    """Updates to apply to game state after a turn."""

    hp_delta: int = Field(default=0, description="HP change")
    inventory_add: List[str] = Field(default_factory=list, description="Items to add")
    inventory_remove: List[str] = Field(
        default_factory=list, description="Items to remove"
    )
    location: str = Field(default="", description="New location")
    last_scene: str = Field(default="", description="Summary of last scene")


class DMResponse(BaseModel):
    """Response from the Dungeon Master (LLM)."""

    dm_narration: str = Field(description="1-5 short paragraphs of narration")
    scene_summary: str = Field(description="1-2 sentence summary")
    suggested_actions: List[str] = Field(
        description="Exactly 3 suggested actions", min_items=3, max_items=3
    )
    state_updates: StateUpdates = Field(description="State updates")
    game_over: bool = Field(default=False, description="Game over status")


class GameState(BaseModel):
    """Complete game state sent by client."""

    campaign_seed: str = Field(description="Campaign seed")
    player_name: str = Field(description="Player character name")
    player_class: str = Field(default="Rogue", description="Character class")
    inventory: List[str] = Field(default_factory=list, description="Inventory")
    hp: int = Field(ge=0, description="Hit points")
    location: str = Field(description="Current location")
    last_scene: str = Field(default="", description="Summary of last scene")
    turn_count: int = Field(ge=0, description="Number of turns taken")


class DMRequest(BaseModel):
    """Request to get DM narration."""

    state: GameState = Field(description="Current game state")
    player_action: Optional[str] = Field(
        default=None, description="Player action this turn"
    )


class VoiceRequest(BaseModel):
    """Request to generate voice narration."""

    text: str = Field(description="Text to convert to speech")


class VoiceResponse(BaseModel):
    """Response with voice audio."""

    audio_base64: str = Field(description="Base64-encoded audio data")
    content_type: str = Field(default="audio/mp3", description="MIME type")
