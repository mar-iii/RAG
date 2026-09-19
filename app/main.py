from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.dashboard import router as dashboard_router
from app.api.v1.router import api_router
from app.config import settings

app = FastAPI(title=settings.project_name)
app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(dashboard_router)


@app.get("/", response_class=HTMLResponse, tags=["dashboard"])
def dashboard() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Enterprise RAG Dashboard</title>
  <style>
    :root { font-family: system-ui, sans-serif; color: #172033; background: #f4f7fb; }
    body { max-width: 900px; margin: 0 auto; padding: 32px 18px; }
    main { display: grid; gap: 18px; }
    section { background: white; border: 1px solid #dce3ef; border-radius: 12px; padding: 20px; }
    h1 { margin-top: 0; } h2 { margin-top: 0; font-size: 1.15rem; }
    label { display: block; font-weight: 600; margin: 10px 0 6px; }
    input, button { font: inherit; padding: 10px 12px; border-radius: 7px; }
    input { width: 100%; box-sizing: border-box; border: 1px solid #b8c3d4; }
    button { border: 0; color: white; background: #3157c8; cursor: pointer; margin-top: 12px; }
    button:disabled { opacity: .6; cursor: wait; }
    pre, #answer { white-space: pre-wrap; word-break: break-word; }
    .status { margin-top: 12px; color: #42526b; } .error { color: #b42318; }
    li { margin: 8px 0; }
  </style>
</head>
<body>
  <main>
    <h1>Enterprise RAG Dashboard</h1>
    <section>
      <h2>Ingest document</h2>
      <input id="file" type="file" accept=".txt,.md,text/plain,text/markdown">
      <button id="upload">Upload and index</button>
      <div id="upload-status" class="status"></div>
    </section>
    <section>
      <h2>Ask a question</h2>
      <label for="question">Question</label>
      <input id="question" type="text" placeholder="Ask about an indexed document">
      <button id="ask">Ask question</button>
      <div id="query-status" class="status"></div>
      <h3>Answer</h3>
      <div id="answer">No answer yet.</div>
      <h3>Sources</h3>
      <ul id="sources"></ul>
    </section>
  </main>
  <script>
    const setStatus = (id, message, error = false) => {
      const element = document.querySelector(id);
      element.textContent = message;
      element.className = error ? "status error" : "status";
    };
    document.querySelector("#upload").onclick = async () => {
      const file = document.querySelector("#file").files[0];
      if (!file) return setStatus("#upload-status", "Choose a .txt or .md file first.", true);
      const button = document.querySelector("#upload");
      button.disabled = true; setStatus("#upload-status", "Indexing document...");
      try {
        const body = new FormData(); body.append("file", file);
        const response = await fetch("/dashboard/ingest/", {method: "POST", body});
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Upload failed.");
        setStatus("#upload-status", `${data.message} (${data.chunks_indexed} chunks).`);
      } catch (error) { setStatus("#upload-status", error.message, true); }
      finally { button.disabled = false; }
    };
    document.querySelector("#ask").onclick = async () => {
      const question = document.querySelector("#question").value.trim();
      if (!question) return setStatus("#query-status", "Enter a question first.", true);
      const button = document.querySelector("#ask");
      button.disabled = true; setStatus("#query-status", "Searching and generating...");
      try {
        const response = await fetch("/dashboard/query/", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({question, top_k: 3})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Query failed.");
        document.querySelector("#answer").textContent = data.answer;
        document.querySelector("#sources").innerHTML = data.source_documents
          .map(source => `<li><strong>${source.source}</strong><br>${source.content}</li>`)
          .join("");
        setStatus("#query-status", "Done.");
      } catch (error) { setStatus("#query-status", error.message, true); }
      finally { button.disabled = false; }
    };
  </script>
</body>
</html>"""


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "healthy"}
