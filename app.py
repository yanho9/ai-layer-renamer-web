from flask import Flask, request, send_file, jsonify
import openai, os, io, tempfile

# Try to import psd-tools safely
try:
    from psd_tools import PSDImage
    PSD_TOOLS_AVAILABLE = True
except Exception as e:
    PSD_TOOLS_AVAILABLE = False
    print("⚠️ psd-tools not available:", e)

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

    if not PSD_TOOLS_AVAILABLE:
        return jsonify({"error": "psd-tools library not available on server"}), 500

    try:
        psd = PSDImage.open(psd_path)
    except Exception as e:
        return jsonify({"error": f"Failed to open PSD. Likely unsupported format. Details: {str(e)}"}), 500

    renamed_count = 0
    for i, layer in enumerate(psd):
        if not layer.is_group() and layer.is_visible():
            # Try to describe the layer
            desc = None
            try:
                desc = f"Layer {i} | Size: {layer.size}, Kind: {getattr(layer, 'kind', 'unknown')}"
            except Exception:
                pass

            if not desc:
                try:
                    pil_img = layer.topil()
                    desc = f"Layer {i} | Fallback image | Size: {pil_img.size}, Mode: {pil_img.mode}"
                except Exception:
                    desc = f"Layer {i} | No details available"

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
                renamed_count += 1
            except Exception as e:
                print("AI rename error:", e)

    if renamed_count == 0:
        return jsonify({"error": "No layers could be processed. PSD may not be supported."}), 500

    # Save updated PSD
    out_bytes = io.BytesIO()
    try:
        psd.save(out_bytes)
    except Exception as e:
        return jsonify({"error": f"Failed to save PSD after renaming: {str(e)}"}), 500

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

    if not PSD_TOOLS_AVAILABLE:
        return jsonify({"error": "psd-tools library not available on server"}), 500

    try:
        psd = PSDImage.open(psd_path)
    except Exception as e:
        return jsonify({"error": f"Failed to open PSD. Likely unsupported format. Details: {str(e)}"}), 500

    info = []
    for i, l in enumerate(psd):
        try:
            info.append({
                "index": i,
                "name": l.name,
                "kind": getattr(l, 'kind', 'unknown'),
                "size": getattr(l, 'size', None)
            })
        except Exception as e:
            info.append({"index": i, "name": "Unknown", "kind": "error", "error": str(e)})

    if not info:
        return jsonify({"error": "PSD opened but no layers found"}), 500

    return jsonify(info)
