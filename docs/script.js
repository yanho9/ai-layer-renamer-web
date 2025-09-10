document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("fileInput");
  const debugMode = document.getElementById("debugToggle").checked;
  const statusEl = document.getElementById("status");
  const debugEl = document.getElementById("debugOutput");

  if (!fileInput.files.length) {
    statusEl.textContent = "❌ Please select a PSD file first.";
    return;
  }

  statusEl.textContent = "Processing...";
  debugEl.textContent = "";

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const endpoint = debugMode
      ? "https://ai-layer-renamer-web.onrender.com/debug"
      : "https://ai-layer-renamer-web.onrender.com/rename";

    const res = await fetch(endpoint, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error("Request failed with " + res.status);

    if (debugMode) {
      // Show JSON of layer info
      const json = await res.json();
      debugEl.textContent = JSON.stringify(json, null, 2);
      statusEl.textContent = "✅ Debug info loaded!";
    } else {
      // Download renamed PSD
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "renamed.psd";
      document.body.appendChild(a);
      a.click();
      a.remove();
      statusEl.textContent = "✅ Done! File downloaded.";
    }
  } catch (err) {
    statusEl.textContent = "❌ Error: " + err.message;
  }
});
