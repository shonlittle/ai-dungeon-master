/**
 * Client for communicating with the backend AI Dungeon Master API
 */

import axios from "axios";
import {
  DMRequest,
  DMResponse,
  GameState,
  VoiceRequest,
  VoiceResponse,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8002";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

export const gameClient = {
  async getDMResponse(
    state: GameState,
    playerAction?: string,
  ): Promise<DMResponse> {
    try {
      const request: DMRequest = {
        state,
        player_action: playerAction,
      };

      const response = await client.post<DMResponse>("/api/dm", request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to get DM response: ${error.message}`);
      }
      throw error;
    }
  },

  async getVoiceNarration(text: string): Promise<VoiceResponse> {
    try {
      const request: VoiceRequest = { text };
      const response = await client.post<VoiceResponse>("/api/voice", request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to get voice narration: ${error.message}`);
      }
      throw error;
    }
  },

  async getGameStart() {
    try {
      const response = await client.get("/api/game-start");
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to get game start: ${error.message}`);
      }
      throw error;
    }
  },
};
