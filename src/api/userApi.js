import { checkResponse } from '../utils/httpUtils.js'

export async function fetchInfo() {
  try {
    const response = await fetch("/fetch_info/", {
      method: "GET",
    });
    await checkResponse(response);
    const data = await response.json();
    handleFetchInfoResponse(data);
  } catch (e) {
    console.error("There was a problem:", e);
  }
}
