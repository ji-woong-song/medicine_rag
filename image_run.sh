docker container stop silver-llm || true &&
docker container rm silver-llm || true &&
docker run -d -p 8000:8000 --name silver-llm --env-file .env shortboy7/silver-llm:latest