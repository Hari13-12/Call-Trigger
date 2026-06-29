from fastapi import FastAPI, HTTPException
from livekit import api
import json
import os
import logging

logger = logging.getLogger("server-app")
logging.basicConfig(level=logging.INFO)

app = FastAPI()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")


@app.get("/")
async def health():
    return {"status": "ok"}


@app.post("/make-sf-call")
async def make_call_list(
    numbers: list[str],
    record_ids: list[str],
    name: list[str],
    mobile: list[str],
    ca: list[str],
    address: list[str],
    amount: list[str],
    date: list[str],
    overdue: list[str],
):
    try:
        logger.info("Inside make_call_list")

        lengths = [
            len(numbers),
            len(record_ids),
            len(name),
            len(mobile),
            len(ca),
            len(address),
            len(amount),
            len(date),
            len(overdue),
        ]

        if len(set(lengths)) != 1:
            raise HTTPException(
                status_code=400,
                detail="All input lists must have the same length."
            )

        agent_name = "salesforce-agent"

        async with api.LiveKitAPI(
            url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
        ) as lkapi:

            for (
                phone,
                record_id,
                customer_name,
                mobile_last4,
                ca_number,
                service_address,
                outstanding_amount,
                due_date,
                overdue_days,
            ) in zip(
                numbers,
                record_ids,
                name,
                mobile,
                ca,
                address,
                amount,
                date,
                overdue,
            ):

                phone_number = f"+91{phone}"

                room_name = f"{phone_number}-{agent_name}-room"
                room_name = room_name.encode(
                    "utf-8", errors="ignore"
                ).decode("utf-8")

                metadata = json.dumps(
                    {
                        "phone_number": phone_number,
                        "record_id": record_id,
                        "name": customer_name,
                        "mobile_last4": mobile_last4,
                        "ca_number": ca_number,
                        "service_address": service_address,
                        "outstanding_amount": outstanding_amount,
                        "due_date": due_date,
                        "overdue_days": overdue_days,
                    }
                )

                logger.info(
                    f"Dispatching call to {phone_number} | Record ID: {record_id}"
                )

                await lkapi.agent_dispatch.create_dispatch(
                    api.CreateAgentDispatchRequest(
                        agent_name=agent_name,
                        room=room_name,
                        metadata=metadata,
                    )
                )

                await lkapi.agent_dispatch.list_dispatch(room_name=room_name)

        return {
            "status": "success",
            "message": "Calls initiated successfully."
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Error initiating calls")

        raise HTTPException(
            status_code=500,
            detail=f"Call initiation failed: {str(e)}"
        )