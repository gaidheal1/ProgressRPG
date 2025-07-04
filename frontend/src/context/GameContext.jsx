// GameContext.jsx
import { createContext, useContext } from 'react';
import { useBootstrapGameData } from '../hooks/useBootstrapGameData';

const GameContext = createContext();

export const useGame = () => {

  const context = useContext(GameContext);
  //console.log('useGame called, context:', context);
  return context;
}

export const GameProvider = ({ children }) => {
  const gameData = useBootstrapGameData();

  return (
    <GameContext.Provider value={gameData}>
      {children}
    </GameContext.Provider>
  );
};
