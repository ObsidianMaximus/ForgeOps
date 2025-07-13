document.addEventListener("DOMContentLoaded", () => {
  fetch("https://<your-api-gateway-url>/visitor")  // replace with your actual endpoint
    .then(res => res.json())
    .then(data => {
      document.getElementById("visitor-count").textContent = data.count;
    })
    .catch(err => {
      console.error("Visitor count fetch failed:", err);
    });
});
