/***************************************************************
 *  PortfolAI - Learn Module (Bundled)
 *  - Includes learnTopics
 *  - Encapsulated in window.LearnUI namespace
 *  - Safe initialization after DOM load
 *  - Zero conflicts with chatbot or other scripts
 ***************************************************************/

console.log("[LearnUI] Script loaded...");

/* ============================================================
   LEARN TOPIC DATA (FULL DATASET)
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

  "Company Fundamentals": {
    subtopics: {
      "P/E Ratio": [
        "The price-to-earnings ratio compares price to earnings...",
        "High P/E = optimism, low P/E = possible undervaluation..."
      ],
      "Revenue & Profit": [
        "Revenue is all money earned; profit is what's left...",
        "Growing revenues signal strong business performance..."
      ],
      "Cash Flow": [
        "Cash flow shows real cash coming in/out...",
        "Investors watch cash flow because companies need real liquidity..."
      ]
    }
  },

  "How to Analyze a Stock": {
    subtopics: {
      "Understand the Business": [
        "Know the business model before investing...",
        "Understanding reduces risk and increases confidence..."
      ],
      "Competitive Advantage": [
        "A moat is an edge against competitors...",
        "Stronger moats = more durable long-term performance..."
      ],
      "Valuation Basics": [
        "Valuation determines if a stock is expensive or cheap...",
        "Buying undervalued companies improves long-term returns..."
      ]
    }
  },

  "Building a Portfolio": {
    subtopics: {
      "Diversification": [
        "Diversification spreads risk across assets...",
        "It protects against major losses..."
      ],
      "How Many Stocks?": [
        "New investors start with a few stocks or ETFs...",
        "Too many becomes hard to manage..."
      ],
      "Sample Portfolios": [
        "Example: 60% market ETF, 20% growth, 20% bonds...",
        "Allocation matters more than individual stock picks..."
      ]
    }
  },

  "Beginner Mistakes": {
    subtopics: {
      "FOMO & Hype": [
        "FOMO causes investors to chase rising stocks...",
        "Chasing hype often leads to losses..."
      ],
      "Overtrading": [
        "Overtrading increases fees and risk...",
        "Long-term investing usually outperforms constant trading..."
      ],
      "No Plan": [
        "Investing without a plan makes panic likely...",
        "A plan keeps decisions clear and disciplined..."
      ]
    }
  },

  "Understanding Market News": {
    subtopics: {
      "Economic Reports": [
        "CPI, unemployment, etc. affect markets...",
        "They change expectations for growth and rates..."
      ],
      "Earnings Season": [
        "Companies release earnings every quarter...",
        "Expectations vs reality drives stock reactions..."
      ],
      "Analyst Ratings": [
        "Analysts issue Buy/Hold/Sell ratings...",
        "Useful input but shouldn't be relied on alone..."
      ]
    }
  },

  "Investing Styles": {
    subtopics: {
      "Growth Investing": [
        "Growth focuses on companies expanding quickly...",
        "High upside but more volatility..."
      ],
      "Value Investing": [
        "Value looks for undervalued companies...",
        "Buying discounts improves long-term performance..."
      ],
      "Dividend Investing": [
        "Dividend stocks pay recurring income...",
        "Helps stabilize portfolios..."
      ]
    }
  },

  "Tools & Resources": {
    subtopics: {
      "Research Platforms": [
        "Yahoo Finance, TradingView, Finviz...",
        "Great for screeners and charts..."
      ],
      "Glossaries & Education": [
        "Glossaries teach financial terms...",
        "Understanding jargon improves confidence..."
      ],
      "Official Sources": [
        "SEC filings provide verified company data...",
        "Most reliable source for serious investors..."
      ]
    }
  }
};

/* ============================================================
   MAIN UI LOGIC (Namespace)
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
     INIT after DOM Ready
     ------------------------- */
  document.addEventListener("DOMContentLoaded", () => {
    console.log("[LearnUI] DOM loaded — initializing...");

    // Get all elements *after* DOM is ready
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

    // If Learn section is not present → abort safely
    if (!catTrack || !pillRow) {
      console.warn("[LearnUI] Learn section NOT found on page — skipping.");
      return;
    }

    init();
  });

  /* ============================================================
     INITIALIZATION
     ============================================================ */

  function init() {
    console.log("[LearnUI] Begin full initialization...");

    setupTopicCards();
    setActiveTopic(currentTopic);

    if (catPrevBtn) catPrevBtn.addEventListener("click", () => {
      catTrack.scrollBy({ left: -260, behavior: "smooth" });
    });

    if (catNextBtn) catNextBtn.addEventListener("click", () => {
      catTrack.scrollBy({ left: 260, behavior: "smooth" });
    });

    if (learnCloseBtn) learnCloseBtn.addEventListener("click", closeOverlay);
    if (learnNextBtn) learnNextBtn.addEventListener("click", nextSlide);
    if (learnPrevBtn) learnPrevBtn.addEventListener("click", prevSlide);

    document.addEventListener("keydown", (e) => {
      if (!overlay || overlay.classList.contains("hidden")) return;
      if (e.key === "Escape") closeOverlay();
      if (e.key === "ArrowRight") nextSlide();
      if (e.key === "ArrowLeft") prevSlide();
    });

    if (askAiBtn) askAiBtn.addEventListener("click", askAiForCurrent);

    console.log("[LearnUI] Initialization complete.");
  }

  /* ============================================================
     TOPIC + SUBTOPICS
     ============================================================ */

  function setupTopicCards() {
    const cards = catTrack.querySelectorAll(".learn-topic-card");
    cards.forEach((card) =>
      card.addEventListener("click", () => setActiveTopic(card.dataset.topic))
    );
  }

  function setActiveTopic(topic) {
    currentTopic = topic;
    activeTopicLabel.textContent = topic;

    const cards = catTrack.querySelectorAll(".learn-topic-card");
    cards.forEach((c) =>
      c.classList.toggle("active", c.dataset.topic === topic)
    );

    buildSubtopicPills(topic);
  }

  function buildSubtopicPills(topic) {
    pillRow.innerHTML = "";

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
     AI BUTTON
     ============================================================ */

  async function askAiForCurrent() {
    aiStatusEl.textContent = "Asking AI assistant...";
    aiResponseEl.textContent = "";

    const prompt = `Explain the topic "${currentTopic} - ${currentSubtopic}" in simple terms for a beginner investor.`;

    try {
      const res = await fetch("/api/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: prompt }),
      });

      const data = await res.json();

      aiStatusEl.textContent = "AI explanation:";
      aiResponseEl.textContent =
        data.response || "AI was unable to provide a response.";
    } catch (err) {
      console.error("[LearnUI] AI request failed:", err);
      aiStatusEl.textContent = "Error contacting AI assistant.";
    }
  }

  /* Public API */
  return { openOverlay, closeOverlay };

})();
