source .env

echo "Starting local server\n"

export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY=$LANGSMITH_API_KEY
export LANGCHAIN_PROJECT=$LANGSMITH_PROJECT
export GOOGLE_API_KEY=$GOOGLE_API_KEY

#export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/app/local-auth.json
export ENV_TYPE=$ENV_TYPE
export PROJECT_ID=$PROJECT_ID
export PYTHONPATH=$(pwd)/app

echo "Loaded environment variables:"
echo "LANGCHAIN_TRACING_V2: $LANGCHAIN_TRACING_V2"
echo "LANGCHAIN_ENDPOINT: $LANGCHAIN_ENDPOINT"
echo "LANGCHAIN_API_KEY: $LANGCHAIN_API_KEY"
echo "LANGCHAIN_PROJECT: $LANGCHAIN_PROJECT"
echo "ENV_TYPE: $ENV_TYPE"
echo "PROJECT_ID: $PROJECT_ID"
echo "GOOGLE_API_KEY: $GOOGLE_API_KEY"

fastapi dev app/main.py