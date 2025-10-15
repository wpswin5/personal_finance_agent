# Personal Finance Agent (Starter)

This is a starter repo structure for an **AI-powered personal finance agent**.

## Features (planned)

- Upload transaction CSVs
- Classify transactions into categories
- Detect anomalies (unusual spend)
- Summarize financial insights
- Conversational agent powered by an LLM

## How to run locally

```bash
# build image
docker build -t finance-agent .

# run container
docker run -p 8000:8000 finance-agent
```

Visit http://localhost:8000/docs for interactive API docs.

## Next steps

- Connect to Azure SQL Database
- Implement classification & anomaly models
- Wire conversational agent to Azure OpenAI + LangChain
- Test readme update for PR process