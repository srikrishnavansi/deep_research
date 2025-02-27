from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from tavily import TavilyClient
from typing import List, Dict, Any
from utils.llm_setup import create_gemini_llm
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self, settings):
        self.settings = settings
        api_key = settings.tavily_api_key.get_secret_value()
        self.tavily_client = TavilyClient(api_key=api_key)
        
        self.llm = create_gemini_llm(
            api_key=settings.google_api_key.get_secret_value(),
            model_name=settings.research_agent_model,
            temperature=0.7
        )
        
        # Ensure results directory exists
        Path(settings.results_dir).mkdir(parents=True, exist_ok=True)
    
    def execute(self, query: str, depth: str) -> Dict[str, Any]:
        """Execute the research process"""
        try:
            if not query or not isinstance(query, str):
                raise ValueError("Query must be a non-empty string")
            
            # Convert depth to Tavily's format
            tavily_depth = "advanced" if depth.lower() == "deep" else "basic"
            logger.debug(f"Using Tavily search_depth: {tavily_depth}")
            
            results = self._tavily_search(query, tavily_depth)
            
            if isinstance(results, dict) and "error" in results:
                raise Exception(f"Search error: {results['error']}")
                
            self._store_results(results)
            return results
            
        except Exception as e:
            logger.error(f"Research execution failed: {str(e)}", exc_info=True)
            raise Exception(f"Research execution failed: {str(e)}")
    
    def _tavily_search(self, query: str, search_depth: str) -> Dict[str, Any]:
        """Execute search using Tavily API with correct depth parameter"""
        try:
            response = self.tavily_client.search(
                query=query,
                search_depth=search_depth  # Using 'basic' or 'advanced'
            )
            logger.debug(f"Tavily API response received")
            return response
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}", exc_info=True)
            error_msg = str(e)
            return {"error": error_msg}
    
    def _store_results(self, results: Dict[str, Any]) -> bool:
        """Store intermediate results to configured storage"""
        try:
            results_file = Path(self.settings.results_dir) / "research_results.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)
            
            with results_file.open("a") as f:
                json.dump(results, f)
                f.write("\n")
            return True
        except Exception as e:
            logger.error(f"Failed to store results: {str(e)}", exc_info=True)
            return False