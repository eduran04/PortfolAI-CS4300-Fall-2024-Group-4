const input = document.getElementById("chat-input");
const send = document.getElementById("chat-send");
const historyDiv = document.getElementById("chat-history");
const chatBar = document.getElementById("chat-bar");

let isWaiting = false;

// Append message with animation
function appendMessage(role, text) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${role}`;
  msgDiv.innerHTML = text.replace(/\n/g, "<br>");

  historyDiv.appendChild(msgDiv);

  // Allow animation to trigger smoothly
  setTimeout(() => (msgDiv.style.opacity = 1), 50);

  historyDiv.scrollTop = historyDiv.scrollHeight;
}

// Typing animation
function showTypingAnimation() {
  const dots = document.createElement("div");
  dots.className = "typing";
  dots.innerHTML = "<span></span><span></span><span></span>";
  historyDiv.appendChild(dots);
  historyDiv.scrollTop = historyDiv.scrollHeight;
  return dots;
}

// Send message to backend
async function sendMessage() {
  const msg = input.value.trim();
  if (!msg || isWaiting) return;

  input.value = "";
  historyDiv.style.display = "block";

  appendMessage("user", msg);
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
  } catch {
    typingDots.remove();
    appendMessage("bot", "⚠️ Error contacting the assistant.");
  } finally {
    isWaiting = false;
  }
}

// Input handling
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
send.addEventListener("click", sendMessage);
chatBar.addEventListener("click", () => input.focus());
