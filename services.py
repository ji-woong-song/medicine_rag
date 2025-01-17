import copy
import logging
from datetime import datetime, timedelta, timezone
from typing import Callable

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory, ConfigurableFieldSpec
from langchain_openai import ChatOpenAI
import pytz

import db
import format
import prompts
from config import OPEN_AI_KEY
from history import HistoryStore

def get_seoul_time():
    seoul_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(seoul_tz)


async def get_user_data(patient_id: int) -> [str, str]:
    medicine_data = await db.get_medicine(patient_id)
    medicine_prompt = format.table_medicine(medicine_data)
    blood_sugar = await db.get_blood_sugur(patient_id)
    blood_sugar_prompt = format.table_blood_sugar(blood_sugar)
    blood_pressure = await db.get_blood_pressure(patient_id)
    blood_pressure_prompt = format.table_blood_pressure(blood_pressure)
    return medicine_prompt, blood_sugar_prompt, blood_pressure_prompt


def get_function_info(func: Callable) -> str:
    return f"Function name: {func.__name__}\nDocstring: {func.__doc__}"


def get_function_name(func: Callable) -> str:
    return func.__name__


class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=OPEN_AI_KEY)
        self.history_factory = HistoryStore()

    async def consult_medical_department(self, chat_user_id: int, patient_id: int, concerns: str) -> str:
        """
        Recommends a medical department and provides tips for effective consultation based on the patient's recent data and concerns.

        Parameters:
            chat_user_id(int): ID of the user talking to the chatbot
            patient_id(int): The ID of the user who is the subject of health counseling. Used to query blood sugar, blood pressure, and medication information in the database
            concerns (str): A description of the patient's symptoms.

        Returns:
            str: The names of recommended medical department with simple explanation and advice for accurate consultation with a doctor
        """
        variables = await self.init_variables(chat_user_id, patient_id, concerns)
        report = await self.invoke_with_history(chat_user_id, patient_id, concerns, prompts.recommend_subject_prompt, variables)
        return report.content

    async def consult_drug_safety(self, chat_user_id: int, patient_id: int, concerns: str) -> str:
        """
        Evaluates whether a newly prescribed medication is safe to take with the patient's blood sugar, blood pressure and medication list
        And address their concerns.

        Parameters:
            chat_user_id(int): ID of the user talking to the chatbot.
            patient_id(int): The ID of the user who is the subject of health counseling. Used to query blood sugar, blood pressure, and medication information in the database
            concerns (str): A string describing the patient's concerns, questions and new_medicines.

        Returns:
            str: A message indicating whether the new medication is safe to take, addressing the patient's concerns.
        """
        variables = await self.init_variables(chat_user_id, patient_id, concerns)
        report = await self.invoke_with_history(chat_user_id, patient_id, concerns, prompts.drug_safety_prompt, variables)
        return report.content

    async def consult_symptoms_and_guidance(self, chat_user_id: int, patient_id: int, concerns: str) -> str:
        """
        Assesses the severity of symptoms based on recent blood sugar, blood pressure and medication list
        And provides guidance on whether medical attention is needed, addressing the patient's concerns.

        Parameters:
            chat_user_id(int): ID of the user talking to the chatbot
            patient_id(int): The ID of the user who is the subject of health counseling
            concerns (str): A description of the patient's symptoms.

        Returns:
            str: A message advising whether the symptoms warrant a hospital visit or can be monitored safely, addressing the patient's concerns.
        """
        variables = await self.init_variables(chat_user_id, patient_id, concerns)
        report = await self.invoke_with_history(chat_user_id, patient_id, concerns, prompts.symptoms_guidance_prompt, variables)
        return report.content

    async def consult_food(self, chat_user_id: int, patient_id: int, concerns: str) -> str:
        """
        Resolve the patient's food-related concerns based on their blood sugar, blood pressure, medication list, and food history.

        Parameters:
            chat_user_id(int): ID of the user talking to the chatbot
            patient_id(int): The ID of the user who is the subject of health counseling. Used to query blood sugar, blood pressure, and medication information in the database
            concerns (str): A description of the patient's food-related concerns.   

        Returns:
            str: A message about the patient's food-related concerns and the solution.
        """
        variables = await self.init_variables_with_food(chat_user_id, patient_id, concerns)
        report = await self.invoke_with_history(chat_user_id, patient_id, concerns, prompts.consult_food_prompt, variables)
        return report.content

    async def consult_general(self, chat_user_id: int, patient_id: int, concerns: str) -> str:
        variables = await self.init_variables(chat_user_id, patient_id, concerns)
        report = await self.invoke_with_history(chat_user_id, patient_id, concerns, prompts.consult_general_prompt, variables)
        return report.content

    async def route_prompt(self, chat_user_id: int, patient_id: int, concerns: str) -> Callable:
        funcs = [self.consult_drug_safety, self.consult_medical_department, self.consult_symptoms_and_guidance,
                 self.consult_general, self.consult_food]
        funcs_info = "\n".join([get_function_info(f) for f in funcs])
        function_map = {f.__name__: f for f in funcs}
        history = self.history_factory.get_history(chat_user_id, patient_id)
        prompt = PromptTemplate(
            input_variables=["problem"],
            template=prompts.router_prompt
        )
        response = self.llm.invoke(
            prompt.format(problem=concerns, funcs_info=funcs_info, history=history.messages)
        )
        content = response.content
        return function_map[f"{content}"]

    async def general_consult(self, chat_user_id: int, patient_id: int, concerns: str) -> str:
        func = await self.route_prompt(chat_user_id, patient_id, concerns)
        print(func)
        return await func(chat_user_id, patient_id, concerns)

    # seoul timezone
    async def init_variables(self, chat_user_id: int, patient_id: int, concerns: str, current: datetime = get_seoul_time()) -> dict:
        medicine_prompt, blood_sugar_prompt, blood_pressure_prompt = await get_user_data(patient_id)
        current_time = current.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time)
        return {
            "medicine": medicine_prompt,
            "blood_sugar": blood_sugar_prompt,
            "blood_pressure": blood_pressure_prompt,
            "current_time": current_time,
            "problem": concerns,
        }

    async def init_variables_with_food(self, chat_user_id: int, patient_id: int, concerns: str, current: datetime = get_seoul_time()) -> dict:
        variables = await self.init_variables(chat_user_id, patient_id, concerns, current)
        food = await db.get_food(patient_id)
        food_prompt = format.table_food(food)
        gi = await db.get_gi(patient_id)
        gi_prompt = format.table_gi(gi)
        variables["food"] = food_prompt
        variables["gi"] = gi_prompt
        return variables

    async def invoke_with_history(self, chat_user_id: int, patient_id: int, concerns: str, template: str,
                                  variables: dict) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", template)
        ])
        chain = prompt | self.llm
        chat_with_history = RunnableWithMessageHistory(
            chain,
            self.history_factory.get_history,
            input_messages_key="problem",
            history_messages_key="history",
            history_factory_config=[
                ConfigurableFieldSpec(
                    id="user_id",
                    annotation=str,
                    name="User ID",
                    description="Unique identifier for the user.",
                    default="",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="target_id",
                    annotation=str,
                    name="Target ID",
                    description="Unique identifier for the target.",
                    default="",
                    is_shared=True,
                ),
            ],
        )
        result = chat_with_history.invoke(
            variables,
            config={"configurable": {"user_id": chat_user_id, "target_id": patient_id}},
        )
        return result

    def clear_history(self, chat_user_id: int, patient_id: int) -> None:
        self.history_factory.clear_history(chat_user_id, patient_id)


llm_service = LLMService()
