export async function checkResponse(response) {
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  return response;
}