# Slack Chat Bot with Langchain

## 시작하기

### 1. 환경 준비 및 패키지 설치
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 프로젝트 루트에 생성하고 다음과 같이 작성하세요:

```
SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_APP_TOKEN=your-slack-app-level-token
LANGCHAIN_API_KEY=your-langchain-api-key
```

### 3. 실행
챗봇 실행 스크립트(예: `main.py`)를 실행하세요:
```bash
python main.py
```

## 참고
- Slack API 토큰 발급: https://api.slack.com/apps
- Langchain 문서: https://python.langchain.com/ 