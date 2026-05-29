# UI

React + TypeScript + MUI frontend for Room Booker.

## Local Development

### Prerequisites

Deploy the infra first to get an API URL:
```bash
cd infra
./deploy.sh api
```

The API URL will be output after deployment (e.g. `https://xxxxxxx.execute-api.eu-west-2.amazonaws.com/dev`).

### Set up .env

Create a `.env` file in the `ui/` folder:
```
VITE_API_URL=https://your-api-id.execute-api.eu-west-2.amazonaws.com/dev
```

### Run
```bash
npm install
npm run dev
```

## CI/CD (GitHub Actions)

The GitHub workflow builds the UI and deploys it to CloudFront. For the production API URL to be baked into the build, set the following GitHub variable:

- **Variable:** `VITE_API_URL` — the deployed API Gateway URL

Set this in: Repo → Settings → Secrets and variables → Actions → Variables tab.
