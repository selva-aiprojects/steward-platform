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

The core engine responsible for constructing portfolios is located in the [AIPortfolioBuilder](file:///d:/Training/working/stocksteward-ai/backend/app/portfolio_construction/ai_portfolio_builder.py) class. When a trader requests portfolio creation or investment, the builder follows a rigorous 6-step pipeline:

### Step 1: Candidate Selection
The system automatically identifies highly liquid candidate symbols (such as the top Nifty components or symbols inside the trader's active watchlists) or analyzes the specific list of scripts requested by the user.

### Step 2: 4-Model AI Ensemble Scoring
Each candidate script is evaluated using a weighted multi-model ensemble:
1. **FinBERT Sentiment Analysis:** Evaluates market sentiment from news, financial reports, and social feeds using the local FinBERT models in [AIFilterEngine](file:///d:/Training/working/stocksteward-ai/backend/app/engines/finbert_engine.py).
2. **LLM Fundamental Grading:** Employs advanced LLM reasoning (via Groq/OpenAI/Anthropic) in the [EnhancedLLMService](file:///d:/Training/working/stocksteward-ai/backend/app/services/enhanced_llm_service.py) to assess corporate health, growth forecasts, and valuation ratios.
3. **LSTM Price Prediction:** Leverages long short-term memory (LSTM) neural networks via the [LSTMPredictor](file:///d:/Training/working/stocksteward-ai/backend/app/ml_models/lstm_predictor.py) to analyze the last 90 days of OHLCV data for technical momentum.
4. **Risk Score Assessment:** Projects tail risk, historical volatility, and Value-at-Risk (VaR) utilizing the portfolio risk metrics.

The ensemble weights are customized dynamically based on the trader’s selected risk profile:

| Model Indicator | Conservative Profile | Moderate Profile | Aggressive Profile |
| :--- | :---: | :---: | :---: |
| **FinBERT Sentiment** | 30% | 25% | 20% |
| **LLM Fundamental** | 30% | 25% | 20% |
| **LSTM Price Predict** | 10% | 30% | 40% |
| **Risk Score (Inverted)** | 30% | 20% | 20% |

> [!NOTE]
> For the Risk Score weight, the system inverts the rating so that lower-risk assets contribute positively to the overall score. Candidate scripts with an aggregate AI score below `0.10` are automatically excluded from the allocation plan to maintain quality.

### Step 3: Modern Portfolio Theory (MPT) Optimization
For portfolios constructed under the **AI Hybrid** or **MPT Only** strategies, the engine runs a Markowitz covariance-based optimization:
* Annualized mean returns and a covariance matrix are calculated using the trailing **252 days of historical data**.
* A Scipy SLSQP (Sequential Least Squares Programming) optimizer solves for the asset weights that maximize the Sharpe ratio:
  $$\max \text{Sharpe Ratio} = \frac{R_p - R_f}{\sigma_p}$$
* The risk-free rate ($R_f$) varies by profile: **4%** for Conservative, **3%** for Moderate, and **2%** for Aggressive.

### Step 4: Hybrid Weight Allocation
The final weights are calculated by blending the AI ensemble scores (converted via softmax to sum to 1) and the MPT weights using a standard hybrid factor ($\alpha = 0.5$):
$$\text{Weight}_{\text{final}} = 0.5 \cdot \text{Weight}_{\text{AI}} + 0.5 \cdot \text{Weight}_{\text{MPT}}$$

### Step 5: Concentration Limits & Risk Constraints
To prevent over-concentration, the builder enforces strict safety limits:
* **Max Single Position:** No single stock can exceed **20%** of the active portfolio value.
* **Min Single Position:** Micro-allocations below **2%** are pruned.
* **Max Sector Exposure:** Total exposure to a single industry/sector cannot exceed **40%**.
* **Min Diversification:** The portfolio must hold at least **5 distinct positions**.

Excess allocations resulting from these rules are automatically redistributed proportionally or routed back into the cash buffer.

---

## 3. The 25% Risk & Rotation Buffer

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

## 4. Continuous Monitoring & Active Rotation

Portfolios are monitored in real time. As market conditions evolve, the [RiskBufferManager](file:///d:/Training/working/stocksteward-ai/backend/app/portfolio_construction/risk_buffer_manager.py) and [PortfolioAgent](file:///d:/Training/working/stocksteward-ai/backend/app/agents/portfolio_agent.py) handle active rotation:

### Rotation triggers
* **Active-to-Buffer (Sell Trigger):** If an existing holding's current AI score falls by more than **0.30** compared to its entry score (delta < -0.30), the system triggers a partial or complete trim, converting the position back into buffer cash.
* **Buffer-to-Active (Buy Trigger):** If a candidate stock's AI score exceeds a current holding's score by more than **0.30**, the system executes a buy order using the Rotation Reserve cash.

> [!WARNING]
> To protect capital, the amount deployed into any single rotation trade is capped at **30% of the available buffer** or **5% of the total portfolio value**, ensuring that tactical entries remain sized safely.

---

## 5. Screen & Chatbot Integration Flows

Traders can review, analyze, and trigger these portfolio procedures directly inside the user interface:

### Chatbot Dialogue Flow
1. Open the [ChatWidget](file:///d:/Training/working/stocksteward-ai/frontend/src/components/ChatWidget.jsx) in the bottom-right corner of the application.
2. Ask the bot questions like: *"What is the AI score for RELIANCE?"* or *"Can you recommend a conservative strategy portfolio?"*
3. The widget routes the prompt to `/api/v1/enhanced-ai/chat` or `/api/v1/portfolio-ai/ai-scores` to fetch real-time multi-model analysis, displaying clear technical, fundamental, and sentiment summaries directly in the conversation.

### Manual Portfolio Deployment Flow
1. Navigate to the **Investment Dashboard** at `/investment` ([InvestmentDashboard.jsx](file:///d:/Training/working/stocksteward-ai/frontend/src/pages/InvestmentDashboard.jsx)) or the **Portfolio** tab at `/portfolio` ([Portfolio.jsx](file:///d:/Training/working/stocksteward-ai/frontend/src/pages/Portfolio.jsx)).
2. The UI renders the [ConfidenceInvestmentCard](file:///d:/Training/working/stocksteward-ai/frontend/src/components/ConfidenceInvestmentCard.jsx) showing your available cash balance.
3. Click **Launch Intelligent Investment**. The frontend calls `POST /api/v1/portfolio-ai/invest` in [portfolio_investment.py](file:///d:/Training/working/stocksteward-ai/backend/app/api/v1/endpoints/portfolio_investment.py#L46), executing the 4-model ensemble, setting up the 25% buffer, and deploying the capital safely.
4. Active rebalances and rotation opportunities can then be tracked and manually approved or automated in real time.
