from typing import Callable

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

import db
import format
import prompts
from config import OPEN_AI_KEY


async def get_user_data(patient_id: int) -> [str, str]:
    medicine_data = await db.get_medicine(patient_id)
    medicine_prompt = format.table_medicine(medicine_data)
    blood_sugar = await db.get_blood_sugur(patient_id)
    blood_sugar_prompt = format.table_blood_sugar(blood_sugar)
    return medicine_prompt, blood_sugar_prompt


def get_function_info(func: Callable) -> str:
    return f"Function name: {func.__name__}\nDocstring: {func.__doc__}"


def get_function_name(func: Callable) -> str:
    return func.__name__


class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=OPEN_AI_KEY)

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
        medicine_prompt, blood_sugar_prompt = await get_user_data(patient_id)
        prompt = PromptTemplate(
            input_variables=["problem"],
            template=prompts.recommend_subject_prompt
        )
        report = self.llm.invoke(
            prompt.format(problem=concerns, medicine=medicine_prompt, blood_sugar=blood_sugar_prompt)
        )
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
        medicine_prompt, blood_sugar_prompt = await get_user_data(patient_id)

        prompt = PromptTemplate(
            input_variables=["problem"],
            template=prompts.drug_safety.prompt
        )
        report = self.llm.invoke(
            prompt.format(problem=concerns, medicine=medicine_prompt, blood_sugar=blood_sugar_prompt)
        )
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
        medicine_prompt, blood_sugar_prompt = await get_user_data(patient_id)

        prompt = PromptTemplate(
            input_variables=["problem"],
            template=prompts.recommend_subject_prompt
        )

        report = self.llm.invoke(
            prompt.format(problem=concerns, medicine=medicine_prompt, blood_sugar=blood_sugar_prompt)
        )
        return report.content

    async def route_prompt(self, chat_user_id: int, patient_id: int, concerns: str) -> Callable:
        funcs = [self.consult_drug_safety, self.consult_medical_department, self.consult_symptoms_and_guidance]
        funcs_info = "\n".join([get_function_info(f) for f in funcs])
        function_map = {f.__name__: f for f in funcs}
        prompt = PromptTemplate(
            input_variables=["problem"],
            template=prompts.router_prompt
        )
        response = self.llm.invoke(
            prompt.format(problem=concerns, funcs_info=funcs_info)
        )
        content = response.content
        print(content)
        return function_map[f"{content}"]


