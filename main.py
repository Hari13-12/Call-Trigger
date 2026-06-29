from fastapi import FastAPI
from livekit import api
import json
from livekit.api import ListRoomsRequest
import os
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("server-app")
logger.setLevel(logging.INFO)
app = FastAPI()


LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

@app.post("/make-sf-call")
async def make_call_list(numbers: list[str], name: list[str], mobile: list[str], ca: list[str], address: list[str], amount: list[str], date: list[str], overdue: list[str]):
    try:
        logger.info("Inside make call list")
        logger.info(f"Numbers: {numbers}")
        agent_name = "salesforce-agent"
        try:

            lkapi = api.LiveKitAPI(url=LIVEKIT_URL,
                    api_key=LIVEKIT_API_KEY,
                    api_secret=LIVEKIT_API_SECRET)
            for a,b,c,d,e,f,g,h in zip(numbers, name, mobile, ca, address, amount, date, overdue):
                number = "+91" + a
                room_name = f"{number}-{agent_name}-room"
                room_name = room_name.encode("utf-8", errors="ignore").decode("utf-8")
                metadata = json.dumps({"phone_number": a, "name":b, "mobile_last4": c, "ca_number": d, "service_address": e, "outstanding_amount": f, "due_date": g, "overdue_days": h})
                await lkapi.agent_dispatch.create_dispatch(
                    api.CreateAgentDispatchRequest(
                        agent_name=agent_name, room=room_name, metadata=metadata
                    )
                )
                await lkapi.agent_dispatch.list_dispatch(room_name=room_name)
            await lkapi.aclose()
            return {"status": "Call initiated successfully"}
        except Exception as e:
            logger.error(f"Error making call list: {e}")
            return {"status": f"Call initiation failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Error making call list: {e}")
        return {"status": f"Error making call list: {str(e)}"}
