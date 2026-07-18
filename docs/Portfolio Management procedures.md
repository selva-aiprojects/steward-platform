# StockSteward AI — Automated Portfolio Management & Stewardship Procedures

This document provides a comprehensive operational guide detailing the automated portfolio construction, optimization, risk buffer management, and active rotation procedures implemented in **StockSteward AI**. It is designed to explain the core quantitative logics and safety protocols to users and traders, ensuring full confidence in how capital is managed.

---

## 1. Core Portfolio Design & Optimization Philosophy

StockSteward AI manages trader assets by blending **Advanced Agentic AI Intelligence** with time-tested **Modern Portfolio Theory (MPT)**. 

Rather than relying on single-model predictions, the system uses a hybrid model that maximizes risk-adjusted returns (Sharpe ratio) while strictly maintaining a cash-hedged execution buffer to navigate volatile market regimes.

```
                  ┌──────────────────────────────┐
                  │      Candidate Symbols       │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │    4-Model Ensemble Score    │
                  │   (FinBERT+LLM+LSTM+Risk)    │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │    Markowitz Optimization    │
                  │   (Sharpe Ratio Maximize)    │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │     25% Portfolio Buffer     │
                  │  (Rotation 15% + Hedge 10%)  │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │     Active Position Plan     │
                  └──────────────────────────────┘
```

---

## 2. Dynamic Portfolio Construction Pipeline

The core engine responsible for constructing portfolios is located in the [AIPortfolioBuilder](file:///d:/Training/working/stocksteward-ai/backend/app/portfolio_construction/ai_portfolio_builder.py) class. When a trader requests portfolio creation or investment, the builder follows a rigorous pipeline:

### Step 1: Candidate Selection
The system automatically identifies highly liquid candidate symbols (such as the top Nifty components or symbols inside the trader's active watchlists) or analyzes the specific list of scripts requested by the user.

### Step 3: 4-Model AI Ensemble Scoring
Each candidate script is evaluated using a weighted multi-model ensemble:
1. **FinBERT Sentiment Analysis:** Evaluates market sentiment from news, financial reports, and social feeds using the local FinBERT models in [AIFilterEngine](file:///d:/Training/working/stocksteward-ai/backend/app/engines/finbert_engine.py).
2. **LLM Fundamental Grading:** Employs advanced LLM reasoning (via Groq/OpenAI/Anthropic) in the [EnhancedLLMService](file:///d:/Training/working/stocksteward-ai/backend/app/services/enhanced_llm_service.py) to assess corporate health, growth forecasts, and valuation ratios.
3. **LSTM Price Prediction:** Leverages long short-term memory (LSTM) neural networks via the [LSTMPredictor](file:///d:/Training/working/stocksteward-ai/backend/app/ml_models/lstm_predictor.py) to analyze the last 90 days of OHLCV data for technical momentum.
4. **Risk Score Assessment:** Projects tail risk, historical volatility, and Value-at-Risk (VaR) utilizing the portfolio risk metrics.

---

## 3. Sector & Industry Diversification Controls

To protect the portfolio from sector-wide downtrends and systemic industry shocks, StockSteward AI employs strict diversification controls:

* **Sector Mapping Heuristics:** The system dynamically classifies candidate symbols into primary industries (e.g., *Banking*, *IT*, *FMCG*, *Energy & Telecom*, *Automobiles*, *Metals & Mining*) using mapped definitions in [_guess_sector](file:///d:/Training/working/stocksteward-ai/backend/app/portfolio_construction/ai_portfolio_builder.py#L723).
* **Sector Cap Limit:** Under [_apply_concentration_limits](file:///d:/Training/working/stocksteward-ai/backend/app/portfolio_construction/ai_portfolio_builder.py#L603), the engine restricts aggregate exposure to any single sector to a maximum of **40%** (`MAX_SECTOR_PCT = 0.40`).
* **Redistribution Logic:** If a sector's cumulative weight exceeds 40%, the excess allocation is pruned and redistributed proportionally across other qualified sectors.

---

## 4. Real-Time Sentiment Analysis via FinBERT

Market sentiment analysis is executed through a specialized NLP pipeline:
* **Model Framework:** The system relies on **FinBERT** (via [FinBERTEngine](file:///d:/Training/working/stocksteward-ai/backend/app/engines/finbert_engine.py)), a language model pre-trained specifically on financial text corpora to achieve high classification accuracy for market terminology.
* **Ingested Feeds:** Sentiment is parsed from live news headers and social streams (simulated StockTwits, Twitter, and Reddit) gathered by [SocialMediaService](file:///d:/Training/working/stocksteward-ai/backend/app/services/social_media_service.py).
* **Scoring Bounds:** The model extracts positive, negative, and neutral probabilities, generating an aggregate sentiment score between `-1.0` (highly bearish) and `+1.0` (highly bullish), which is factored directly into the AI ensemble weight.

---

## 5. Rejection & Filtering Logic (Pruning Criteria)

Before any capital is allocated to a script, the candidate must pass rigorous filtering checks to protect the trader from low-quality or highly volatile assets:

1. **AI Score Rejection:** Any script with a combined AI ensemble score below **0.10** (`MIN_AI_SCORE_TO_INCLUDE = 0.10`) is instantly rejected and excluded from the portfolio.
2. **Liquidity Filter:** The engine checks average trading volumes over the trailing 90 days. Illiquid scripts with sparse volumes are pruned to avoid slippage during order execution.
3. **Volatility & Risk Check:** Script volatility is evaluated by [AIFilterEngine.assess_risk](file:///d:/Training/working/stocksteward-ai/backend/app/engines/ai_filter_engine.py#L432). High-risk parameters penalize the script’s ensemble score (calculated as `1 - risk_score`), reducing its likelihood of selection.

---

## 6. Dynamic Allocation Strategies

Traders can configure their portfolio construction using several strategy types defined in the [InvestmentStrategy](file:///d:/Training/working/stocksteward-ai/backend/app/schemas/portfolio_construction.py) schema:

1. **AI Hybrid (Default):** Blends AI scoring with MPT optimization. Weights are calculated via:
   $$\text{Final Weight} = 0.5 \cdot \text{AI Weight (Softmax of Ensemble)} + 0.5 \cdot \text{MPT Weight (Sharpe Maximizer)}$$
2. **AI Only:** Ignores covariance structures and builds weights purely on the softmax of the AI ensemble scores.
3. **MPT Only:** Ignores AI predictions and optimizes allocation strictly based on historical covariance matrixes.
4. **Markowitz Optimization:** Runs standard Sharpe ratio maximization over a trailing 252-day window using the Scipy SLSQP solver.

> [!IMPORTANT]
> The engine restricts individual holdings under all strategies to a minimum of **2%** (to avoid micro-positions) and a maximum of **20%** of the active capital (to prevent single-stock concentration).

---

## 7. Handling Trader Intent & Investment Horizon

If the system does not explicitly know the trader's intent or time horizon, it defaults to a **Medium-Term Horizon (1–6 months)** with a **Moderate Risk Profile**.

However, if the trader's intent is defined (either selected via the dashboard or parsed from chatbot prompts), the system dynamically shifts the weight of its ensemble models and adjusts target margins:

| Trader Horizon | Primary Driver | Ensemble Weights (Sentiment / Fundamentals / LSTM Price / Risk) | Execution Parameters |
| :--- | :--- | :--- | :--- |
| **Short-Term** | Technical Momentum | High weight on **LSTM Technical Forecasts** (40%) and **FinBERT Sentiment** (25%). Low weight on fundamentals. | Tight stop-losses (**2% - 3%**) and rapid position rotations. |
| **Medium-Term (Default)** | Balanced Sharpe | Balanced split: Sentiment (25%), Fundamentals (25%), LSTM (30%), Risk (20%). | Standard stop-losses (**5%**) and target profit limits (**15%**). |
| **Long-Term** | Value Investing | Heavy weight on **LLM Fundamental Quality** (30%) and **MPT Covariance Optimization** (30%). Low weight on short-term technicals. | Wider stop-loss boundaries (**8% - 12%**) to absorb market noise. |

---

## 8. Standing Recommendations and AI Previews

Traders do not need to create a live portfolio to see what the AI currently favors. StockSteward AI supports a "Standing Recommendations" preview flow:
* **API Endpoint:** `GET /api/v1/portfolio-ai/ai-scores` in [portfolio_investment.py](file:///d:/Training/working/stocksteward-ai/backend/app/api/v1/endpoints/portfolio_investment.py#L358).
* **Flow:** Returns the current ensemble ratings, sentiment classifications, and technical predictions for the stock universe.
* **Chatbot Integration:** The [ChatWidget](file:///d:/Training/working/stocksteward-ai/frontend/src/components/ChatWidget.jsx) accesses this API to suggest the platform's current top-performing and highly rated scripts to the trader dynamically during conversation.

---

## 9. The 25% Risk & Rotation Buffer

A core differentiator of StockSteward AI is the mandatory preservation of a **25% cash buffer** on all automated portfolios. Managed by the [RiskBufferManager](file:///d:/Training/working/stocksteward-ai/backend/app/portfolio_construction/risk_buffer_manager.py), this buffer serves two distinct purposes:

```
                      ┌────────────────────────┐
                      │ Total Capital Invested │
                      └───────────┬────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
      ┌───────────────────────┐       ┌───────────────────────┐
      │  Active Allocation    │       │     Capital Buffer    │
      │         (75%)         │       │         (25%)         │
      └───────────────────────┘       └───────────┬───────────┘
                                                  │
                                  ┌───────────────┴───────────────┐
                                  ▼                               ▼
                      ┌───────────────────────┐       ┌───────────────────────┐
                      │   Rotation Reserve    │       │      Risk Hedge       │
                      │   (60% of Buffer)     │       │   (40% of Buffer)     │
                      └───────────────────────┘       └───────────────────────┘
```

1. **Rotation Reserve (60% of Buffer / 15% of Total Portfolio):**
   * Acts as tactical "dry powder". It allows the system to execute immediate buy orders when the AI detects high-conviction opportunities, without forcing the premature sale of core holdings.
2. **Risk Hedge (40% of Buffer / 10% of Total Portfolio):**
   * Stored in stable liquid assets/cash to protect the trader's total valuation against sudden market drawdowns, helping avoid margin calls or forced liquidations.

---

## 10. Continuous Monitoring & Active Rotation

Portfolios are monitored in real time. As market conditions evolve, the [RiskBufferManager](file:///d:/Training/working/stocksteward-ai/backend/app/portfolio_construction/risk_buffer_manager.py) and [PortfolioAgent](file:///d:/Training/working/stocksteward-ai/backend/app/agents/portfolio_agent.py) handle active rotation:

### Rotation triggers
* **Active-to-Buffer (Sell Trigger):** If an existing holding's current AI score falls by more than **0.30** compared to its entry score (delta < -0.30), the system triggers a partial or complete trim, converting the position back into buffer cash.
* **Buffer-to-Active (Buy Trigger):** If a candidate stock's AI score exceeds a current holding's score by more than **0.30**, the system executes a buy order using the Rotation Reserve cash.

> [!WARNING]
> To protect capital, the amount deployed into any single rotation trade is capped at **30% of the available buffer** or **5% of the total portfolio value**, ensuring that tactical entries remain sized safely.
