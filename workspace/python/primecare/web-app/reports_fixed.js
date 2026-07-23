// Helper to make API calls consistently
async function fetchAPI(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const data = await response.json();
  if (data.error) {
    throw new Error(data.error);
  }
  return data;
}

// Update all the api() calls to fetchAPI()
// Replace all instances of:
// const data = await api('GET', url);
// With:
// const data = await fetchAPI(url);
