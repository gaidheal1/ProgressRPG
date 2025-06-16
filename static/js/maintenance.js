document.addEventListener("DOMContentLoaded", () => {
        
    const gameplayContainer = document.getElementById("gameplay-container");
    const profileId = gameplayContainer?.dataset.profileId;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const url = `${protocol}://${window.location.host}/ws/profile_${profileId}/`;

    const socket = new WebSocket(url);

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log("Received message:", data);
        if (data.action === "load-game" && data.success) {
            console.log("Maintenance ended! Redirecting to game...");
            window.location.href = "/game/";  // 🚀 Load the game page when maintenance ends
        }
    };
  });

