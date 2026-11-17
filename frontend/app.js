const API_URL = "/api";
let chatHistory = [];

const messagesElement = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");

marked.use({
  breaks: true,
  gfm: true,
});

function renderMarkdown(text) {
  return DOMPurify.sanitize(marked.parse(text));
}

function addMessage(content, role) {
  const element = document.createElement("div");
  element.className = `message ${role}`;
  if (role === "user") {
    element.textContent = content;
  } else {
    element.innerHTML = renderMarkdown(content);
  }
  messagesElement.appendChild(element);
  messagesElement.scrollTop = messagesElement.scrollHeight;
  return element;
}

async function sendMessage(message) {
  const trimmed = message.trim();
  if (!trimmed || sendButton.disabled) return;

  addMessage(trimmed, "user");
  chatHistory.push({ role: "user", content: trimmed });
  input.value = "";
  sendButton.disabled = true;
  const loading = addMessage("AI is thinking...", "assistant loading");

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: trimmed, history: chatHistory.slice(0, -1) }),
    });
    if (!response.ok) throw new Error("Request failed");
    const data = await response.json();
    loading.remove();
    addMessage(data.reply, "assistant");
    chatHistory.push({ role: "assistant", content: data.reply });
  } catch (error) {
    loading.remove();
    addMessage("Sorry, something went wrong. Please try again.", "assistant");
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(input.value);
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll("[data-message]").forEach((button) => {
  button.addEventListener("click", () => sendMessage(button.dataset.message));
});

addMessage("Hello! Ask me about an IELTS word, send me a sentence to correct, or choose an option below.", "assistant");
