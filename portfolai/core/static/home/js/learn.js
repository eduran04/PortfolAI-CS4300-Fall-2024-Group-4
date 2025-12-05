// Learn Topic Data

const learnTopics = {
  "Stock Market Basics": {
    subtopics: {
      "What Is a Stock?": [
        "A stock represents partial ownership in a company. When you buy a share, you are buying a tiny slice of that business and its future results.",
        "Companies issue stock to raise money for things like launching new products, hiring employees, paying off debt, or expanding into new markets.",
        "As a shareholder, you benefit when the company grows. If profits and expectations rise, other investors may be willing to pay more for each share, pushing the stock price higher.",
        "Some companies also share a portion of their profits through dividends, which are cash payments made to shareholders on a regular schedule.",
        "Key idea: owning stock lets everyday people participate in the success (and risks) of real businesses without having to run those businesses themselves."
      ],

      "ETFs Explained": [
        "An ETF (Exchange-Traded Fund) is a basket of investments—like stocks or bonds—that trades on an exchange just like a single stock.",
        "When you buy one share of an ETF, you are getting tiny pieces of many underlying holdings at once. This gives you instant diversification in a single trade.",
        "Most ETFs follow a specific index or theme. For example, one ETF might track the S&P 500, while another focuses on clean energy companies or technology stocks.",
        "ETFs are popular because they usually have lower fees than actively managed funds and require less research than choosing many individual companies on your own.",
        "Key idea: ETFs are a beginner-friendly way to build a diversified portfolio quickly, without having to pick each stock by hand."
      ],

      "What Makes Prices Move?": [
        "Stock prices move because of supply and demand. If more people want to buy a stock than sell it, the price tends to go up. If more people want to sell than buy, the price tends to go down.",
        "Investor expectations are a big driver. News about earnings, new products, leadership changes, or the overall economy can change how people feel about a company’s future.",
        "Short-term price moves can also be influenced by headlines, social media buzz, or market emotions like fear and greed, even when the underlying business has not changed much.",
        "Long-term stock performance usually follows the company’s results. Strong revenue growth, solid profits, and good management can push prices higher over time.",
        "Key idea: price changes are a constant negotiation between buyers and sellers about what a company is worth today based on what they expect tomorrow."
      ]
    }
  },

  "Reading Stock Charts": {
    subtopics: {
      "Candlesticks": [
        "Candlestick charts show how a stock’s price moved during a specific time period (like one day or one hour) using a single candle shape.",
        "Each candlestick displays four key prices: the open, high, low, and close. The thick body shows the range between open and close, while thin wicks show the extremes of the day.",
        "If the closing price is higher than the opening price, the candle is usually shown as green or white (a bullish candle). If the closing price is lower, it is red or black (a bearish candle).",
        "Patterns of candlesticks can hint at market sentiment. For example, a series of strong green candles may show growing optimism, while a series of red candles can signal selling pressure.",
        "Key idea: candlesticks turn raw price numbers into an easy-to-scan visual story of how buyers and sellers behaved during each period."
      ],

      "Volume": [
        "Volume tells you how many shares of a stock were traded during a specific time period. It is often shown as bars beneath the price chart.",
        "High volume means a lot of shares changed hands, which usually signals strong interest or conviction from buyers and sellers.",
        "When price moves sharply on low volume, it can be a weaker signal because only a small number of traders participated in that move.",
        "Traders often look for price breakouts (moves above resistance or below support) that are supported by higher-than-normal volume to confirm the strength of the move.",
        "Key idea: volume is like the “voice” behind price action—louder volume generally means the market is speaking more clearly."
      ],

      "Support & Resistance": [
        "Support is a price level where a stock has historically had difficulty falling below because buyers tend to step in around that area.",
        "Resistance is a price level where a stock has historically had difficulty moving above because sellers tend to appear and take profits.",
        "These levels form as investors remember past turning points and place buy or sell orders near those same prices again.",
        "Traders use support and resistance to help plan entries and exits. Buying near support and taking profits near resistance is a common approach.",
        "Key idea: support and resistance act like floors and ceilings on a chart, helping you anticipate where price might pause, bounce, or break through."
      ]
    }
  },

  "Company Fundamentals": {
    subtopics: {
      "P/E Ratio": [
        "The price-to-earnings (P/E) ratio compares a company’s current stock price to its earnings per share. It shows how much investors are willing to pay for $1 of earnings.",
        "A higher P/E can mean investors expect strong future growth, while a lower P/E might suggest the stock is cheaper or that investors are less confident.",
        "P/E should be compared within context—such as against competitors in the same industry or the company’s own historical P/E range.",
        "A very high P/E may signal that expectations are extremely optimistic, which can be risky if the company fails to deliver.",
        "Key idea: the P/E ratio is a quick starting point to judge valuation, but it’s not enough on its own to make a final decision."
      ],

      "Revenue & Profit": [
        "Revenue is the total amount of money a company brings in from selling products or services before any expenses are taken out.",
        "Profit (also called net income) is what remains after all costs—like salaries, materials, rent, and taxes—have been paid.",
        "Growing revenue with stable or increasing profit margins is usually a healthy sign that the business is expanding efficiently.",
        "If revenue grows but profit does not, it may mean costs are rising too quickly or the company is discounting heavily to drive sales.",
        "Key idea: strong and consistent growth in both revenue and profit usually supports long-term stock performance."
      ],

      "Cash Flow": [
        "Cash flow tracks how much actual cash is coming into and going out of a business over a period of time.",
        "Positive cash flow means the company generates enough cash to pay its bills, invest in growth, and possibly return money to shareholders through dividends or buybacks.",
        "A company can look profitable on paper but still struggle if its customers pay late or inventory builds up, which can hurt cash flow.",
        "Investors pay close attention to operating cash flow and free cash flow to see if the company can sustain itself without constantly borrowing.",
        "Key idea: profits are important, but steady, positive cash flow is what actually keeps a business alive and flexible."
      ]
    }
  },

  "How to Analyze a Stock": {
    subtopics: {
      "Understand the Business": [
        "The first step in analyzing a stock is understanding what the company actually does in plain language.",
        "Ask simple questions: What problem does this company solve? Who are its customers? How does it make money from them?",
        "Review the company’s main products or services, where it operates (local or global), and whether demand is likely to grow or shrink over time.",
        "If you cannot easily explain the business model to a friend, it may be a sign that you need to learn more before investing.",
        "Key idea: a clear understanding of the business helps you judge whether its future looks promising or uncertain."
      ],

      "Competitive Advantage": [
        "A competitive advantage (or moat) is something that makes it hard for other companies to copy or overtake a business.",
        "Common moats include strong brand recognition, unique technology, cost advantages, patents, network effects, or high switching costs for customers.",
        "A strong moat allows a company to maintain pricing power, protect its market share, and generate higher profits over time.",
        "Look for signs like loyal customers, consistent profit margins, and leadership in market share when evaluating a moat.",
        "Key idea: companies with durable competitive advantages are often better positioned to deliver steady long-term returns."
      ],

      "Valuation Basics": [
        "Valuation is about estimating whether a stock is cheap, fairly priced, or expensive compared to its fundamentals and peers.",
        "Investors use tools like the P/E ratio, price-to-sales, price-to-book, and discounted cash flow models to estimate value.",
        "A great company can still be a poor investment if you pay too high a price relative to what it is likely worth.",
        "Comparing a stock’s valuation to similar companies and its own history helps you avoid overpaying during hype.",
        "Key idea: good investing combines quality businesses with reasonable prices, not just one or the other."
      ]
    }
  },

  "Building a Portfolio": {
    subtopics: {
      "Diversification": [
        "Diversification means spreading your investments across different companies, sectors, and even asset classes so you are not relying on just one area.",
        "If one stock or sector performs poorly, other holdings can help offset those losses, making your overall experience smoother.",
        "You can diversify by owning broad-market ETFs, by mixing industries (e.g., tech, healthcare, consumer goods), and by including some bonds or cash.",
        "Too little diversification can lead to big swings in your portfolio. Too much can make it hard to track what you own.",
        "Key idea: thoughtful diversification reduces risk without requiring you to predict which single stock will win."
      ],

      "How Many Stocks?": [
        "There is no perfect number of stocks that fits everyone, but beginners often do best starting with a manageable list.",
        "A common approach is to hold a few broad ETFs for core exposure and then add a small number of individual companies you understand well.",
        "Owning too few stocks can leave you vulnerable to one company’s problems. Owning too many can make research and monitoring overwhelming.",
        "Think about your time, interest level, and comfort with research when deciding how many positions to hold.",
        "Key idea: start simple, stay organized, and expand only when you can confidently follow what you own."
      ],

      "Sample Portfolios": [
        "Sample portfolios are example setups that show how different mixes of assets can match different goals and risk levels.",
        "A conservative beginner might favor more bonds and broad market ETFs, while a growth-oriented investor might lean more heavily into stock ETFs and a few growth companies.",
        "For example, a balanced beginner portfolio might be: 60% total-market ETF, 20% growth or tech ETF, and 20% bond or dividend ETF.",
        "As your situation changes—such as age, income, or goals—you can adjust these percentages to stay aligned with your needs.",
        "Key idea: your portfolio structure should match your time horizon, risk tolerance, and personal goals, not someone else’s preferences."
      ]
    }
  },

  "Beginner Mistakes": {
    subtopics: {
      "FOMO & Hype": [
        "FOMO (fear of missing out) happens when investors rush into a stock just because it is going up or trending on social media.",
        "Buying based on hype instead of research often means entering at high prices when excitement is already priced in.",
        "When the excitement fades or news shifts, these stocks can fall quickly, leaving late buyers with big losses.",
        "It is okay to be curious about popular stocks, but always slow down, research the business, and ask whether the price still makes sense.",
        "Key idea: don’t let headlines or hype pressure you into decisions that do not fit your plan."
      ],

      "Overtrading": [
        "Overtrading means buying and selling frequently, often in response to every piece of news or every small price move.",
        "This behavior increases transaction costs, can create tax consequences, and usually leads to emotional decision-making.",
        "Constantly checking prices and reacting to short-term swings makes it harder to stay focused on long-term goals.",
        "Many studies show that investors who trade less and stick to a plan often outperform those who trade too often.",
        "Key idea: investing is usually more successful as a patient, long-term game—not a rapid-fire reaction to every move."
      ],

      "No Plan": [
        "Investing without a written plan makes it easy to change course whenever emotions spike, especially during market drops.",
        "A basic plan should include your goals (like retirement or buying a home), your time horizon, and how much risk you are willing to take.",
        "It should also outline how you choose investments, how diversified you want to be, and what you will do during market volatility.",
        "Having this plan written down gives you something steady to lean on when you feel tempted to panic or chase trends.",
        "Key idea: a simple, written plan is one of the strongest tools you have to keep your behavior aligned with your goals."
      ]
    }
  },

  "Understanding Market News": {
    subtopics: {
      "Economic Reports": [
        "Economic reports, like inflation (CPI), unemployment rates, and interest-rate decisions, describe the overall health of the economy.",
        "These reports influence expectations about whether consumers will keep spending and whether businesses will keep growing.",
        "When inflation is high or interest rates rise, borrowing becomes more expensive, which can slow growth and put pressure on stocks.",
        "When reports show steady growth and manageable inflation, investors may feel more confident, and markets can respond positively.",
        "Key idea: understanding the basic direction of the economy helps you put market moves in context instead of reacting blindly."
      ],

      "Earnings Season": [
        "Earnings season is the period—typically four times a year—when public companies report their financial results for the quarter.",
        "These reports include revenue, profit, and guidance about what management expects for the future.",
        "Stocks often move sharply after earnings because new information forces investors to update their expectations.",
        "A company can grow profits yet still fall in price if results were below what investors were expecting.",
        "Key idea: earnings season is a regular checkpoint where the story about a company is updated and repriced."
      ],

      "Analyst Ratings": [
        "Analysts are professionals who research companies and issue ratings such as Buy, Hold, or Sell, often with a specific price target.",
        "A rating upgrade or downgrade can influence short-term investor sentiment and create quick price moves.",
        "However, analysts can be wrong, and their opinions are only one input among many when evaluating a stock.",
        "It is helpful to read the reasons behind an analyst’s view rather than blindly following the rating alone.",
        "Key idea: use analyst research as a supporting tool, not as a substitute for your own understanding."
      ]
    }
  },

  "Investing Styles": {
    subtopics: {
      "Growth Investing": [
        "Growth investing focuses on companies that are expected to increase their revenues, profits, or market share faster than average.",
        "These companies often reinvest earnings back into the business instead of paying dividends, aiming to expand quickly.",
        "Growth stocks can be more volatile because their prices are built on high expectations about the future.",
        "If those expectations are met or exceeded, returns can be strong. If they disappoint, price declines can be sharp.",
        "Key idea: growth investing suits investors who can handle ups and downs in pursuit of higher long-term potential."
      ],

      "Value Investing": [
        "Value investing looks for companies that appear to be trading below their estimated intrinsic value based on fundamentals.",
        "These companies may be temporarily out of favor, facing short-term challenges, or simply overlooked by the market.",
        "Value investors look for strong balance sheets, steady cash flow, and reasonable prospects selling at a discount.",
        "The strategy relies on the idea that, over time, the market tends to correct mispricings as information becomes clearer.",
        "Key idea: value investing is about patience—buying quality businesses when they are cheap and waiting for recognition."
      ],

      "Dividend Investing": [
        "Dividend investing focuses on companies that regularly share a portion of their profits with shareholders in the form of cash payments.",
        "These companies are often mature, stable businesses with predictable earnings and a track record of consistent payouts.",
        "Dividend income can be reinvested to buy more shares, increasing the compounding effect over time.",
        "Dividend stocks can also help soften the impact of market downturns by providing income even when prices fluctuate.",
        "Key idea: dividend investing blends potential price appreciation with ongoing cash flow for a smoother experience."
      ]
    }
  },

  "Tools & Resources": {
    subtopics: {
      "Research Platforms": [
        "Research platforms like Yahoo Finance, TradingView, and Finviz provide charts, news, company profiles, and key financial ratios.",
        "They often include screeners that let you filter stocks by criteria such as market cap, sector, valuation, or growth metrics.",
        "Using these tools helps you compare companies side-by-side and avoid relying on a single data point or opinion.",
        "Over time, you can customize a small set of favorite tools that match your research style and preferences.",
        "Key idea: think of research platforms as your investing toolkit—learn them gradually and use them to support better decisions."
      ],

      "Glossaries & Education": [
        "Finance glossaries and educational sites help translate technical terms into plain language.",
        "Learning the meaning of common terms—like EPS, free cash flow, volatility, or market cap—makes reading articles and reports much easier.",
        "Short lessons, videos, and quizzes can reinforce your understanding and build confidence step by step.",
        "Focusing on a few concepts at a time prevents overload and keeps learning manageable and sustainable.",
        "Key idea: improving your vocabulary is one of the fastest ways to feel more at home in the investing world."
      ],

      "Official Sources": [
        "Official sources include company investor-relations pages, SEC filings (like 10-Ks and 10-Qs), and regulatory announcements.",
        "These documents provide detailed information about a company’s financial results, risks, strategies, and leadership.",
        "They are not always easy to read at first, but even scanning key sections can give you an advantage over investors who rely only on headlines.",
        "Combining official documents with simpler summaries from trusted sites gives you both depth and clarity.",
        "Key idea: primary sources are the closest you can get to the raw truth about a company’s situation and plans."
      ]
    }
  }
};

//Visuals per topic

const topicVisuals = {
  "Stock Market Basics": {
    tag: "Foundations",
    heroClass: "hero-basics",
    icon: "📈"
  },
  "Reading Stock Charts": {
    tag: "Charts & Signals",
    heroClass: "hero-charts",
    icon: "📊"
  },
  "Company Fundamentals": {
    tag: "Company Health",
    heroClass: "hero-fundamentals",
    icon: "📑"
  },
  "How to Analyze a Stock": {
    tag: "Analysis Skills",
    heroClass: "hero-analysis",
    icon: "🧠"
  },
  "Building a Portfolio": {
    tag: "Portfolio Design",
    heroClass: "hero-portfolio",
    icon: "💼"
  },
  "Beginner Mistakes": {
    tag: "Common Pitfalls",
    heroClass: "hero-mistakes",
    icon: "⚠️"
  },
  "Understanding Market News": {
    tag: "News & Events",
    heroClass: "hero-news",
    icon: "📰"
  },
  "Investing Styles": {
    tag: "Approaches",
    heroClass: "hero-styles",
    icon: "🎯"
  },
  "Tools & Resources": {
    tag: "Toolbox",
    heroClass: "hero-tools",
    icon: "🛠️"
  }
};


// No default topic until user clicks
let currentTopic = null;
let currentSubtopic = null;

// Main topic strip
const catTrack = document.getElementById("learnCatTrack");
const catPrevBtn = document.getElementById("learnCatPrev");
const catNextBtn = document.getElementById("learnCatNext");

// Subtopic grid
const cardGrid = document.getElementById("learnPillRow");
const activeTopicLabel = document.getElementById("learnActiveTopicLabel");

// Overlay + controls
const overlay = document.getElementById("learnOverlay");
const titleEl = document.getElementById("learnTitle");
const subtopicEl = document.getElementById("learnSubtopic");
const slideEl = document.getElementById("learnSlide");
const counterEl = document.getElementById("learnCounter");
const closeBtn = document.getElementById("learnClose");
const nextBtn = document.getElementById("learnNext");
const prevBtn = document.getElementById("learnPrev");

// AI section
const askAiBtn = document.getElementById("learnAskAiBtn");
const aiStatusEl = document.getElementById("learnAiStatus");
const aiResponseEl = document.getElementById("learnAiResponse");

// markdown formatter for AI responses

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function formatAiMarkdown(md) {
  if (!md) return "";

  let text = md.replace(/\r\n/g, "\n").trim();

  // Clean stray # markers
  text = text.replace(/\s+#\s*(?=\n|$)/g, "");
  text = text.replace(/^#\s*$/gm, "");

  // Escape first for XSS safety
  text = escapeHtml(text);

  // Bold
  text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  const lines = text.split("\n");
  let htmlParts = [];
  let inList = false;

  function openList() {
    if (!inList) {
      htmlParts.push('<ul class="chat-list">');
      inList = true;
    }
  }
  function closeList() {
    if (inList) {
      htmlParts.push("</ul>");
      inList = false;
    }
  }

  for (let rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      continue;
    }

    const headingMatch = line.match(/^\s*(#{1,3})\s*(.+)$/);
    if (headingMatch) {
      closeList();
      const level = headingMatch[1].length;
      const textContent = headingMatch[2].trim();

      if (level === 3) {
        htmlParts.push(`<h4 class="chat-header">${textContent}</h4>`);
      } else {
        htmlParts.push(`<h3 class="chat-header">${textContent}</h3>`);
      }
      continue;
    }



    // Bullets
    const bulletMatch = line.match(/^-\s+(.+)/);
    if (bulletMatch) {
      openList();
      htmlParts.push("<li>" + bulletMatch[1].trim() + "</li>");
      continue;
    }

    // Paragraph
    closeList();
    htmlParts.push("<p>" + line + "</p>");
  }

  closeList();
  return htmlParts.join("\n");
}

// init

function initLearnSection() {
  if (!catTrack || !cardGrid) return;

  // Card grid
  cardGrid.classList.add("learn-card-grid");
  cardGrid.innerHTML = "";

  if (activeTopicLabel) {
    activeTopicLabel.textContent = "Select a topic to view lessons";
  }

  // Main topic cards always visible
  const topicCards = catTrack.querySelectorAll(".learn-topic-card");
  topicCards.forEach((card) => {
    card.addEventListener("click", () => {
      const topic = card.getAttribute("data-topic");
      setActiveTopic(topic);
    });
  });


  // Overlay controls
  if (closeBtn) {
    closeBtn.addEventListener("click", closeOverlay);
  }

  // Keyboard navigation: only Escape to close
  document.addEventListener("keydown", (e) => {
    if (!overlay || overlay.classList.contains("hidden")) return;
    if (e.key === "Escape") closeOverlay();
  });

  // Ask AI button
  if (askAiBtn) {
    askAiBtn.addEventListener("click", askAiForCurrent);
  }
}

// Topic & Subtopic Cards

function setActiveTopic(topicName) {
  currentTopic = topicName;
  currentSubtopic = null;

  if (activeTopicLabel) activeTopicLabel.textContent = topicName;

  // Highlight active main-topic card
  const topicCards = catTrack.querySelectorAll(".learn-topic-card");
  topicCards.forEach((card) => {
    const t = card.getAttribute("data-topic");
    if (t === topicName) card.classList.add("active");
    else card.classList.remove("active");
  });

  buildSubtopicCards(topicName);
}

function buildSubtopicCards(topicName) {
  if (!cardGrid) return;
  cardGrid.innerHTML = "";

  const subtopicsObj = learnTopics[topicName].subtopics;
  const subNames = Object.keys(subtopicsObj);

  const visuals = topicVisuals[topicName] || {
    tag: "Beginner",
    heroClass: "hero-default",
    icon: "📚"
  };

  subNames.forEach((subName) => {
    const slides = subtopicsObj[subName];
    const previewText = slides[0] || "";

    const card = document.createElement("article");
    card.className = "learn-card";
    card.setAttribute("data-subtopic", subName);

    // Meta row
    const metaRow = document.createElement("div");
    metaRow.className = "learn-card-meta";

    const tag = document.createElement("span");
    tag.className = "learn-card-tag";
    tag.textContent = visuals.tag;


    metaRow.appendChild(tag);

    // Hero strip with topic-specific visuals
    const hero = document.createElement("div");
    hero.className = `learn-card-hero ${visuals.heroClass}`;

    const iconWrap = document.createElement("div");
    iconWrap.className = "learn-card-hero-icon";
    iconWrap.textContent = visuals.icon;

    const badge = document.createElement("div");
    badge.className = "learn-card-hero-badge";
    badge.textContent = topicName;

    hero.appendChild(iconWrap);
    hero.appendChild(badge);

    // Title & description
    const title = document.createElement("h3");
    title.className = "learn-card-title";
    title.textContent = subName;

    const desc = document.createElement("p");
    desc.className = "learn-card-desc";
    desc.textContent = previewText;

    // Footer
    const footer = document.createElement("div");
    footer.className = "learn-card-footer";

    const topicLabel = document.createElement("span");
    topicLabel.textContent = topicName;

    const cta = document.createElement("span");
    cta.className = "learn-card-cta";
    cta.textContent = "Learn More →";

    footer.appendChild(topicLabel);
    footer.appendChild(cta);

    // Assemble card
    card.appendChild(metaRow);
    card.appendChild(hero);
    card.appendChild(title);
    card.appendChild(desc);
    card.appendChild(footer);

    card.addEventListener("click", () => {
      openOverlay(topicName, subName);
    });

    cardGrid.appendChild(card);
  });
}

// Overlay Cards

function openOverlay(topicName, subtopicName) {
  currentTopic = topicName;
  currentSubtopic = subtopicName;

  if (titleEl) titleEl.textContent = topicName;
  if (subtopicEl) subtopicEl.textContent = subtopicName;
  if (aiStatusEl) aiStatusEl.textContent = "";
  if (aiResponseEl) aiResponseEl.textContent = "";

  updateSlide();

  if (overlay) {
    overlay.classList.remove("hidden");
  }
  document.body.style.overflow = "hidden";
}

function closeOverlay() {
  if (overlay) {
    overlay.classList.add("hidden");
  }
  document.body.style.overflow = "";
}

function updateSlide() {
  const slides = learnTopics[currentTopic].subtopics[currentSubtopic];
  if (!slides) return;

  const subset = Array.isArray(slides) ? slides.slice(0, 2) : [slides];
  const text = subset.join(" ");

  if (slideEl) slideEl.textContent = text;
}

// AI Integration

async function askAiForCurrent() {
  if (!currentTopic || !currentSubtopic) {
    if (aiStatusEl) {
      aiStatusEl.textContent = "Pick a lesson first, then ask PortfolAI to explain it.";
    }
    return;
  }

  if (aiStatusEl) aiStatusEl.textContent = "Asking PortfolAI assistant...";
  if (aiResponseEl) aiResponseEl.textContent = "";

  const prompt = `Explain the topic "${currentTopic} - ${currentSubtopic}" in simple terms for a beginner investor. Focus on why it matters and how it relates to stock investing and portfolio decisions. Use short sections with labels like "Definition", "Why it matters", and "How it fits into investing.Write a complete explanation and then stop. Do NOT ask the reader any follow-up questions, 
do NOT invite them to ask more questions, and do NOT end with a question."`;

  try {
    const res = await fetch("/api/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: prompt })
    });

    const data = await res.json();
    if (data && data.response) {
      if (aiStatusEl) aiStatusEl.textContent = "AI explanation:";
      const formatted = formatAiMarkdown(data.response);
      if (aiResponseEl) aiResponseEl.innerHTML = formatted;
    } else {
      if (aiStatusEl) aiStatusEl.textContent = "Sorry, the AI could not generate a response.";
    }
  } catch (err) {
    console.error("AI error:", err);
    if (aiStatusEl) {
      aiStatusEl.textContent = "Error contacting AI assistant. Please try again.";
    }
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initLearnSection);
} else {
  initLearnSection();
}
