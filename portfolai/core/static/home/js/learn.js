/***************************************************************
 *  PortfolAI - Learn Module (Refactored)
 *  - Encapsulated in window.LearnUI namespace
 *  - Event delegation added
 *  - Security improvements (no unsafe innerHTML)
 *  - Better fetch error handling
 *  - More readable structure
 ***************************************************************/

console.log("[LearnUI] Script loaded...");

/* ============================================================
   LEARN TOPIC DATA
   ============================================================ */

const learnTopics = {
  "Stock Market Basics": {
    subtopics: {
      "What Is a Stock?": [
        "A stock represents ownership in a company...",
        "Stocks matter because they let everyday people share..."
      ],
      "ETFs Explained": [
        "An ETF is a basket of stocks...",
        "ETFs are important because they provide diversification..."
      ],
      "What Makes Prices Move?": [
        "Stock prices move from supply and demand...",
        "Economic news, earnings, and interest rates impact prices..."
      ]
    }
  },
  "Reading Stock Charts": {
    subtopics: {
      "Candlesticks": [
        "Candlesticks represent open, high, low, close prices...",
        "They help visualize short-term sentiment..."
      ],
      "Volume": [
        "Volume measures how many shares traded...",
        "High volume confirms strong price moves..."
      ],
      "Support & Resistance": [
        "Support is a price level where the stock tends to stop falling...",
        "Knowing these levels helps identify entries and exits..."
      ]
    }
  },
  // ... (other topics unchanged)
};

/* ============================================================
   MAIN LOGIC — NAMESPACE
   ============================================================ */

window.LearnUI = (function () {
  let catTrack, pillRow, activeTopicLabel;
  let overlay, titleEl, subtopicEl, slideEl, counterEl;
  let learnCloseBtn, learnNextBtn, learnPrevBtn;
  let askAiBtn, aiStatusEl, aiResponseEl;
  let catPrevBtn, catNextBtn;

  let currentTopic = Object.keys(learnTopics)[0];
  let currentSubtopic = null;
  let currentSlideIndex = 0;

  /* -------------------------
     DOM READY
     ------------------------- */
  document.addEventListener("DOMContentLoaded", () => {
    console.log("[LearnUI] DOM loaded — initializing...");

    catTrack = document.getElementById("learnCatTrack");
    pillRow = document.getElementById("learnPillRow");
    activeTopicLabel = document.getElementById("learnActiveTopicLabel");

    overlay = document.getElementById("learnOverlay");
    titleEl = document.getElementById("learnTitle");
    subtopicEl = document.getElementById("learnSubtopic");
    slideEl = document.getElementById("learnSlide");
    counterEl = document.getElementById("learnCounter");

    learnCloseBtn = document.getElementById("learnClose");
    learnNextBtn = document.getElementById("learnNext");
    learnPrevBtn = document.getElementById("learnPrev");

    askAiBtn = document.getElementById("learnAskAiBtn");
    aiStatusEl = document.getElementById("learnAiStatus");
    aiResponseEl = document.getElementById("learnAiResponse");

    catPrevBtn = document.getElementById("learnCatPrev");
    catNextBtn = document.getElementById("learnCatNext");

    if (!catTrack || !pillRow) {
      console.warn("[LearnUI] Learn section not found — skipping init.");
      return;
    }

    init();
  });

  /* ============================================================
     INITIALIZATION
     ============================================================ */

  function init() {
    console.log("[LearnUI] Full initialization...");

    setupTopicCardsDelegated();
    setActiveTopic(currentTopic);

    if (catPrevBtn) {
      catPrevBtn.addEventListener("click", () =>
        catTrack.scrollBy({ left: -260, behavior: "smooth" })
      );
    }

    if (catNextBtn) {
      catNextBtn.addEventListener("click", () =>
        catTrack.scrollBy({ left: 260, behavior: "smooth" })
      );
    }

    if (learnCloseBtn) learnCloseBtn.addEventListener("click", closeOverlay);
    if (learnNextBtn) learnNextBtn.addEventListener("click", nextSlide);
    if (learnPrevBtn) learnPrevBtn.addEventListener("click", prevSlide);

    document.addEventListener("keydown", (e) => {
      if (overlay?.classList.contains("hidden")) return;

      if (e.key === "Escape") closeOverlay();
      if (e.key === "ArrowRight") nextSlide();
      if (e.key === "ArrowLeft") prevSlide();
    });

    if (askAiBtn) askAiBtn.addEventListener("click", askAiForCurrent);

    console.log("[LearnUI] Initialization complete.");
  }

  /* ============================================================
     TOPICS — EVENT DELEGATION
     ============================================================ */

  function setupTopicCardsDelegated() {
    catTrack.addEventListener("click", (event) => {
      const card = event.target.closest(".learn-topic-card");
      if (!card) return;

      const topic = card.dataset.topic;
      if (topic) setActiveTopic(topic);
    });
  }

  function setActiveTopic(topic) {
    currentTopic = topic;
    activeTopicLabel.textContent = topic;

    catTrack.querySelectorAll(".learn-topic-card").forEach((c) => {
      c.classList.toggle("active", c.dataset.topic === topic);
    });

    buildSubtopicPills(topic);
  }

  function buildSubtopicPills(topic) {
    pillRow.textContent = ""; // safer than innerHTML

    const subtopics = learnTopics[topic].subtopics;

    Object.keys(subtopics).forEach((subName, index) => {
      const pill = document.createElement("button");
      pill.className = "learn-pill";
      pill.textContent = subName;

      pill.addEventListener("click", () => {
        pillRow.querySelectorAll(".learn-pill")
               .forEach((p) => p.classList.remove("active"));

        pill.classList.add("active");
        openOverlay(topic, subName);
      });

      pillRow.appendChild(pill);

      if (index === 0) currentSubtopic = subName;
    });
  }

  /* ============================================================
     OVERLAY + SLIDES
     ============================================================ */

  function openOverlay(topic, subtopic) {
    currentTopic = topic;
    currentSubtopic = subtopic;
    currentSlideIndex = 0;

    titleEl.textContent = topic;
    subtopicEl.textContent = subtopic;

    aiStatusEl.textContent = "";
    aiResponseEl.textContent = "";

    updateSlide();

    overlay.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  }

  function closeOverlay() {
    overlay.classList.add("hidden");
    document.body.style.overflow = "";
  }

  function updateSlide() {
    const slides = learnTopics[currentTopic].subtopics[currentSubtopic];
    slideEl.textContent = slides[currentSlideIndex];
    counterEl.textContent = `${currentSlideIndex + 1} / ${slides.length}`;
  }

  function nextSlide() {
    const slides = learnTopics[currentTopic].subtopics[currentSubtopic];
    if (currentSlideIndex < slides.length - 1) {
      currentSlideIndex++;
      updateSlide();
    }
  }

  function prevSlide() {
    if (currentSlideIndex > 0) {
      currentSlideIndex--;
      updateSlide();
    }
  }

  /* ============================================================
     AI BUTTON — more secure, validated, safer error handling
     ============================================================ */

  async function askAiForCurrent() {
    aiStatusEl.textContent = "Asking AI assistant...";
    aiResponseEl.textContent = "";

    // Validate inputs
    if (!currentTopic || !currentSubtopic) {
      aiStatusEl.textContent = "Missing topic/subtopic.";
      return;
    }

    const prompt = `Explain the topic "${currentTopic} - ${currentSubtopic}" 
in simple terms for a beginner investor.`;

    try {
      const response = await fetch("/api/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: prompt })
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const data = await response.json();
      aiStatusEl.textContent = "AI explanation:";
      aiResponseEl.textContent =
        data?.response || "AI was unable to provide a response.";

    } catch (error) {
      console.error("[LearnUI] AI request error:", error);
      aiStatusEl.textContent = "Error contacting AI assistant.";
      aiResponseEl.textContent = "Please try again later.";
    }
  }

  /* Public API */
  return { openOverlay, closeOverlay };

})();
