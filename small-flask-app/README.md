# Drawing UI

Run the Flask drawing UI with:

`uv run python small-flask-app/app.py`

The app serves:
- `POST /draw`: accepts the reference image from `drawing_agent.py`
- `GET /draw`: returns the completed user drawing as an image
- `GET /`: browser UI with pen, eraser, clear, and done controls