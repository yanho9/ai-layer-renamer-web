# AI Layer Renamer (Web MVP)

A minimal web app that renames Photoshop PSD layers using AI.

## Backend (Render)
1. Go to [Render](https://render.com) → New → Web Service.
2. Connect this repo, set **root directory** = `backend`.
3. Build command:
   ```
   pip install -r requirements.txt
   ```
4. Start command:
   ```
   gunicorn app:app
   ```
5. Add environment variable:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
6. Deploy → you’ll get a URL like:
   ```
   https://ai-layer-renamer.onrender.com
   ```

Test backend:
```
https://ai-layer-renamer.onrender.com/ping
```
Should return `{"status":"ok"}`.

## Frontend (GitHub Pages)
1. Enable GitHub Pages in repo settings, source = `/frontend` folder.
2. Edit `frontend/script.js` → replace backend URL with your Render URL.
3. Visit your GitHub Pages link → upload a PSD → get a renamed PSD 🎉
