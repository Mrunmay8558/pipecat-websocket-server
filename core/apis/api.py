from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Response

from core.apis.routes.plivo_router import plivo_router

app = FastAPI(
    title="Agent ICICI",
    description="Agent ICICI is a conversational agent that can assist with various tasks.",
)


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    # Security Headers
    response.headers["X-Frame-Options"] = "DENY" 
    response.headers["X-Content-Type-Options"] = "nosniff" 
    response.headers["X-XSS-Protection"] = "1; mode=block" 
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"  
    )
   
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=()"
    )
    response.headers["Cache-Control"] = "no-store"  
    response.headers["Server"] = "Custom Server"  

    method = request.method

    if method == "GET":
        response.headers["Access-Control-Allow-Methods"] = "GET"
    elif method == "POST":
        response.headers["Access-Control-Allow-Methods"] = "POST"
    elif method == "PUT":
        response.headers["Access-Control-Allow-Methods"] = "PUT"
    elif method == "DELETE":
        response.headers["Access-Control-Allow-Methods"] = "DELETE"

    return response

@app.get("/set-cookie")
def set_cookie(response: Response):
    response.set_cookie(
        key="session",
        value="value",
        httponly=True,  # Prevents JavaScript access
        secure=True,  # Only sent over HTTPS
        samesite="strict",  # CSRF protection
        max_age=1800,  # 30 minutes
    )


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plivo_router, tags=["Plivo"])

@app.get("/")
def ping():
    """[ping func provides a health check]

    Returns:
        [dict]: [success response for health check]
    """
    return {"response": "ping to CliniQ360 backend server successful"}
