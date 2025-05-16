from fastapi import APIRouter, HTTPException, status, WebSocket, Response
from core import logger
from core.apis.schemas.request import RequestCall
import plivo
import os
from dotenv import load_dotenv
import json, asyncio


logging = logger(__name__)

load_dotenv(override=True)


plivo_router = APIRouter()

print(os.getenv("PLIVO_AUTH_ID"))

client = plivo.RestClient(os.getenv("PLIVO_AUTH_ID"),os.getenv("PLIVO_AUTH_TOKEN"))

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
        response = client.calls.create(
            from_=os.getenv("PLIVO_FROM_NUMBER"),
            to_='+919156685436',
            answer_url=os.getenv("PLIVO_ANSWER_XML"),
            answer_method='POST',)
        return {
            "status": "success",
            "message": "Call initiated successfully",
            "call_uuid": response['api_id'],
        }
    except Exception as e:
        logging.error(f"Error in create_call_disposition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )

@plivo_router.post("/webhook")
def webhook():
    """
    [API for plivo webhook]
    """
    xml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Record 
                action="https://pegasus-immortal-stud.ngrok-free.app/get_recording/" 
                redirect="false" 
                recordSession="true" 
                maxLength="3600" 
            />
            <Stream 
                streamTimeout="86400" 
                keepCallAlive="true" 
                bidirectional="true" 
                contentType="audio/x-mulaw;rate=8000" 
                audioTrack="inbound" 
                statusCallbackUrl="https://pegasus-immortal-stud.ngrok-free.app/callbacks"
            >
                wss://pegasus-immortal-stud.ngrok-free.app/media-stream
            </Stream>
        </Response>
    """
    return Response(content=xml.strip(), media_type="application/xml")
    
        
@plivo_router.websocket("/media-stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    [WebSocket endpoint for real-time communication]

    Args:
        websocket (WebSocket): [WebSocket connection object]
    
    Returns:
        [None]: [None]
    """
    try:
        # Accept connection only once
        await websocket.accept()
        logging.info("Client connected to WebSocket")
        
        # Initialize call_id and stream_id
        call_id = None
        stream_id = None
        
        # Process incoming messages
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            
            try:
                data = json.loads(message)
                event_type = data.get('event')
                
                if event_type == "media":
                    # Handle media event
                    logging.debug("Received media event")
                    audio_payload = data['media']['payload']
                    # Process audio with pipecat
                    # Example: await pipecat_bot(websocket, call_id, audio_payload)
                    
                elif event_type == "start":
                    # Handle start event
                    stream_id = data['start']['streamId']
                    call_id = data['start']['callId']
                    logging.info(f"Incoming stream started - streamId: {stream_id}, callId: {call_id}")
                    
                elif event_type == "stop":
                    # Handle stop event
                    logging.info(f"Incoming stream stopped - streamId: {data['stop']['streamId']}")
                    # Signal end of processing
                    
                else:
                    logging.info(f"Received non-media event: {event_type}")
                    
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing message: {e}, Message: {message}")
                
    except WebSocketDisconnect:
        logging.info("Client disconnected normally")
    except Exception as e:
        logging.error(f"Error in websocket_endpoint: {e}")
        # Don't raise HTTPException for WebSockets - connection is already established
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1011, reason=f"Internal server error")
            
            
@plivo_router.post("/get_recording/")
async def get_recording():
    """
    [API for getting the recording]

    Args:
        request (Request): [Request object]
    
    Returns:
        [JSON]: [Response containing the status of the recording]
    """
    try:
      
        
        return {"status": "success", "message": "Recording processed successfully"}
    except Exception as e:
        logging.error(f"Error in get_recording: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
        
@plivo_router.post("/callbacks")
async def callbacks():
    """
    [API for handling callbacks]

    Args:
        request (Request): [Request object]
    
    Returns:
        [JSON]: [Response containing the status of the callback]
    """
    try:
        pass
    except Exception as e:
        logging.error(f"Error in callbacks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )