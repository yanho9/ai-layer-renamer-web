from flask import Flask, request, send_file, jsonify
from psd_tools import PSDImage
import openai, os, io, tempfile

app = Flask(__name__)

# Load API key from environment (set this in Render dashboard)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"}), 200

@app.route("/rename", methods=["POST"])
def rename_layers():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    # Save uploaded PSD to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".psd") as tmp:
        file.save(tmp.name)
        psd_path = tmp.name

    try:
        psd = PSDImage.open(psd_path)
    except Exception as e:
        return jsonify({"error": f"Failed to load PSD: {str(e)}"}), 500

    for i, layer in enumerate(psd):
        if not layer.is_group() and layer.is_visible():
            desc = None
            try:
                # Try metadata description
                desc = f"Layer {i} | Size: {layer.size}, Kind: {getattr(layer, 'kind', 'unknown')}"
            except Exception:
                pass

            if not desc:
                try:
                    # Fallback: rasterize to PIL image
                    pil_img = layer.topil()
                    desc = f"Layer {i} | Image fallback | Size: {pil_img.size}, Mode: {pil_img.mode}"
                except Exception:
                    desc = f"Layer {i} | Could not extract details"

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You generate short, descriptive names for Photoshop layers."},
                        {"role": "user", "content": desc}
                    ]
                )
                new_name = response["choices"][0]["message"]["content"].strip()
                layer.name = new_name
            except Exception as e:
                print("AI rename error:", e)

    out_bytes = io.BytesIO()
    psd.save(out_bytes)
    out_bytes.seek(0)

    return send_file(out_bytes, as_attachment=True, download_name="renamed.psd")

@app.route("/debug", methods=["POST"])
def debug_layers():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".psd") as tmp:
        file.save(tmp.name)
        psd_path = tmp.name

    try:
        psd = PSDImage.open(psd_path)
        info = []
        for i, l in enumerate(psd):
            try:
                info.append({
                    "index": i,
                    "name": l.name,
                    "kind": getattr(l, 'kind', 'unknown'),
                    "size": getattr(l, 'size', None)
                })
            except Exception:
                info.append({"index": i, "name": "Unknown", "kind": "error"})
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
