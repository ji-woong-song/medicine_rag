import datetime
import json
from typing import Callable
import db
import format

variables_judge_prompt_template = """
You are a medical expert. 
Answer the user's concern with history by determining if a function call is needed.
If so, return the function name and the parameters as a JSON object array.
1. You must think about the user's concern and the information you have.
2. You should search the information widely to deal with the user's concern as much as possible to make the answer more accurate.
3. You need to be careful with typing param. (int as int without quote, str as str with quote, datetime as datetime.datetime with quote like '2024-01-01 00:00:00')
4. You must keep the order of the parameters as the order of the function's parameters.
5. If none of the given function can answer the user's concern, return empty array.

Current time: {current_time}
Patient ID: {patient_id}

User's concern:
{problem}

History:
{history}

Available functions:
{funcs_info}

Respond in JSON format with the structure:
1. Single function call:
[{{"function_name": "function_name", "params": [param1, param2, ...]}}]
2. Multiple function calls:
[{{"function_name": "function_name", "params": [param1, param2, ...]}}, {{"function_name": "function_name", "params": [param1, param2, ...]}}]
3. Zero function call:
[]
"""


class PromptBuilder:
    def __init__(self):
        self.prompt_template = """
당신은 의료 전문가이며 친절한 의료 상담사입니다.
당신의 역할은 다음과 같습니다.

1. 이 사람의 {informations} 을 참고하여 이 사람의 [고민]을 들어주세요.
2. 각종 [정보]들을 참고할 때는 현재 시간 {current_time}을 기준으로 참고하세요.
3. 조언을 할 때는 이 사람의 [고민]과 {informations} 사이 관계를 짚어주면서 시작하세요.
4. 이 사람의 고민을 해결하기 위한 조언을 해주세요.

[고민]
{concern}
"""
        self.informations = ""
        self.functions = [self.add_blood_pressure_info, self.add_blood_sugar_info, self.add_medicine_info, self.add_food_info, self.add_gi_info]
        self.function_info = "\n".join([self.get_function_info(func) for func in self.functions])
        self.function_map = {f.__name__: f for f in self.functions}

    def get_function_info(self, func: Callable) -> str:
        return f"Function name: {func.__name__}\nDocstring: {func.__doc__}"

    async def build_llm_based_variables_prompts(self, patient_id: str, input: str, history: list, current_time: datetime.datetime, llm):
        variables_judge_prompt = variables_judge_prompt_template.format(patient_id=patient_id, problem=input, history=history, funcs_info=self.function_info, current_time=current_time)
        result = llm.invoke(variables_judge_prompt)
        print("LLM Response:", result.content)
        
        try:
            content = result.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1]
            if content.endswith("```"):
                content = content.split("```")[0]
            content = content.strip()
            
            json_result = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON Parsing Error: {e}")
            print(f"Attempted to parse: {content}")
            raise
        
        for direction in json_result:
            function_name = direction["function_name"]
            params = direction["params"]
            await self.function_map[function_name](*params)
        self.prompt_template = self.prompt_template.format(concern=input, informations=self.informations, current_time=current_time)
        return self.prompt_template

    async def add_blood_pressure_info(self, patient_id, start_date, end_date):
        """
        Get patient's blood pressure information between start_date and end_date to the prompt.

        Parameters:
            patient_id(int): patient id
            start_date(datetime.datetime): start date, format: YYYY-MM-DD HH:MM:SS
            end_date(datetime.datetime): end date, format: YYYY-MM-DD HH:MM:SS
        """
        blood_pressure_prompt = """
[혈압 정보]
| 최고혈압 | 최저혈압 | 시간 |
|--------|--------|--------|
"""
        blood_pressure_info = await db.get_blood_pressure(patient_id, start_date, end_date)
        blood_pressure_format = format.table_blood_pressure(blood_pressure_info)
        blood_pressure_prompt += blood_pressure_format + "\n"
        self.prompt_template += blood_pressure_prompt
        self.informations += "[혈압 정보], "

    async def add_blood_sugar_info(self, patient_id, start_date, end_date):
        """
        Get patient's blood sugar information between start_date and end_date to the prompt.

        Parameters:
            patient_id(int): patient id
            start_date(datetime.datetime): start date, format: YYYY-MM-DD HH:MM:SS
            end_date(datetime.datetime): end date, format: YYYY-MM-DD HH:MM:SS
        """
        blood_sugar_prompt = """
[혈당량 정보]
| 날짜 | 혈당량 |
|--------|--------|
"""
        blood_sugar_info = await db.get_blood_sugar(patient_id, start_date, end_date)
        blood_sugar_format = format.table_blood_sugar(blood_sugar_info)
        blood_sugar_prompt += blood_sugar_format + "\n"
        self.prompt_template += blood_sugar_prompt
        self.informations += "[혈당량 정보], "

    async   def add_medicine_info(self, patient_id, start_date, end_date):
        """
        Get what medicine patient took or will take between start_date and end_date to the prompt.

        Parameters:
            patient_id(int): patient id
            start_date(datetime.datetime): start date, format: YYYY-MM-DD HH:MM:SS
            end_date(datetime.datetime): end date, format: YYYY-MM-DD HH:MM:SS
        """
        medicine_prompt = """
[복약 정보]
| 시작일 | 종료일 | 약품명 |
|--------|--------|--------|
"""
        medicine_info = await db.get_medicine(patient_id, start_date, end_date)
        medicine_format = format.table_medicine(medicine_info)
        medicine_prompt += medicine_format + "\n"
        self.prompt_template += medicine_prompt
        self.informations += "[복약 정보], "

    async def add_food_info(self, patient_id, start_date, end_date):
        """
        Get what patient ate between start_date and end_date to the prompt.

        Parameters:
            patient_id(int): patient id
            start_date(datetime.datetime): start date, format: YYYY-MM-DD HH:MM:SS
            end_date(datetime.datetime): end date, format: YYYY-MM-DD HH:MM:SS
        """
        food_prompt = """
[식사 정보]
| 먹은 시각 | 먹은 음식들 |
| -------- | --------- |
"""
        food_info = await db.get_food(patient_id, start_date, end_date)
        food_format = format.table_food(food_info)
        food_prompt += food_format + "\n"
        self.prompt_template += food_prompt
        self.informations += "[식사 정보], "

    async def add_gi_info(self):
        """
        Get Objective GI information to the prompt.
        """
        gi_prompt = """
[GI 정보]
| 음식 이름 | GI 지수 |
| -------- | ------ |
"""
        gi_info = await db.get_gi()
        gi_format = format.table_gi(gi_info)
        gi_prompt += gi_format + "\n"
        self.prompt_template += gi_prompt
        self.informations += "[GI 정보], "
