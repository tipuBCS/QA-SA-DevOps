# API

Using AWS Lambda Powertools for API

Package Manager: uv

## Development

### Install dependencies
```bash
uv sync --extra dev
```

### Unit tests
```bash
uv run pytest -m "not integration"
```

### Integration tests

Integration tests hit the live deployed API. You need to set `API_URL` in your `.env`:

```
API_URL=https://your-api-id.execute-api.eu-west-2.amazonaws.com/dev
```

Get this value from the CDK output after running `npm run deploy` in the `infra` folder.

Then run:
```bash
uv run pytest -m integration -v
```
