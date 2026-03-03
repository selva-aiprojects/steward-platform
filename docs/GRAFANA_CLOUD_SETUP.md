# Grafana Cloud Setup Guide: StockSteward AI (Free Tier)

This guide helps you set up a **Free Forever** observability stack using Grafana Cloud, avoiding Render's server costs.

## 1. Create your Grafana Cloud Account
1. Go to [https://grafana.com/auth/sign-up/](https://grafana.com/auth/sign-up/) and create a free account.
2. Once logged in, you will be taken to your **Grafana Cloud Portal**.
3. Launch your managed Grafana instance (usually `yourname.grafana.net`).

## 2. Connect StockSteward Metrics
We will configure Grafana Cloud to "pull" metrics from your Render-hosted backend.

1. In your Grafana Cloud instance, go to **Connections** -> **Add new connection**.
2. Search for **Prometheus**.
3. Select **Prometheus** -> **Hosted Prometheus**.
4. We actually want to add a **Scrape Job**. 
   * *Note: Since the backend is public, we can use the "Synthetic Monitoring" or simply configure a cloud-hosted Prometheus to scrape your URL.*

### Easier Alternative: Cloud Scrape
1. Go to **Cloud Portal** -> **Prometheus** -> **Settings**.
2. Use the **Grafana Agent** or **Grafana Alloy** if running locally, but for Render:
3. Navigate to **Administration** -> **Scrape Jobs** (if available in your plan) OR:
4. **BEST WAY**: Go to **Dashboards** -> **Import**.
5. Import a standard Python/FastAPI dashboard or create a new one.
6. Use **Metrics** -> **Add Query** -> **Prometheus**.
7. For the URL, use: `https://stocksteward-ai-backend.onrender.com/api/v1/logs/metrics?user_id=999`.

## 3. Enable Embedding
To show the dashboard inside the StockSteward AI portal:
1. In Grafana Cloud, go to **Administration** -> **Settings**.
2. Ensure `allow_embedding` is `true` (it is usually enabled by default on Cloud).
3. Create a **Service Account** with "Viewer" role.
4. Generate a **Token** for this account.

## 4. Get the Embed URL
1. Open the dashboard you want to show (e.g., "FastAPI System Pulse").
2. Click the **Share** icon (top right) -> **Embed**.
3. Toggle "Current time range" and "Template variables" as needed.
4. Copy the URL inside the `src="..."` attribute.

## 5. Update StockSteward Portal
1. Go to your **Render Frontend** environment variables.
2. Set `REACT_APP_GRAFANA_URL` to the URL you copied in step 4.
3. Set `REACT_APP_SUPERSET_URL` to `native` (this will trigger the built-in React dashboard we are creating).

---

## Troubleshooting "Mixed Content"
If the iframe doesn't load:
*   Ensure your Grafana Cloud URL starts with `https://`.
*   Check that you haven't set "X-Frame-Options: DENY" in your Grafana settings (Administration -> Settings).
