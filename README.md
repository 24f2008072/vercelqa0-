# eShopCo latency metrics API

## Deploy to Vercel
1. Extract this ZIP and push the folder contents to a GitHub repository.
2. Import that repository at https://vercel.com/new.
3. Deploy with the default project settings.
4. Your POST endpoint will be `https://YOUR-VERCEL-PROJECT.vercel.app/` (the route sends requests to the Python function).

## Request
```json
{"regions":["apac","amer"],"threshold_ms":181}
```

## Notes
- Response is a JSON object keyed by region.
- `breaches` counts latency values strictly greater than `threshold_ms`.
- `p95_latency` uses linear interpolation (NumPy default percentile convention).
- CORS allows any origin and POST/OPTIONS requests.
