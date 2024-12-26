docker container stop silver-llm && docker container rm silver-llm &&
docker run -d -p 8000:8000 -n silver-llm --env-file .env shortboy7/silver-llm:latest