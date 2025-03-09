export async function checkInternetConnection() {
  if (!navigator.onLine) {
    console.warn("Client is offline based on navigator.onLine");
    return false;
  }

  try {
    const response = await fetch("/ping.json", { cache: 'no-store' });
    if (response.ok) {
      console.log("Internet connection verified.");
      return true;
    } else {
      console.error("Failed to fetch the resource. Response status:", response.status);
      return false;
    }
  } catch (e) {
    console.error("Error during connectivity check:", e);
    return false;
  }
}

export function onOffline() {
  console.log("User is now offline.");
}

export async function onOnline(submitPendingReports) {
  console.log("User is back online. Attempting to submit pending reports...");
  const connection = await checkInternetConnection();
  if (connection) {
    await submitPendingReports();
  }
}
