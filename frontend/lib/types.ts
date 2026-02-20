/**
 * Type definitions for AI Dungeon Master game
 */

export interface StateUpdates {
  hp_delta: number;
  inventory_add: string[];
  inventory_remove: string[];
  location: string;
  last_scene: string;
}

export interface DMResponse {
  dm_narration: string;
  scene_summary: string;
  suggested_actions: [string, string, string];
  state_updates: StateUpdates;
  game_over: boolean;
}

export interface GameState {
  campaign_seed: string;
  player_name: string;
  player_class: string;
  inventory: string[];
  hp: number;
  location: string;
  last_scene: string;
  turn_count: number;
}

export interface DMRequest {
  state: GameState;
  player_action?: string;
}

export interface VoiceRequest {
  text: string;
}

export interface VoiceResponse {
  audio_base64: string;
  content_type: string;
}
