# app.py
import os, requests
from fastapi import FastAPI, Request, BackgroundTasks
from rag import get_answer
from dotenv import load_dotenv; load_dotenv()

SID, TOK = os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
FROM = os.getenv("TWILIO_WHATSAPP_NUMBER")

app = FastAPI()

def twilio_send(to: str, body: str):
    print("--- 4. ATTEMPTING TO SEND TWILIO MESSAGE ---")
    requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{SID}/Messages.json",
        auth=(SID, TOK),
        data={"From": FROM, "To": to, "Body": body[:4096]},
        timeout=10
    )
    print("--- 5. TWILIO MESSAGE SENT SUCCESSFULLY ---")

@app.post("/webhook")
async def inbound(req: Request, bg: BackgroundTasks):
    print("\n--- 1. WEBHOOK RECEIVED ---")
    data = await req.form()
    sender = data.get("From")        # "whatsapp:+55..."
    body   = data.get("Body", "").strip()
    print(f"--- From: {sender}, Body: {body} ---")

    def job():
        print("--- 2. STARTING BACKGROUND JOB ---")
        try:
            # --- The most likely point of failure is here ---
            reply = get_answer(body)
            # ------------------------------------------------

            # --- FOR DEBUGGING: To isolate the problem, you can comment out the line above
            # --- and uncomment the line below to test a simple reply.
            # reply = "This is a test reply."
            # ------------------------------------------------

            print(f"--- 3. GOT REPLY FROM RAG: '{reply[:50]}...' ---")
        except Exception as e:
            print(f"--- X. AN EXCEPTION OCCURRED: {e} ---")
            reply = f"⚠️ Sorry, an error occurred:\n{e}"
        
        twilio_send(sender, reply)

    bg.add_task(job)
    return "ok"