from fastapi import APIRouter, HTTPException, status, WebSocket
from core import logger
from core.apis.schemas.request import RequestCall

logging = logger(__name__)

plivo_router = APIRouter()

@plivo_router.post("/v1/call_disposition")
def create_call_disposition(call_request:RequestCall):
    """
    [API route for creating a call disposition]

    Args:
        call_request (RequestCall): [Call Request object containing mobile number and full name]
        
    Raises:
        HTTPException: [If the mobile number is not valid or if the call fails]
    
    Returns:
        [JSON]: [Response containing the status of the call]
    """
    
    try:
        pass
    except Exception as e:
        logging.error(f"Error in create_call_disposition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
        
@plivo_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    [WebSocket endpoint for real-time communication]

    Args:
        websocket (WebSocket): [WebSocket connection object]
        
    Raises:
        HTTPException: [If the WebSocket connection fails]
    
    Returns:
        [None]: [None]
    """
    await websocket.accept()
    logging.info("Client connected to WebSocket")
    
    try:
        await websocket.accept()
        while True:
            pass
            
        
        
       
    except Exception as e:
        logging.error(f"Error in websocket_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
    
    