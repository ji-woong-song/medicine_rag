
from fastapi import FastAPI
from starlette.responses import JSONResponse

from dto import UserConsultRequest
from services import llm_service

app = FastAPI()

@app.post("/medicine-consult")
async def medicine_consult(req: UserConsultRequest):
    content = await llm_service.consult_drug_safety(req.chat_user_id, req.target_id, req.concern)
    return JSONResponse(content={"response": content})

@app.post("/medical-department-consult")
async def department_consult(req: UserConsultRequest):
    content = await llm_service.consult_medical_department(req.chat_user_id, req.target_id, req.concern)
    return JSONResponse(content={"response": content})

@app.post("/symptoms-and-guidance-consult")
async def symptoms_and_guidance_consult(req: UserConsultRequest):
    content = await llm_service.consult_symptoms_and_guidance(req.chat_user_id, req.target_id, req.concern)
    return JSONResponse(content={"response": content})

@app.post("/food-consult")
async def food_consult(req: UserConsultRequest):
    content = await llm_service.consult_food(req.chat_user_id, req.target_id, req.concern)
    return JSONResponse(content={"response": content})

@app.post("/general-consult")
async def general_consult(req: UserConsultRequest):
    content = await llm_service.general_consult(req.chat_user_id, req.target_id, req.concern)
    return JSONResponse(content={"response": content})

