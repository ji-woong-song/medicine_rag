# Python 3.9 알파인 이미지를 기반으로 설정
FROM python:3.9-alpine

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 파일을 컨테이너로 복사
COPY requirement.txt .

# 패키지 설치
RUN pip install --no-cache-dir -r requirement.txt

# 타임존 설정
ENV TZ=Asia/Seoul
RUN apk add --no-cache tzdata

# 애플리케이션 파일 복사 (medicine.py와 .env 파일 제외)
COPY . .

# uvicorn을 사용하여 애플리케이션 실행
CMD ["uvicorn", "server:app", "--host", "0.0.0.0"]
