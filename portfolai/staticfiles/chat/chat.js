// --- Elements --- //
const input = document.getElementById("chat-input");
const send = document.getElementById("chat-send");
const historyDiv = document.getElementById("chat-history");
const chatHeader = document.getElementById("chat-header");
const closeBtn = document.getElementById("chat-close");
const clearBtn = document.getElementById("chat-clear");
const chatIcon = document.getElementById("chat-icon");

let isWaiting = false;
let chatOpen = false;

// --- Append Message --- //
function appendMessage(role, text) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${role}`;
  msgDiv.textContent = text;
  historyDiv.appendChild(msgDiv);

  setTimeout(() => {
    msgDiv.style.opacity = 1;
    msgDiv.style.transform = "translateY(0)";
  }, 50);

  historyDiv.scrollTop = historyDiv.scrollHeight;
}

// --- Typing Animation --- //
function showTypingAnimation() {
  const dots = document.createElement("div");
  dots.className = "typing";
  dots.innerHTML = "<span></span><span></span><span></span>";
  historyDiv.appendChild(dots);
  historyDiv.scrollTop = historyDiv.scrollHeight;
  return dots;
}

// --- Expand Chat --- //
function showChatHistory() {
  if (chatOpen) return;
  chatHeader.classList.add("show");
  historyDiv.classList.add("show");
  chatHeader.classList.remove("hidden");
  historyDiv.classList.remove("hidden");
  chatOpen = true;

  // Swap to active icon + pulse
  if (chatIcon) {
    const activeSrc = chatIcon.dataset.active;
    if (activeSrc) chatIcon.src = activeSrc;
    chatIcon.classList.add("active");
  }
}

// --- Collapse Chat --- //
function hideChatHistory() {
  chatHeader.classList.remove("show");
  historyDiv.classList.remove("show");
  chatOpen = false;

  setTimeout(() => {
    chatHeader.classList.add("hidden");
    historyDiv.classList.add("hidden");
  }, 300);

  // Swap to idle icon
  if (chatIcon) {
    const idleSrc = chatIcon.dataset.idle;
    if (idleSrc) chatIcon.src = idleSrc;
    chatIcon.classList.remove("active");
  }
}

// --- Send Message --- //
async function sendMessage() {
  const msg = input.value.trim();
  if (!msg || isWaiting) return;

  showChatHistory(); // expand on send
  appendMessage("user", msg);
  input.value = "";
  isWaiting = true;

  const typingDots = showTypingAnimation();

  try {
    const res = await fetch("/api/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg }),
    });

    const data = await res.json();
    typingDots.remove();

    if (data.response) appendMessage("bot", data.response);
    else appendMessage("bot", "Sorry, something went wrong.");
  } catch (err) {
    console.error("Chat error:", err);
    typingDots.remove();
    appendMessage("bot", "Error contacting the assistant.");
  } finally {
    isWaiting = false;
  }
}

// --- Clear Chat --- //
async function clearChat() {
  try {
    const res = await fetch("/api/chat/clear/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    const data = await res.json();
    if (data.success) {
      // Clear local chat history display
      historyDiv.innerHTML = "";
      appendMessage("bot", "Chat history cleared. How can I help you?");
    }
  } catch (err) {
    console.error("Clear chat error:", err);
  }
}

// --- Event Listeners --- //
input.addEventListener("focus", showChatHistory);
input.addEventListener("input", showChatHistory);
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
send.addEventListener("click", sendMessage);
closeBtn.addEventListener("click", hideChatHistory);
if (clearBtn) clearBtn.addEventListener("click", clearChat);
