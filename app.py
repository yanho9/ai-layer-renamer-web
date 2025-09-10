from flask import Flask, request, send_file, jsonify
import openai, os, io, tempfile
from psd_tools.psd.image import PSDImage  # pillow-psd import
from PIL import Image

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
        return jsonify({"error": f"Failed to open PSD with pillow-psd: {str(e)}"}), 500

    renamed_layers = []
    new_images = []

    for i, layer in enumerate(psd.layers):
        try:
            if not layer.is_visible():
                continue

            pil_img = layer.as_PIL()
            desc = f"Layer {i} | Size: {pil_img.size}, Mode: {pil_img.mode}"

            # Ask AI for a name
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You generate short, descriptive names for Photoshop layers."},
                        {"role": "user", "content": desc}
                    ]
                )
                new_name = response["choices"][0]["message"]["content"].strip()
            except Exception:
                new_name = f"Layer_{i}"

            renamed_layers.append({"index": i, "name": new_name})
            new_images.append(pil_img)

        except Exception as e:
            renamed_layers.append({"index": i, "name": f"ErrorLayer_{i}", "error": str(e)})

    if not new_images:
        return jsonify({"error": "No layers processed"}), 500

    # Rebuild new PSD-like file (flattened stack of images into one PSD)
    out_bytes = io.BytesIO()
    try:
        base = Image.new("RGBA", psd.size, (255, 255, 255, 0))
        for img in new_images:
            base.alpha_composite(img.convert("RGBA"))
        base.save(out_bytes, format="PSD")
    except Exception as e:
        return jsonify({"error": f"Failed to save renamed PSD: {str(e)}"}), 500

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
    except Exception as e:
        return jsonify({"error": f"Failed to open PSD with pillow-psd: {str(e)}"}), 500

    info = []
    for i, layer in enumerate(psd.layers):
        try:
            img = layer.as_PIL()
            info.append({
                "index": i,
                "size": img.size,
                "mode": img.mode,
                "visible": layer.is_visible()
            })
        except Exception as e:
            info.append({"index": i, "error": str(e)})

    return jsonify(info)
