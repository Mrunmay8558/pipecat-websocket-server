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
from prompts.agent_icici import icici_prompt
from pipecat.services.mem0.memory import Mem0MemoryService
from core.utils.prompts.agent_icici import icici_prompt


# Set SSL certificate environment variables
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Load environment variables
load_dotenv(override=True)

# Configure logging
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

class SessionTimeoutHandler:
    """Handles actions to be performed when a session times out.
    Inputs:
    - task: Pipeline task (used to queue frames).
    - tts: TTS service (used to generate speech output).
    """

    def __init__(self, task, tts):
        self.task = task
        self.tts = tts
        self.background_tasks = set()

    async def handle_timeout(self, client_address):
        """Handles the timeout event for a session."""
        try:
            logger.info(f"Connection timeout for {client_address}")

            await self.task.queue_frames([BotInterruptionFrame()])

            await self.tts.say(
                "I'm sorry, we are ending the call now. Please feel free to reach out again if you need assistance."
            )

            end_call_task = asyncio.create_task(self._end_call())
            self.background_tasks.add(end_call_task)
            end_call_task.add_done_callback(self.background_tasks.discard)
        except Exception as e:
            logger.error(f"Error during session timeout handling: {e}")

    async def _end_call(self):
        """Completes the session termination process after the TTS message."""
        try:
            # Wait for a duration to ensure TTS has completed
            await asyncio.sleep(15)

            # Queue both BotInterruptionFrame and EndFrame to conclude the session
            await self.task.queue_frames([BotInterruptionFrame(), EndFrame()])

            logger.info("TTS completed and EndFrame pushed successfully.")
        except Exception as e:
            logger.error(f"Error during call termination: {e}")
            
llm = OpenAILLMService(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
    
stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    
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


async def pipecat_bot(websocket: WebSocket, call_id: str, audio_packet: str):
    """
    Function to run the pipecat bot.
    This function initializes the bot and starts the FastAPI server.
    It sets up the necessary components such as the pipeline, transport, and services.
    """
    
    try:
        transport = FastAPIWebsocketTransport(
            websocket=websocket,
            params=FastAPIWebsocketParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            )
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
        
        await PipelineRunner().run(task)
    except Exception as e:
        logger.error(f"Error in pipecat_bot: {e}")
        return False
    
    
    
    