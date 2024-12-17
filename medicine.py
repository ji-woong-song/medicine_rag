import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

import db
import format

key = os.getenv("OPENAI_API_KEY")
load_dotenv()

recommend_subject_template = """
당신은 의료 전문가이며 친절한 의료 상담사입니다.
당신의 역할은 다음과 같습니다.

1. 이 사람의 [복약 정보] 및 [혈당량 정보], [혈압 정보]를 참고하여 이 사람의 [고민]을 들어주세요.
2. [복약 정보]를 참고할 때는 현재 시간 "2024-11-29 22:00"을 기준으로 참고하세요.
3. 조언을 할 때는 이 사람의 [고민]과 [복약 정보] 사이 관계를 짚어주면서 시작하세요. 
4. 이 사람의 고민을 해결하기 위한 조언을 해주세요.
5. 조언에는 우선적으로 방문해야 할 진료과 3개를 적합한 순서대로 포함해주세요. 
6. 제시한 진료과마다의 차이점을 초등학생이라도 알기 쉽게 설명해줘
7. 조언에는 의사에게 상담할 때 말하면 좋은 정보를 포함해주세요.

[고민]
{problem}

[혈당량 정보]
| 날짜 | 혈당량 |
|--------|--------|
{blood_sugar}

[혈압 정보]
| 최고혈압 | 최저혈압 | 시간 |
|--------|--------|--------|
| 100 | 80 | 아침 |

[복약 정보]
| 시작일 | 종료일 | 약품명 |
|--------|--------|--------|
{medicine}
"""

llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0,
    api_key=key
)

prompt = PromptTemplate(
    input_variables=["problem"],
    template=recommend_subject_template
)

async def generate_report(input:str, user_id):
    medicine_data = await db.get_medicine(user_id)
    medicine_prompt = format.table_medicine(medicine_data)
    blood_sugar = await db.get_blood_sugur(user_id)
    blood_sugar_prompt = format.table_blood_sugar(blood_sugar)
    print(blood_sugar_prompt)
    report = llm.invoke(prompt.format(problem=input, medicine=medicine_prompt, blood_sugar=blood_sugar_prompt))
    print(report.content)


if __name__ == '__main__':
    input = "혈액 응고 장애가 있는데 내가 먹고 있는 약 중에 먹으면 안되는 약이 있어?"
    asyncio.run(generate_report(input, 1))


