# AI Layer Renamer (Web MVP)

A minimal web app that renames Photoshop PSD layers using AI.

## Backend (Render)
1. Go to [Render](https://render.com) → New → Web Service.
2. Connect this repo, use root directory = `/` (repo root).
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

Test backend health:
```
https://ai-layer-renamer.onrender.com/ping
```

Test PSD parsing (no AI):
```
POST https://ai-layer-renamer.onrender.com/debug
```

## Frontend (GitHub Pages)
1. Enable GitHub Pages in repo settings, source = `/docs` folder.
2. Edit `docs/script.js` → replace backend URL with your Render URL.
3. Visit your GitHub Pages link → upload a PSD → get a renamed PSD 🎉
