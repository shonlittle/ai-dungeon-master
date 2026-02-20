"""Adapter for Grok LLM API calls."""

import json
import os
from typing import Optional

import httpx
from dotenv import load_dotenv

from models import DMResponse, GameState

load_dotenv()


class GrokProvider:
    """Interface to Grok LLM for DM narration generation."""

    def __init__(self):
        """Initialize Grok provider with API credentials."""
        self.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv(
            "XAI_API_KEY"
        )
        self.llm_model = os.getenv("LLM_MODEL", "grok-4-fast-non-reasoning")
        # OpenRouter URL for xAI models
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate_dm_response(
        self, state: GameState, player_action: Optional[str] = None
    ) -> DMResponse:
        """
        Generate DM narration using Grok LLM.

        Args:
            state: Current game state
            player_action: Optional player action to respond to

        Returns:
            Parsed DMResponse from LLM

        Raises:
            ValueError: If response is invalid JSON or missing required fields
        """
        prompt = self._build_dm_prompt(state, player_action)

        try:
            response = await self._call_grok(prompt)
            dm_response = self._parse_response(response)
            return dm_response
        except json.JSONDecodeError:
            # Retry with JSON correction prompt
            correction_prompt = (
                f"{prompt}\n\n"
                "IMPORTANT: Return ONLY valid JSON, nothing else. No markdown, "
                "no code blocks, just raw JSON."
            )
            response = await self._call_grok(correction_prompt)
            dm_response = self._parse_response(response)
            return dm_response

    def _build_dm_prompt(
        self, state: GameState, player_action: Optional[str]
    ) -> str:
        """Build the system + user prompt for DM narration."""
        system_msg = """You are a fun, cinematic Dungeon Master for a text-based RPG. Your tone is light, 
humorous, and family-friendly. Never include gore or darkness. Keep narration vivid but concise (under 1200 characters).

You MUST respond with ONLY valid JSON matching this exact schema (no markdown, no explanations):
{
  "dm_narration": "1-5 short paragraphs of vivid narration",
  "scene_summary": "1-2 sentence summary",
  "suggested_actions": ["action1", "action2", "action3"],
  "state_updates": {
    "hp_delta": <number>,
    "inventory_add": [<items>],
    "inventory_remove": [<items>],
    "location": "string",
    "last_scene": "string"
  },
  "game_over": <boolean>
}"""

        state_str = f"""Current game state:
- Player: {state.player_name} (Class: {state.player_class})
- HP: {state.hp}
- Location: {state.location}
- Inventory: {', '.join(state.inventory) if state.inventory else 'empty'}
- Turn: {state.turn_count}
- Last scene: {state.last_scene or 'Game start'}"""

        action_str = (
            f"Player action: {player_action}"
            if player_action
            else "Game start: Describe the scene as the adventure begins."
        )

        user_msg = f"""{state_str}

{action_str}

Generate the next scene, exactly 3 suggested actions, and state changes.
If the player dies or story naturally ends, set "game_over": true and give actions like ["Restart", "Review recap", "Exit"]."""

        return f"System: {system_msg}\n\nUser: {user_msg}"

    async def _call_grok(self, prompt: str) -> str:
        """Make HTTP request to Grok LLM API."""
        if not self.api_key:
            # Return mock response for testing without API key
            return self._get_mock_response()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(self.api_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _parse_response(self, response_text: str) -> DMResponse:
        """Parse and validate JSON response from LLM."""
        # Clean up response (remove markdown code blocks if present)
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        return DMResponse(**data)

    @staticmethod
    def _get_mock_response() -> str:
        """Return a mock DM response for testing without API key."""
        mock_dm = {
            "dm_narration": (
                "You wake up in a dusty tavern. The smell of ale and adventure "
                "fills the air. A cloaked figure in the corner beckons you over. "
                "What do you do?"
            ),
            "scene_summary": "A mysterious figure invites you into adventure.",
            "suggested_actions": [
                "Approach the cloaked figure",
                "Order a drink first",
                "Leave the tavern",
            ],
            "state_updates": {
                "hp_delta": 0,
                "inventory_add": ["Tavern badge"],
                "inventory_remove": [],
                "location": "Dusty Tavern",
                "last_scene": "Arrived at the tavern",
            },
            "game_over": False,
        }
        return json.dumps(mock_dm)


# Create singleton instance
grok = GrokProvider()
