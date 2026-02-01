---
description: How to perform manual Buy, Sell, and Hold operations in the Trading Hub
---

# Manual Execution Workflow

This workflow guides users through the process of manual trading, overriding the Algo-Agents when necessary.

### Prerequisites
- Logged in as an **INVESTOR** or **ADMIN** acting as an Investor.
- Portfolio must have **Ready Capital** (cash balance).

### Steps

1. **Activate Manual Override**
   - Navigate to the **Trading Hub** (`/trading`).
   - Locate the mode toggle in the header.
   - Click **"Manual Mode"**. 
   - *Result*: The "Steward Auto" shield will dim, and the **Manual Order Ticket** will illuminate.

2. **Configure Order**
   - **Asset Ticker**: Enter the symbol (e.g., `NVDA`, `TSLA`).
   - **Units**: Set the quantity of shares/contracts to trade.

3. **Execute Trade**
   - Click the **"Buy"** (Green) button to enter a position.
   - Click the **"Sell"** (Red) button to exit or short a position.
   - *Result*: A "Security Handshake" shimmer will appear, followed by a confirmation alert.

4. **Confirm in wealth Vault**
   - Navigate to the **Portfolio** (`/portfolio`).
   - Verify that the **Asset Allocation** pie chart and **Active Holdings** list reflect the new trade.
   - Check the **Cash Balance** for the corresponding debit/credit.

5. **Hold Position**
   - To "Hold", simply allow the strategy to remain in the **Active Mandates** list without triggering a Sell command. 
   - Observe the **Agent Thought Stream** for real-time risk evaluation while holding.
