# PDNA Agriculture Dashboard — Grenada

Dashboard for the KoboToolbox Agriculture MULTICROP project, using Eastern Caribbean dollars (EC$/XCD).

## Deployment

1. Create a **new GitHub repository** (e.g., `pdna-agriculture-dashboard`). Upload `app.py`, `requirements.txt`, and `.gitignore`.
2. In Streamlit Community Cloud, select the new repository and set the main file to `app.py`.
3. Open the app **Settings → Secrets** and enter the following (replace only the placeholder):

```toml
KOBO_SERVER = "https://kf.kobotoolbox.org"
KOBO_ASSET_UID = "asrBXTfAXfnqdMn9q4pdK5"
KOBO_API_TOKEN = "PASTE_YOUR_PRIVATE_KOBO_API_TOKEN_HERE"
```

4. Save Secrets and restart/reboot the app. Do **not** add the API token to GitHub.
5. Submit new Kobo records and press **Refresh Kobo data** in the app (otherwise data are cached up to five minutes).

## Data rules

- Top-level KPIs are computed from each **parent Kobo submission exactly once**, using `summary_damage`, `summary_losses`, and `summary_impact`.
- The 12 repeat-group types are parsed separately for product and group analysis, preventing double-counting of farms.
- Product-level subtotals need not equal overall totals because the form may include additional costs and other categories outside repeats.
- Kobo API returns original XLSForm **field names**, not necessarily the friendly labels shown in the XLSX export.
- Verify crop/product labels and repeat field mappings with live API results after deployment; the latest Grenada XLSForm may use custom field names.
- GPS points outside Grenada can occur in test submissions.
