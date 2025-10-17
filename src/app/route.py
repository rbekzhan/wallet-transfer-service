from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.handlers import send_sms_user, verify_code, create_account, create_transfer



app = FastAPI()


# TODO security issue.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


routes = [
    ("/api/v1.0/send-sms", send_sms_user, "POST"),
    ("/api/v1.0/verify-code", verify_code, "POST"),

    ("/api/v1.0/account", create_account, "POST"),
    ("/api/v1.0/transfer", create_transfer, "POST"),
]

for path, handler, method in routes:
    app.add_api_route(path, handler, methods=[method])
