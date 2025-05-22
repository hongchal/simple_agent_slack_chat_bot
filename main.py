import os 
from slack_bolt import App 
from slack_bolt.adapter.socket_mode import SocketModeHandler 
from dotenv import load_dotenv 
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import time

from agent import graph as simple_agent
from langchain_core.messages import HumanMessage


load_dotenv() 
small_llm = ChatOpenAI(model="gpt-4o-mini")
llm = ChatOpenAI(model="gpt-4o")

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

user_cache = {"users": None, "timestamp": 0}
CACHE_TTL = 60 * 10  # 10분

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    client.views_publish(
      user_id=event["user"],
      view={
        "type": "home",
        "callback_id": "home_view",
 
        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to hpt(hanpoom ai agent) Home_* :tada:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*현재 사용 가능한 기능: *"
            }
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": """ 
              - 번역기(한글 -> 영어, 영어->한글) : /trans 를 입력하면 번역창이 뜹니다! \n
- 특정 시점의 주문 목록 추출 : hpt와의 개인 대화에서 추출 가능합니다
              """
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Currently available features: *"
            }
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": """
              - Translator (Korean → English, English → Korean): Type /trans to open the translation window! \n
- Extracting order list at a specific time: Available via private chat with hpt
              """
            }
          }
        ]
      }
    )
  
  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

def get_user_map(client):
    now = time.time()
    if user_cache["users"] is None or now - user_cache["timestamp"] > CACHE_TTL:
        users = client.users_list()
        user_cache["users"] = users
        user_cache["timestamp"] = now
    else:
        users = user_cache["users"]
    return {user['name'].lower(): user['id'] for user in users['members'] if not user['deleted']}

@app.command("/trans")
def translate_submit_command(body, ack, client):
    ack()
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view={
            "type": "modal",
            # View identifier
            "callback_id": "submit_trans",
            "title": {"type": "plain_text", "text": "hapoom translater"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps({"channel_id": body['channel_id']}),
            "blocks": [
                {
                    "type": "input",
                    "block_id": "input_c",
                    "label": {"type": "plain_text", "text": "plz write the message"},
                    "optional": False,
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "dreamy_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "korean to english, english to korean"}
                    }
                }
            ]
        }
    )

@app.view("submit_trans")
def view_submit_trans(body, ack, client):
    ack()

    private_metadata = json.loads(body['view']['private_metadata'])
    channel_id = private_metadata['channel_id']
    user_id = body['user']['id']

    if channel_id.startswith("D"):  
        dm_channel = client.conversations_open(users=user_id)
        channel_id = dm_channel["channel"]["id"]

    sentence = body['view']['state']['values']['input_c']['dreamy_input']['value']
    sender = body['user']['name']

    prompt = PromptTemplate.from_template("""
    You are a translator.
    Translate if the sentence is in Korean, translate it to English. dont not add any sentence without in sentence.
    If the sentence is in English, translate it to Korean. and don't fix '@~'.
    Sentence: {sentence}
    """)

    translate_chain = prompt | small_llm | StrOutputParser()
    response = translate_chain.invoke(sentence)
    mention_candidates = re.findall(r'@(\w+)', response)

    mention_pairs = [(orig, orig.lower()) for orig in mention_candidates]

    user_map = get_user_map(client)

    for orig, lower in mention_pairs:
        if lower in user_map:
            user_id = user_map[lower]
            response = response.replace(f"@{orig}", f"<@{user_id}>")

    response = f"sender: {sender} \n{response}"

    client.chat_postMessage(
        channel=channel_id,
        text=response
    )

@app.message()
def message_reaction(message, say, ack, client):
    ack()
    query = message['text']
    print(query)

    config = {
        'configurable': {
            'thread_id': message['user']
        }
    }

    file_path = None 

    for chunk in simple_agent.stream({'messages': [HumanMessage(query)], 'summary': ''}, stream_mode='values', config=config):
        # chunk['messages'][-1].pretty_print()
        for msg in chunk['messages']:
            # Tool Message에서 파일 경로 추출
            if getattr(msg, "type", None) == "tool" or getattr(msg, "role", None) == "tool":
                try:
                    tool_content = msg.content
                    if isinstance(tool_content, str) and "file_path" in tool_content:
                        file_info = json.loads(tool_content)
                        file_path = file_info.get("file_path")
                except Exception as e:
                    print(f"Tool message 파싱 오류: {e}")
            # 마지막 AI 메시지 저장
            if getattr(msg, "type", None) == "ai" or getattr(msg, "role", None) == "assistant":
                last_ai_content = msg.content

    # 1. 파일 경로가 포함되어 있는지 확인
    content = str(last_ai_content)
    print(content)

    if file_path and os.path.exists(file_path):
        client.files_upload_v2(
            channel=message['channel'],
            file=file_path,
            title="Order Data",
            filename=os.path.basename(file_path)
        )
        say("엑셀 파일을 업로드했습니다.")
    else:
        # 파일 경로가 없으면 마지막 AI 메시지 출력
        say(str(last_ai_content) if last_ai_content else "결과가 없습니다.")




if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start() 