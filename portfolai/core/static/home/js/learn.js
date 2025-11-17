// Learn topic data

const learnTopics = {
  "Stock Market Basics": {
    subtopics: {
      "What Is a Stock?": [
        "A stock represents ownership in a company. When you buy a share, you own a tiny piece of the business. Companies issue stock to raise money for growth, hiring, and new products.",
        "Stocks matter because they let everyday people share in the profits and growth of successful companies. As the company grows and becomes more valuable, its stock price can increase, rewarding investors."
      ],
      "ETFs Explained": [
        "An ETF (Exchange-Traded Fund) is a basket of stocks (or other assets) that trades like a single stock. When you buy one ETF share, you gain exposure to many underlying holdings.",
        "ETFs are important for stock investors because they provide instant diversification, often at low cost. This helps reduce risk compared to owning a single stock."
      ],
      "What Makes Prices Move?": [
        "Stock prices move based on supply and demand. When more people want to buy than sell, prices rise. When more want to sell than buy, prices fall.",
        "Earnings reports, economic news, interest rates, and overall market sentiment all influence investor expectations, which then move stock prices."
      ]
    }
  },

  "Reading Stock Charts": {
    subtopics: {
      "Candlesticks": [
        "Candlestick charts show the open, high, low, and close prices for a given time period. Green (or white) candles usually mean price increased; red (or black) means price decreased.",
        "Candlestick patterns help traders and investors visualize short-term sentiment and potential reversals or continuations in price trends."
      ],
      "Volume": [
        "Volume tells you how many shares were traded in a given period. High volume often confirms strong interest behind a price move.",
        "Understanding volume matters because big price movements with low volume may be less reliable than moves supported by heavy trading activity."
      ],
      "Support & Resistance": [
        "Support is a price level where a stock tends to stop falling as buyers step in. Resistance is a level where it tends to stop rising as sellers appear.",
        "These levels help investors identify potential entry and exit points, and understand where price might struggle to move past."
      ]
    }
  },

  "Company Fundamentals": {
    subtopics: {
      "P/E Ratio": [
        "The price-to-earnings (P/E) ratio compares a stock’s price to its earnings per share. It’s one way to gauge how 'expensive' a stock is relative to its profits.",
        "P/E matters because it reflects investor expectations. High P/E can signal growth optimism, while low P/E may indicate undervaluation or underlying concerns."
      ],
      "Revenue & Profit": [
        "Revenue is the total money a company brings in from selling products or services. Profit is what’s left after expenses are subtracted.",
        "Growing revenue and stable or rising profits usually indicate a healthy business, which can support long-term stock performance."
      ],
      "Cash Flow": [
        "Cash flow tracks how much actual cash moves in and out of a business. Strong positive cash flow supports operations, debt payments, and reinvestment.",
        "For investors, cash flow is critical: companies need real cash (not just accounting profits) to survive downturns and fund future growth."
      ]
    }
  },

  "How to Analyze a Stock": {
    subtopics: {
      "Understand the Business": [
        "Before investing, you should understand what the company does, how it makes money, and who its customers are.",
        "Clarity about the business model reduces risk: if you can’t explain how the company earns money, it’s harder to judge whether the stock is a good investment."
      ],
      "Competitive Advantage": [
        "A 'moat' is a company’s durable edge over competitors—like strong brand, exclusive technology, or network effects.",
        "Companies with strong moats are more likely to maintain profits and pricing power, which supports long-term stock returns."
      ],
      "Valuation Basics": [
        "Valuation is about estimating whether a stock is cheap, fair, or expensive compared to its fundamentals and peers.",
        "Paying far above a company’s estimated value can limit future returns, while buying below value can improve long-term upside."
      ]
    }
  },

  "Building a Portfolio": {
    subtopics: {
      "Diversification": [
        "Diversification means spreading your money across different stocks, sectors, or asset classes to reduce risk.",
        "If one stock or sector performs poorly, diversified portfolios are better positioned to handle the loss."
      ],
      "How Many Stocks?": [
        "Many investors start with a handful of well-researched stocks plus broad ETFs. Owning too few increases risk; owning too many can be hard to manage.",
        "The right number depends on your time, risk tolerance, and whether you rely on ETFs for broad exposure."
      ],
      "Sample Portfolios": [
        "A simple beginner mix might be: 60% broad market ETF, 20% growth ETF, 20% bond or dividend ETF.",
        "These mixes matter because allocation—how you divide your money across assets—often impacts risk and returns more than individual stock picks."
      ]
    }
  },

  "Beginner Mistakes": {
    subtopics: {
      "FOMO & Hype": [
        "FOMO (Fear of Missing Out) leads investors to chase hot stocks after big price spikes.",
        "Buying based on hype rather than research can mean entering at inflated prices and facing large drawdowns."
      ],
      "Overtrading": [
        "Overtrading is constantly buying and selling, often based on emotion or short-term noise.",
        "Frequent trading can increase fees, taxes, and stress—often leading to worse long-term results than a calmer, long-term approach."
      ],
      "No Plan": [
        "Investing without a clear plan—no goals, time horizon, or risk limits—makes it easy to panic or chase trends.",
        "A written plan helps guide decisions and keeps your portfolio aligned with your personal financial goals."
      ]
    }
  },

  "Understanding Market News": {
    subtopics: {
      "Economic Reports": [
        "Reports like inflation (CPI), unemployment, and interest-rate decisions affect the entire market.",
        "They matter because they shape expectations about growth, profits, and borrowing costs—key drivers of stock prices."
      ],
      "Earnings Season": [
        "Companies regularly report earnings, revenue, and guidance for future quarters.",
        "Stocks often move sharply after earnings because new information updates investors’ expectations."
      ],
      "Analyst Ratings": [
        "Analysts issue Buy/Hold/Sell ratings and price targets based on their research.",
        "Ratings can influence short-term sentiment, but investors should use them as one input—not a sole decision-maker."
      ]
    }
  },

  "Investing Styles": {
    subtopics: {
      "Growth Investing": [
        "Growth investors focus on companies expected to increase revenues and profits quickly.",
        "These stocks can offer high upside but may also be more volatile and sensitive to changes in expectations."
      ],
      "Value Investing": [
        "Value investors look for companies trading below their estimated intrinsic value.",
        "The idea is to buy quality businesses at a discount to improve long-term risk/reward."
      ],
      "Dividend Investing": [
        "Dividend investors seek companies that regularly share profits with shareholders through cash payments.",
        "Dividends can provide income and help smooth returns during volatile markets."
      ]
    }
  },

  "Tools & Resources": {
    subtopics: {
      "Research Platforms": [
        "Tools like Yahoo Finance, TradingView, and Finviz offer charts, fundamentals, and screeners.",
        "Using good tools helps you compare companies, spot trends, and stay informed."
      ],
      "Glossaries & Education": [
        "Finance glossaries and educational sites help decode jargon like EPS, P/E, and volatility.",
        "Understanding these terms makes it easier to interpret news, reports, and analyst opinions."
      ],
      "Official Sources": [
        "Official sites like SEC.gov and company investor relations pages provide filings, annual reports, and presentations.",
        "These primary sources are essential for serious research because they come directly from companies and regulators."
      ]
    }
  }
};

// ==================== STATE & ELEMENTS ====================

let currentTopic = "Stock Market Basics";
let currentSubtopic = null;
let currentSlideIndex = 0;

const catTrack = document.getElementById("learnCatTrack");
const catPrevBtn = document.getElementById("learnCatPrev");
const catNextBtn = document.getElementById("learnCatNext");
const pillRow = document.getElementById("learnPillRow");
const activeTopicLabel = document.getElementById("learnActiveTopicLabel");

const overlay = document.getElementById("learnOverlay");
const titleEl = document.getElementById("learnTitle");
const subtopicEl = document.getElementById("learnSubtopic");
const slideEl = document.getElementById("learnSlide");
const counterEl = document.getElementById("learnCounter");
const closeBtn = document.getElementById("learnClose");

const nextBtn = document.getElementById("learnNext");
const prevBtn = document.getElementById("learnPrev");

const askAiBtn = document.getElementById("learnAskAiBtn");
const aiStatusEl = document.getElementById("learnAiStatus");
const aiResponseEl = document.getElementById("learnAiResponse");

// Initialization

function initLearnSection() {
  if (!catTrack || !pillRow) return;

  // Set up topic card clicks
  const cards = catTrack.querySelectorAll(".learn-topic-card");
  cards.forEach((card) => {
    card.addEventListener("click", () => {
      const topic = card.getAttribute("data-topic");
      setActiveTopic(topic);
    });
  });

  // Set default active topic
  setActiveTopic(currentTopic);

  // Category scroll arrows
  catPrevBtn.addEventListener("click", () => {
    catTrack.scrollBy({ left: -260, behavior: "smooth" });
  });
  catNextBtn.addEventListener("click", () => {
    catTrack.scrollBy({ left: 260, behavior: "smooth" });
  });

  // Overlay controls
  closeBtn.addEventListener("click", closeOverlay);

  nextBtn.addEventListener("click", () => {
    if (!currentTopic || !currentSubtopic) return;
    const slides = learnTopics[currentTopic].subtopics[currentSubtopic];
    if (currentSlideIndex < slides.length - 1) {
      currentSlideIndex++;
      updateSlide();
    }
  });

  prevBtn.addEventListener("click", () => {
    if (!currentTopic || !currentSubtopic) return;
    if (currentSlideIndex > 0) {
      currentSlideIndex--;
      updateSlide();
    }
  });

  // Keyboard navigation
  document.addEventListener("keydown", (e) => {
    if (overlay.classList.contains("hidden")) return;
    if (e.key === "Escape") closeOverlay();
    if (e.key === "ArrowRight") nextBtn.click();
    if (e.key === "ArrowLeft") prevBtn.click();
  });

  // Ask AI integration
  askAiBtn.addEventListener("click", askAiForCurrent);
}

// Topic and Subtopic Handlers

function setActiveTopic(topicName) {
  currentTopic = topicName;
  activeTopicLabel.textContent = topicName;

  // Highlight active card
  const cards = catTrack.querySelectorAll(".learn-topic-card");
  cards.forEach((card) => {
    const t = card.getAttribute("data-topic");
    if (t === topicName) card.classList.add("active");
    else card.classList.remove("active");
  });

  // Rebuild subtopic pills
  buildSubtopicPills(topicName);
}

function buildSubtopicPills(topicName) {
  pillRow.innerHTML = "";
  const subtopicsObj = learnTopics[topicName].subtopics;
  const keys = Object.keys(subtopicsObj);

  keys.forEach((subName, index) => {
    const pill = document.createElement("button");
    pill.className = "learn-pill";
    pill.textContent = subName;

    pill.addEventListener("click", () => {
      // Remove previous active
      pillRow.querySelectorAll(".learn-pill").forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      openOverlay(topicName, subName);
    });

    // Auto-open first subtopic for convenience
    if (index === 0 && !currentSubtopic) {
      currentSubtopic = subName;
    }

    pillRow.appendChild(pill);
  });
}

// Overlay and Flashcard Handlers

function openOverlay(topicName, subtopicName) {
  currentTopic = topicName;
  currentSubtopic = subtopicName;
  currentSlideIndex = 0;

  titleEl.textContent = topicName;
  subtopicEl.textContent = subtopicName;
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

// Ai Intergration

async function askAiForCurrent() {
  if (!currentTopic || !currentSubtopic) return;

  aiStatusEl.textContent = "Asking PortfolAI assistant...";
  aiResponseEl.textContent = "";

  const prompt = `Explain the topic "${currentTopic} - ${currentSubtopic}" in simple terms for a beginner investor. Focus on why it matters and how it relates to stock investing and portfolio decisions.`;

  try {
    const res = await fetch("/api/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: prompt })
    });

    const data = await res.json();
    if (data && data.response) {
      aiStatusEl.textContent = "AI explanation:";
      aiResponseEl.textContent = data.response;
    } else {
      aiStatusEl.textContent = "Sorry, the AI could not generate a response.";
    }
  } catch (err) {
    console.error("AI error:", err);
    aiStatusEl.textContent = "Error contacting AI assistant. Please try again.";
  }
}

//Init on Load

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initLearnSection);
} else {
  initLearnSection();
}
