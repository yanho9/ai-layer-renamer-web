document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files.length) return;

  document.getElementById("status").textContent = "Processing...";

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const res = await fetch("https://ai-layer-renamer-web.onrender.com/rename", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error("Request failed");

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "renamed.psd";
    document.body.appendChild(a);
    a.click();
    a.remove();

    document.getElementById("status").textContent = "✅ Done! File downloaded.";
  } catch (err) {
    document.getElementById("status").textContent = "❌ Error: " + err.message;
  }
});
