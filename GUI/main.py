from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

origins = [
	"*" # 모든 출처? 허용
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    #allow_origin_regex="http://127\.0\.0\.1(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


async def get_rand():
    import random as rd
    rn = rd.randint(1,10)
    print("num is ",rn)
    await asyncio.sleep(rn)
    return rn

@app.get("/")
async def root():
    num = await get_rand()
    return {"message":"hell o'h"+str(num)}


#실행:uvicorn main:app --reload
#cd GUI로 열어서