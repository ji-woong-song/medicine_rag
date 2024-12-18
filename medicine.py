import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

import db
import format
import prompts

key = os.getenv("OPENAI_API_KEY")
load_dotenv()


llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0,
    api_key=key
)

prompt = PromptTemplate(
    input_variables=["problem"],
    template=prompts.recommend_subject_prompt
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


