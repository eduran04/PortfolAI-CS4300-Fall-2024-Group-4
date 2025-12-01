// Wait for DOM to be fully loaded before initializing chat
document.addEventListener('DOMContentLoaded', function() {
  initializeChat();
});

function initializeChat() {
  // --- Elements --- //
  const input = document.getElementById("chat-input");
  const send = document.getElementById("chat-send");
  const historyDiv = document.getElementById("chat-history");
  const chatHeader = document.getElementById("chat-header");
  const closeBtn = document.getElementById("chat-close");
  const clearBtn = document.getElementById("chat-clear");
  const chatIcon = document.getElementById("chat-icon");
  const chatWidget = document.getElementById("chat-widget");

  // Check if elements exist
  if (!input || !send || !historyDiv || !chatHeader || !closeBtn || !chatIcon || !chatWidget) {
    console.error('Chat widget elements not found');
    return;
  }

  let isWaiting = false;
  let chatOpen = false;

  // --- Position State --- //
  let isExpanded = false;

  // --- Helper: Escape HTML --- //
  function escapeHTML(str) {
    return str.replace(/[&<>"']/g, function(match) {
      switch (match) {
        case "&": return "&amp;";
        case "<": return "&lt;";
        case ">": return "&gt;";
        case '"': return "&quot;";
        case "'": return "&#39;";
        default: return match;
      }
    });
  }

  // --- Format Bot Message --- //
  function formatBotMessage(text) {
    // Escape all HTML in input
    text = escapeHTML(text);
    // Remove trailing colons from bold text
    text = text.replace(/\*\*(.+?)\*\*\s*:/g, '<strong>$1</strong>');

    // Convert remaining **bold** to <strong>
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Convert inline code/values like `$1.85` to styled spans
    text = text.replace(/`([^`]+)`/g, '<span class="chat-value">$1</span>');

    // Split into lines for processing
    const lines = text.split('\n');
    let formatted = '';
    let inOrderedList = false;
    let inUnorderedList = false;
    let listDepth = 0;

    for (let i = 0; i < lines.length; i++) {
      const originalLine = lines[i];
      const trimmedLine = originalLine.trim();
      const indentLevel = originalLine.length - originalLine.trimStart().length;

      // Skip empty lines
      if (!trimmedLine) {
        // Close any open lists
        if (inOrderedList) {
          formatted += '</ol>';
          inOrderedList = false;
          listDepth = 0;
        }
        if (inUnorderedList) {
          formatted += '</ul>';
          inUnorderedList = false;
          listDepth = 0;
        }
        continue;
      }

      // Check for markdown headers (### Header with or without colon)
      const headerMatch = trimmedLine.match(/^###\s+(.+?)(?:\s*:)?\s*$/);
      if (headerMatch) {
        if (inOrderedList) {
          formatted += '</ol>';
          inOrderedList = false;
          listDepth = 0;
        }
        if (inUnorderedList) {
          formatted += '</ul>';
          inUnorderedList = false;
          listDepth = 0;
        }
        formatted += `<h4 class="chat-header">${headerMatch[1]}</h4>`;
        continue;
      }

      // Check for numbered list item (e.g., "1. ", "2. ", etc.)
      const numberedMatch = trimmedLine.match(/^(\d+)\.\s+(.+)$/);
      if (numberedMatch) {
        if (inUnorderedList) {
          formatted += '</ul>';
          inUnorderedList = false;
          listDepth = 0;
        }
        if (!inOrderedList) {
          formatted += '<ol class="chat-list">';
          inOrderedList = true;
          listDepth = indentLevel;
        }
        formatted += `<li>${numberedMatch[2]}</li>`;
        continue;
      }

      // Check for bullet point (- Item)
      const bulletMatch = trimmedLine.match(/^-\s+(.+)$/);
      if (bulletMatch) {
        if (inOrderedList) {
          formatted += '</ol>';
          inOrderedList = false;
          listDepth = 0;
        }
        if (!inUnorderedList || indentLevel !== listDepth) {
          if (inUnorderedList && indentLevel !== listDepth) {
            formatted += '</ul>';
          }
          formatted += '<ul class="chat-list">';
          inUnorderedList = true;
          listDepth = indentLevel;
        }

        // Handle bold text within bullet points (remove colons)
        let content = bulletMatch[1];
        content = content.replace(/^(.+?):\s*/, '<strong>$1</strong> ');

        formatted += `<li>${content}</li>`;
        continue;
      }

      // Check for indented plain text that looks like a list item (e.g., "    Name Apple Inc.")
      // This handles indented key-value pairs or list items
      if (indentLevel >= 4) {
        const keyValueMatch = trimmedLine.match(/^([^:]+?):\s*(.+)$/);
        if (keyValueMatch) {
          if (!inUnorderedList || indentLevel !== listDepth) {
            if (inOrderedList) {
              formatted += '</ol>';
              inOrderedList = false;
            }
            if (inUnorderedList && indentLevel !== listDepth) {
              formatted += '</ul>';
            }
            formatted += '<ul class="chat-list chat-nested">';
            inUnorderedList = true;
            listDepth = indentLevel;
          }
          formatted += `<li><strong>${keyValueMatch[1]}</strong> ${keyValueMatch[2]}</li>`;
          continue;
        }
      }

      // Regular paragraph - close lists if we're not in a list context
      if (indentLevel === 0 || (inOrderedList && indentLevel < listDepth) || (inUnorderedList && indentLevel < listDepth)) {
        if (inOrderedList) {
          formatted += '</ol>';
          inOrderedList = false;
          listDepth = 0;
        }
        if (inUnorderedList) {
          formatted += '</ul>';
          inUnorderedList = false;
          listDepth = 0;
        }
      }

      formatted += `<p>${trimmedLine}</p>`;
    }

    // Close any remaining open lists
    if (inOrderedList) {
      formatted += '</ol>';
    }
    if (inUnorderedList) {
      formatted += '</ul>';
    }

    return formatted;
  }

  // --- Append Message --- //
  function appendMessage(role, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role}`;
    
    // Use textContent for user messages (safe), innerHTML for bot messages (formatted)
    if (role === "bot") {
      msgDiv.innerHTML = formatBotMessage(text);
    } else {
      msgDiv.textContent = text;
    }
    
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

  // --- Widget State Management --- //
  function expandWidget() {
    if (isExpanded) return;
    chatWidget.classList.remove("minimized", "position-left");
    chatWidget.classList.add("expanded");
    isExpanded = true;
  }

  function collapseWidget() {
    chatWidget.classList.remove("expanded");
    chatWidget.classList.add("minimized", "position-left");
    isExpanded = false;
  }

  // --- Initialize Widget State --- //
  function initializeWidget() {
    // Start in minimized state on the left
    collapseWidget();
  }

  // --- Expand Chat --- //
  function showChatHistory() {
    if (chatOpen) return;
    
    // Expand to center
    expandWidget();
    
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

    // Collapse to bottom-left
    collapseWidget();

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

  // --- Chat Icon Click to Expand --- //
  chatIcon.addEventListener("click", () => {
    if (!chatOpen) {
      showChatHistory();
    }
  });

  // --- Initialize --- //
  initializeWidget();
}
