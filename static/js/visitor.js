(function () {
  const cacheKey = "visitor_count";
  const cacheTTL = 60 * 60 * 1000; // 1 hour in milliseconds

  const now = Date.now();

  // Attempt to read from sessionStorage
  let cached = null;
  try {
    cached = JSON.parse(sessionStorage.getItem(cacheKey));
  } catch (err) {
    console.warn("Failed to parse cached visitor count:", err);
  }

  const setCount = (count) => {
    document.getElementById("visitor-count").textContent = count;
  };

  // If cache exists and is fresh, use it
  if (cached && now - cached.timestamp < cacheTTL) {
    console.log("✅ Using cached visitor count:", cached.count);
    setCount(cached.count);
  } else {
    // Fetch from API
    fetch("https://uhvsu4omn5.execute-api.ap-south-1.amazonaws.com//visitor")
      .then((response) => {
        if (!response.ok) throw new Error("API response not OK");
        return response.json();
      })
      .then((data) => {
        const count = data.count;
        setCount(count);
        sessionStorage.setItem(
          cacheKey,
          JSON.stringify({ count, timestamp: now })
        );
        console.log("🔄 Visitor count updated from API:", count);
      })
      .catch((error) => {
        console.error("❌ Error fetching visitor count:", error);
        // Optional: show stale cache if available
        if (cached) {
          console.warn("⚠️ Falling back to stale cached count:", cached.count);
          setCount(cached.count);
        } else {
          setCount("–"); // fallback UI
        }
      });
  }
})();
