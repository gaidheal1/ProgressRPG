export function validateInput(input) {
  const pattern = /^[a-zA-Z0-9\s]+$/; // Adjust pattern as needed
  return pattern.test(input);
}
