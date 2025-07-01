// GameContext.js
import { createContext, useContext } from 'react';
import { useBootstrapGameData } from '../hooks/useBootstrapGameData';

const GameContext = createContext();

export const useGame = () => useContext(GameContext);

export const GameProvider = ({ children }) => {
  const gameData = useBootstrapGameData();

  return (
    <GameContext.Provider value={gameData}>
      {children}
    </GameContext.Provider>
  );
};
