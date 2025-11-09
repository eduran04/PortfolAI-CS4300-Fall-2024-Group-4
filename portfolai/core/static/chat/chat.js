// --- Elements --- //
const input = document.getElementById("chat-input");
const send = document.getElementById("chat-send");
const historyDiv = document.getElementById("chat-history");
const chatHeader = document.getElementById("chat-header");
const closeBtn = document.getElementById("chat-close");
const chatIcon = document.getElementById("chat-icon");

let isWaiting = false;
let chatOpen = false;

// --- Get CSRF Token --- //
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

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

// --- Get Current Stock Symbol --- //
function getCurrentStockSymbol() {
  const searchInput = document.getElementById("stock-search");
  if (searchInput && searchInput.value) {
    return searchInput.value.toUpperCase().trim();
  }
  return null;
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
    // Get current stock symbol from the search input
    const currentStock = getCurrentStockSymbol();
    
    const requestBody = { message: msg };
    if (currentStock) {
      requestBody.current_stock = currentStock;
    }

    const res = await fetch("/api/chat/", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken") || ""
      },
      credentials: "same-origin",
      body: JSON.stringify(requestBody),
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

// --- Event Listeners --- //
input.addEventListener("focus", showChatHistory);
input.addEventListener("input", showChatHistory);
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
send.addEventListener("click", sendMessage);
closeBtn.addEventListener("click", hideChatHistory);
