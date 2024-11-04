from swarm import Swarm, Agent
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from functions.yt import search_youtube_videos, get_transcript_from_prompt
from functions.functions import get_podcast_episodes_by_title, read_and_chunk_podcast, process_audio_file
from typing import List, Dict, Optional, Dict as PodcastDict

# Load environment variables
load_dotenv()

# Initialize Tavily client with API key from .env
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

print("Environment variables loaded")

client = Swarm()
print("Swarm client initialized")

class ConversationHistory:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.max_history = 10  # Adjust based on your needs

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # Keep only the last N messages to prevent context from getting too long
        if len(self.messages) > self.max_history:
            self.messages.pop(0)

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages

# Initialize conversation history
conversation_history = ConversationHistory()

class PodcastMemory:
    def __init__(self):
        self.episode_lists: Dict[str, List[Dict]] = {}
        
    def store_episodes(self, podcast_name: str, episodes: List[Dict]):
        self.episode_lists[podcast_name] = episodes
        
    def get_episodes(self, podcast_name: str) -> Optional[List[Dict]]:
        return self.episode_lists.get(podcast_name)

# Initialize podcast memory
podcast_memory = PodcastMemory()

def transfer_to_explainer(*args, **kwargs):
    """Perform an explanation using user prompt and return the response."""
    print("Transferring to explainer")
    return explainer

def transfer_to_researcher(*args, **kwargs):
    """Perform a web search using user prompt and return the response."""
    print("Transferring to researcher")
    return researcher

def transfer_to_yt_transcriber(*args, **kwargs):
    """Perform a YouTube transcript search using user prompt and return the response."""
    print("Transferring to YouTube Transcriber")
    return yt_transcriber

def transfer_to_transcript_analyst(*args, **kwargs):
    print("Transferring to Transcript Analyst")
    return transcript_analyst

def transfer_to_apple_podcast_agent(*args, **kwargs):
    """Perform a Apple Podcast search using user prompt and return the response."""
    print("Transferring to Apple Podcast Agent")
    return apple_podcast_agent

def web_search(query):
    """Perform a web search using Tavily and return the response."""
    print(f"Performing web search for: {query}")
    response = tavily_client.search(query)
    return response

def transfer_to_podcast_episode_analyzer(*args, **kwargs):
    """Transfer control to the Podcast Episode Analyzer agent."""
    print("Transferring to Podcast Episode Analyzer")
    return podcast_episode_analyzer

manager = Agent(
    name="Manager",
    instructions=(
        "You oversee the research and explanation process.\n"
        "You delegate tasks to the researcher, explainer, YouTube transcriber, transcript analyst, and Apple podcast agent.\n"
        "If you need YouTube video transcripts, delegate the task to the YouTube transcriber.\n"
        "For questions about the content of YouTube transcripts, delegate to the transcript analyst.\n"
        "For queries related to Apple podcasts, delegate to the Apple podcast agent.\n"
        "For specific podcast episode queries, ensure the Apple podcast agent shares results with the Podcast Episode Analyzer."
    ),
    functions=[
        transfer_to_researcher, 
        transfer_to_explainer, 
        transfer_to_yt_transcriber,
        transfer_to_transcript_analyst, 
        transfer_to_apple_podcast_agent,
        transfer_to_podcast_episode_analyzer,
        search_youtube_videos, 
        get_podcast_episodes_by_title
    ],
)
print("Manager created")

explainer = Agent(
    name="Explainer",
    model="o1-mini",
    instructions=(
        "I explain things in a way that is easy to understand."
    ),
)
print("Explainer created")

researcher = Agent(
    name="Researcher",
    model="gpt-4o",
    instructions=(
        "As a world-class web research agent, your primary responsibility is to conduct exhaustive and precise web searches.\n"
        "Employ cutting-edge search methodologies and tools to extract the most pertinent, current, and comprehensive information available.\n"
        "Critically evaluate the credibility and validity of each source, ensuring that all information is derived from authoritative and trustworthy origins.\n"
        "Integrate and synthesize the collected data to deliver a nuanced and in-depth understanding of the subject matter.\n"
        "Maintain a meticulous approach to detail, ensuring that all findings are accurate, relevant, and presented in a clear and concise manner."
    ),
    functions=[web_search],
)
print("Researcher created")

yt_researcher = Agent(
    name="YT Researcher",
    model="gpt-4o",
    instructions=(
        "As a specialized YouTube research agent, your primary responsibility is to conduct thorough and precise searches on YouTube.\n"
        "Utilize advanced search techniques and tools to identify the most relevant, current, and comprehensive video content available.\n"
        "Critically assess the credibility and validity of each video source, ensuring that all information is derived from authoritative and trustworthy channels.\n"
        "Analyze and synthesize the collected video data to provide a detailed and insightful understanding of the subject matter.\n"
        "Maintain a meticulous approach to detail, ensuring that all findings are accurate, relevant, and presented in a clear and concise manner."
    ),
    functions=[search_youtube_videos],
)

print("YT Researcher created")

yt_transcriber = Agent(
    name="YouTube Transcriber",
    model="gpt-4o",
    instructions=(
        "As a specialized YouTube transcript retrieval agent, your primary responsibility is to fetch and process transcripts from YouTube videos.\n"
        "When given a topic or query, search for relevant YouTube videos and retrieve their transcripts.\n"
        "Provide the full transcript to the transcript analyst for further processing."
    ),
    functions=[get_transcript_from_prompt],
)
print("YouTube Transcriber created")

transcript_analyst = Agent(
    name="Transcript Analyst",
    model="o1",
    instructions=(
        "As a transcript analyst, your role is to analyze and answer questions about YouTube video transcripts.\n"
        "You will receive transcripts from the YouTube Transcriber and user questions about the content.\n"
        "Provide concise, accurate answers based on the information in the transcripts.\n"
        "If asked for specific information, search within the transcripts to find the most relevant parts."
    ),
)
print("Transcript Analyst created")

apple_podcast_agent = Agent(
    name="Apple Podcast Agent",
    model="gpt-4o",
    instructions=(
        "As an Apple podcast specialist, your role is to handle queries related to Apple podcasts.\n"
        "You can search for podcast episodes and retrieve list of episodes.\n"
        "When a user asks about specific episodes or content, delegate to the Podcast Episode Analyzer.\n"
        "Always share the full list of episodes you find with the Podcast Episode Analyzer."
    ),
    functions=[get_podcast_episodes_by_title, transfer_to_podcast_episode_analyzer],
)
print("Apple Podcast Agent created")

podcast_episode_analyzer = Agent(
    name="Podcast Episode Analyzer",
    model="gpt-4o",
    instructions=(
        "Your role is to analyze podcast episode lists and respond to specific queries about episodes.\n"
        "When you receive a list of episodes from the Apple Podcast Agent, carefully review it and:\n"
        "1. Match specific episode titles or IDs mentioned in user queries\n"
        "2. Extract relevant episode information based on user's questions\n"
        "3. If an episode is found, provide detailed information about it\n"
        "4. If an episode isn't found, suggest similar episodes from the list\n"
        "Always maintain the episode list in your context for follow-up questions."
    ),
)

def process_question(question: str):
    print(f"Processing question: {question}")
    
    # Add the new question to history
    conversation_history.add_message("user", question)
    
    # Create the messages list with system message and conversation history
    messages = [
        {"role": "system", "content": (
            "You have access to various specialized agents including a YouTube Transcriber, "
            "Transcript Analyst, Apple Podcast Agent, and Podcast Episode Analyzer. "
            "Use them as needed based on the user's query."
        )},
    ]
    
    # Add any relevant podcast episodes from memory
    if podcast_memory.episode_lists:
        podcast_context = "Available podcast episodes:\n"
        for podcast_name, episodes in podcast_memory.episode_lists.items():
            podcast_context += f"\n{podcast_name}:\n"
            for ep in episodes:
                podcast_context += f"- {ep.get('title', 'Unknown Title')} (ID: {ep.get('id', 'Unknown ID')})\n"
        messages.append({"role": "system", "content": podcast_context})
    
    messages.extend(conversation_history.get_messages())
    
    # Run the conversation
    response = client.run(
        agent=manager,
        messages=messages,
    )
    
    # Add the response to history
    conversation_history.add_message("assistant", response.messages[-1]["content"])
    
    return response.messages[-1]["content"]
