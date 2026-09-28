/*
STUDENT CODE MAP
PURPOSE: Read browser input, send it to Flask, and display Flask's result.
NO AI LOGIC: RAG, Qwen, validation, database work, and file creation stay in Python.
CONNECTIONS: Chat -> /api/chat; Create -> /api/generate.
EDIT HERE: Browser-only interactions belong in this file.
*/

// No library is imported. Built-in browser APIs are enough.
document.addEventListener("DOMContentLoaded", setupPage);

// PURPOSE: Connect page buttons/forms after HTML loads.
// CONNECTS: browser load -> sendChat(), createArtifact(), showMode(), newChat().
function setupPage() {
    var chatForm = document.getElementById("chat-form");
    var creatorForm = document.getElementById("creator-form");
    if (chatForm) {
        chatForm.addEventListener("submit", sendChat);
        document.getElementById("new-chat").addEventListener("click", newChat);
        document.getElementById("chat-mode-button").addEventListener("click", function () { showMode(true); });
        document.getElementById("creator-mode-button").addEventListener("click", function () { showMode(false); });
    }
    if (creatorForm) {
        creatorForm.addEventListener("submit", createArtifact);
    }
}

// PURPOSE: Put Python/browser text into one HTML element.
// CONNECTS: sendChat(), showResult(), showError() -> visible DOM.
function setText(id, value) {
    var element = document.getElementById(id);
    if (element) element.textContent = value;
}

// PURPOSE: Transport form data to Flask and return its JSON result.
// CONNECTS: sendChat()/createArtifact() -> fetch() -> Python API.
// IMPORTANT: This function does not calculate the AI result.
async function postForm(url, formData) {
    try {
        var response = await fetch(url, { method: "POST", body: formData });
        return { ok: response.ok, data: await response.json() };
    } catch (error) {
        return { ok: false, data: { message: "Could not connect to Flask. Check the server terminal." } };
    }
}

// PURPOSE: Show either Chat or Create without changing backend state.
// CONNECTS: mode buttons in app.html -> this function.
function showMode(showChat) {
    document.getElementById("chat-mode").hidden = !showChat;
    document.getElementById("creator-mode").hidden = showChat;
    document.getElementById("chat-mode-button").classList.toggle("active", showChat);
    document.getElementById("creator-mode-button").classList.toggle("active", !showChat);
}

// PURPOSE: Send one chat message to Python and display the returned answer.
// CONNECTS: app.html -> sendChat() -> /api/chat -> chat_api.py -> rag.py -> ai.py.
// EDIT HERE: Change browser-side chat collection/display only.
async function sendChat(event) {
    event.preventDefault();
    var input = document.getElementById("chat-input");
    var button = document.getElementById("send-chat");
    var message = input.value.trim();
    if (!message) return;

    addMessage("user", message);
    input.value = "";
    button.disabled = true;
    setText("chat-status", "Python is searching the knowledge base and asking Qwen…");

    var form = new FormData();
    form.append("message", message);
    var result = await postForm("/api/chat", form);
    if (result.ok && result.data.success) {
        addMessage("assistant", result.data.reply || "No answer was returned.");
        setText("chat-status", result.data.rag_used ? "Answer ready · RAG used." : "Answer ready.");
    } else {
        setText("chat-status", result.data.message || "Chat failed.");
    }
    button.disabled = false;
    input.focus();
}

// PURPOSE: Add one user/AI message to the visible chat area.
// CONNECTS: sendChat() -> this function -> #chat-messages in app.html.
function addMessage(role, message) {
    var area = document.getElementById("chat-messages");
    var card = document.createElement("article");
    var label = document.createElement("div");
    var text = document.createElement("div");
    card.className = "chat-message " + role;
    label.className = "chat-label";
    text.className = "chat-content";
    label.textContent = role === "user" ? "You" : "AI";
    text.textContent = message;
    card.appendChild(label);
    card.appendChild(text);
    area.appendChild(card);
    area.scrollTop = area.scrollHeight;
}

// PURPOSE: Clear visible messages only; no history is stored in SQLite.
// CONNECTS: New Chat button -> this function.
function newChat() {
    document.getElementById("chat-messages").innerHTML = "";
    setText("chat-status", "New chat started.");
    document.getElementById("chat-input").focus();
}

// PURPOSE: Send a document request and file type to Python.
// CONNECTS: app.html -> createArtifact() -> /api/generate -> document_api.py.
// IMPORTANT: Python performs RAG, Qwen, validation, retry, and file creation.
async function createArtifact(event) {
    event.preventDefault();
    var prompt = document.getElementById("prompt").value.trim();
    var type = document.getElementById("artifact-type").value;
    var button = document.getElementById("generate-button");
    if (!prompt) {
        setText("creator-status", "Please describe what you want to create.");
        return;
    }

    button.disabled = true;
    document.getElementById("result-card").hidden = true;
    document.getElementById("error-card").hidden = true;
    setText("creator-status", "Python is running RAG → Qwen → validation → file…");

    var form = new FormData();
    form.append("prompt", prompt);
    form.append("artifact_type", type);
    var result = await postForm("/api/generate", form);
    if (result.ok && result.data.success) showResult(result.data);
    else showError(result.data);
    button.disabled = false;
}

// PURPOSE: Display Python's successful generation result and download link.
// CONNECTS: createArtifact() -> document_api.py JSON -> this function.
function showResult(data) {
    document.getElementById("result-card").hidden = false;
    setText("result-title", data.title || "Generation complete");
    setText("result-model", data.model || "Local Qwen");
    setText("result-validation", data.validation || "Passed");
    setText("result-artifact", String(data.artifact_type || "file").toUpperCase());
    document.getElementById("content-preview").value = data.content_preview || "";

    var stages = document.getElementById("generation-stages");
    stages.textContent = "";
    var title = document.createElement("strong");
    title.textContent = "Python pipeline";
    stages.appendChild(title);
    for (var i = 0; i < (data.stages || []).length; i += 1) {
        var row = document.createElement("div");
        row.textContent = data.stages[i].stage + ": " + data.stages[i].message;
        stages.appendChild(row);
    }

    var link = document.getElementById("download-link");
    link.href = data.artifact_url;
    link.textContent = "Download " + String(data.artifact_type).toUpperCase();
    setText("creator-status", "Generation complete. Your file is ready.");
}

// PURPOSE: Show the error information that Python returned.
// CONNECTS: createArtifact() -> Flask error JSON -> this function.
function showError(data) {
    document.getElementById("error-card").hidden = false;
    setText("error-stage", data.stage || "generation");
    setText("error-message", data.message || "The server could not finish the request.");
    setText("error-suggestion", data.suggestion || "Check the server and try again.");
    setText("creator-status", "Generation failed.");
}
