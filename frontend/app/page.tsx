"use client";

import { useState, useRef } from "react";
import { GameState, DMResponse } from "@/lib/types";
import { gameClient } from "@/lib/gameClient";

export default function Home() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [dmResponse, setDmResponse] = useState<DMResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [audioPlaying, setAudioPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [customAction, setCustomAction] = useState("");
  const [playerName, setPlayerName] = useState("");
  const [playerClass, setPlayerClass] = useState("Rogue");
  const audioRef = useRef<HTMLAudioElement>(null);

  const generateCampaignSeed = () => {
    return Math.random().toString(36).substring(2, 11);
  };

  const startAdventure = async () => {
    const newState: GameState = {
      campaign_seed: generateCampaignSeed(),
      player_name: playerName || "Adventurer",
      player_class: playerClass,
      inventory: [],
      hp: 20,
      location: "Starting Point",
      last_scene: "",
      turn_count: 0,
    };

    setGameState(newState);
    setError(null);
    await getDMResponse(newState);
  };

  const getDMResponse = async (state: GameState, action?: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await gameClient.getDMResponse(state, action);
      setDmResponse(response);

      // Apply state updates
      const updatedState: GameState = {
        ...state,
        hp: Math.max(0, state.hp + response.state_updates.hp_delta),
        inventory: [
          ...state.inventory.filter(
            (item) => !response.state_updates.inventory_remove.includes(item),
          ),
          ...response.state_updates.inventory_add,
        ],
        location: response.state_updates.location || state.location,
        last_scene: response.state_updates.last_scene || state.last_scene,
        turn_count: state.turn_count + 1,
      };

      setGameState(updatedState);

      // Get voice narration
      if (response.dm_narration) {
        await playNarration(response.dm_narration);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to get DM response";
      setError(message);
      setLoading(false);
    }
  };

  const playNarration = async (text: string) => {
    try {
      const voiceResponse = await gameClient.getVoiceNarration(text);

      if (audioRef.current) {
        const audioData = `data:audio/mp3;base64,${voiceResponse.audio_base64}`;
        audioRef.current.src = audioData;
        setAudioPlaying(true);

        audioRef.current.onended = () => {
          setAudioPlaying(false);
          setLoading(false);
        };

        audioRef.current.play();
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to generate voice";
      setError(message);
      setLoading(false);
    }
  };

  const skipAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setAudioPlaying(false);
    setLoading(false);
  };

  const handleAction = async (action: string) => {
    if (!gameState) return;

    setCustomAction("");
    await getDMResponse(gameState, action);
  };

  const resetGame = () => {
    setGameState(null);
    setDmResponse(null);
    setCustomAction("");
    setError(null);
    setPlayerName("");
    setPlayerClass("Rogue");
  };

  if (!gameState) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-full max-w-md p-8 rounded-lg bg-gray-800 shadow-2xl">
          <h1 className="text-4xl font-bold mb-2 text-center text-yellow-400">
            AI Dungeon Master
          </h1>
          <p className="text-center text-gray-300 mb-8">
            Embark on an AI-powered adventure
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Character Name
              </label>
              <input
                type="text"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                placeholder="Enter your name"
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:border-yellow-400 focus:bg-gray-750"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Character Class
              </label>
              <select
                value={playerClass}
                onChange={(e) => setPlayerClass(e.target.value)}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-yellow-400"
              >
                <option>Rogue</option>
                <option>Wizard</option>
                <option>Warrior</option>
                <option>Cleric</option>
              </select>
            </div>

            {error && (
              <div className="p-3 bg-red-900 border border-red-700 rounded text-red-100 text-sm">
                {error}
              </div>
            )}

            <button
              onClick={startAdventure}
              className="w-full py-3 bg-yellow-500 hover:bg-yellow-600 text-gray-900 font-bold rounded transition"
            >
              Start Adventure
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Game Area */}
        <div className="lg:col-span-2 space-y-4">
          {/* Narration Panel */}
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg min-h-80">
            {dmResponse ? (
              <div>
                <h2 className="text-2xl font-bold text-yellow-400 mb-4">
                  {dmResponse.scene_summary}
                </h2>
                <p className="text-gray-100 leading-relaxed whitespace-pre-wrap">
                  {dmResponse.dm_narration}
                </p>
              </div>
            ) : (
              <p className="text-gray-400">Loading adventure...</p>
            )}
          </div>

          {/* Audio Player */}
          <audio ref={audioRef} className="w-full" />
          {audioPlaying && (
            <div className="bg-blue-900 border border-blue-600 rounded p-4 flex items-center justify-between">
              <span className="text-blue-100">🔊 Playing narration...</span>
              <button
                onClick={skipAudio}
                className="px-3 py-1 bg-blue-700 hover:bg-blue-600 rounded text-sm text-white"
              >
                Skip
              </button>
            </div>
          )}

          {/* Suggested Actions */}
          {dmResponse && !dmResponse.game_over && (
            <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-lg font-bold text-gray-200 mb-4">
                What do you do?
              </h3>
              <div className="space-y-3">
                {dmResponse.suggested_actions.map((action, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAction(action)}
                    disabled={loading || audioPlaying}
                    className="w-full text-left px-4 py-3 bg-gray-700 hover:bg-gray-600 border border-gray-600 rounded text-gray-100 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Custom Action */}
          {dmResponse && !dmResponse.game_over && (
            <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={customAction}
                  onChange={(e) => setCustomAction(e.target.value)}
                  onKeyDown={(e) => {
                    if (
                      e.key === "Enter" &&
                      customAction &&
                      !loading &&
                      !audioPlaying
                    ) {
                      handleAction(customAction);
                    }
                  }}
                  placeholder="Or type a custom action..."
                  disabled={loading || audioPlaying}
                  className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:border-yellow-400 disabled:opacity-50"
                />
                <button
                  onClick={() => customAction && handleAction(customAction)}
                  disabled={!customAction || loading || audioPlaying}
                  className="px-6 py-2 bg-yellow-500 hover:bg-yellow-600 text-gray-900 font-bold rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Send
                </button>
              </div>
            </div>
          )}

          {/* Game Over */}
          {dmResponse && dmResponse.game_over && (
            <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-xl font-bold text-yellow-400 mb-4">
                Adventure Ended
              </h3>
              <p className="text-gray-100 mb-6">{dmResponse.dm_narration}</p>
              <button
                onClick={resetGame}
                className="w-full py-3 bg-yellow-500 hover:bg-yellow-600 text-gray-900 font-bold rounded transition"
              >
                Start New Adventure
              </button>
            </div>
          )}

          {/* Error Display */}
          {error && !loading && (
            <div className="bg-red-900 border border-red-700 rounded p-4">
              <p className="text-red-100">⚠️ {error}</p>
              <button
                onClick={() => setError(null)}
                className="mt-2 text-sm px-3 py-1 bg-red-700 hover:bg-red-600 rounded text-white"
              >
                Dismiss
              </button>
            </div>
          )}
        </div>

        {/* Game State Panel */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg sticky top-4">
            <h3 className="text-lg font-bold text-yellow-400 mb-4">
              Game Status
            </h3>

            <div className="space-y-4 text-sm">
              <div>
                <p className="text-gray-400">Character</p>
                <p className="text-white font-medium">
                  {gameState.player_name}
                </p>
              </div>

              <div>
                <p className="text-gray-400">Class</p>
                <p className="text-white font-medium">
                  {gameState.player_class}
                </p>
              </div>

              <div>
                <p className="text-gray-400">Health Points</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-700 rounded h-6 overflow-hidden">
                    <div
                      className="bg-red-500 h-full transition-all"
                      style={{
                        width: `${Math.max(0, (gameState.hp / 20) * 100)}%`,
                      }}
                    />
                  </div>
                  <span className="font-bold text-white">
                    {gameState.hp}/20
                  </span>
                </div>
              </div>

              <div>
                <p className="text-gray-400">Location</p>
                <p className="text-white font-medium">{gameState.location}</p>
              </div>

              <div>
                <p className="text-gray-400">Turn</p>
                <p className="text-white font-medium">{gameState.turn_count}</p>
              </div>

              <div>
                <p className="text-gray-400 mb-2">Inventory</p>
                {gameState.inventory.length > 0 ? (
                  <ul className="space-y-1">
                    {gameState.inventory.map((item, idx) => (
                      <li
                        key={idx}
                        className="text-gray-300 text-xs bg-gray-700 px-2 py-1 rounded"
                      >
                        • {item}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 text-xs italic">Empty</p>
                )}
              </div>

              <button
                onClick={resetGame}
                className="w-full mt-6 py-2 bg-gray-700 hover:bg-gray-600 rounded text-gray-200 text-sm font-medium transition"
              >
                New Game
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
