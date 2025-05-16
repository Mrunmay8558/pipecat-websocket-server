import asyncio
import os
import sys
import certifi
import ssl

from dotenv import load_dotenv
from loguru import logger
from fastapi import WebSocket

from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketTransport,
    FastAPIWebsocketParams
)
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import BotInterruptionFrame, EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.serializers.protobuf import ProtobufFrameSerializer
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.network.websocket_server import (
    WebsocketServerParams,
    WebsocketServerTransport,
)
from core.utils.prompts.agent_icici import icici_prompt
from pipecat.services.mem0.memory import Mem0MemoryService
from core.utils.prompts.agent_icici import icici_prompt
from deepgram import LiveOptions
from core.utils.plivo.plivo_serializer import PlivoFrameSerializer
from core.utils.plivo.plivo_session_handler import SessionTimeoutHandler


# Set SSL certificate environment variables
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Load environment variables
load_dotenv(override=True)

# Configure logging
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


    
    

llm = OpenAILLMService(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"),live_options= LiveOptions(
        model="nova-2-general",
        language="en-US",
        smart_format=True,
        vad_events=True,
        encoding="mu"
        
    ))
    
stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"),
                         live_options=LiveOptions(
                            encoding="linear16",
                            language="en-IN",
                            model="nova-2",
                            sample_rate=16000,
                            channels=1,
                            interim_results=False,
                            smart_format=True,
                            punctuate=True,
                            profanity_filter=True,
                            vad_events=False,
                            ),
                        )
    
tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="791d5162-d5eb-40f0-8189-f19db44611d8",
    )
    
memory = Mem0MemoryService(
        api_key=os.getenv("MEMO_API_KEY"),
        user_id="user123",
    )

messages = [
        {
            "role": "system",
            "content": icici_prompt,
        },
    ]

context = OpenAILLMContext(messages)
context_aggregator = llm.create_context_aggregator(context)


async def pipecat_bot(websocket_client, stream_id: str):
    """
    Function to run the pipecat bot.
    This function initializes the bot and starts the FastAPI server.
    It sets up the necessary components such as the pipeline, transport, and services.
    """
    
    try:
        transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_out_enabled=True,
            add_wav_header=False,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            vad_audio_passthrough=True,
            serializer=PlivoFrameSerializer(stream_id),
        ),
    )

        pipeline = Pipeline([
            transport.input(),    
            stt,                 
            llm,                  
            tts,                 
            transport.output()   
        ])

        task = PipelineTask(pipeline)
        
        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            messages.append({"role": "system", "content": "Please introduce yourself to the user."})
            await task.queue_frames([context_aggregator.user().get_context_frame()])

        @transport.event_handler("on_session_timeout")
        async def on_session_timeout(transport, client):
            logger.info(f"Entering in timeout for {client.remote_address}")
            timeout_handler = SessionTimeoutHandler(task, tts)
            await timeout_handler.handle_timeout(client.remote_address)
            
        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            logger.info("Client disconnected")
            await task.queue_frames([EndFrame()])
        
        runner = PipelineRunner(handle_sigint=False)
        await runner.run(task)
    except Exception as e:
        logger.error(f"Error in pipecat_bot: {e}")
        return False
    
    
    
    