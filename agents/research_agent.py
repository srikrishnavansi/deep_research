from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from tavily import TavilyClient
from typing import List, Dict, Any
from utils.llm_setup import create_gemini_llm
import json
from pathlib import Path
import logging
from datetime import datetime

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
        self.results_dir = Path(settings.results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, query: str, depth: str) -> Dict[str, Any]:
        """Execute the research process"""
        try:
            if not query or not isinstance(query, str):
                raise ValueError("Query must be a non-empty string")
            
            # Ensure depth is correctly set
            search_depth = "advanced" if depth.lower() == "advanced" else "basic"
            logger.debug(f"Using Tavily search_depth: {search_depth}")
            
            results = self._tavily_search(query, search_depth)
            
            if isinstance(results, dict) and "error" in results:
                raise Exception(f"Search error: {results['error']}")
            
            # Add metadata to results
            results_with_metadata = {
                "query": query,
                "depth": search_depth,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "user": "srikrishnavansi",  # Using the current user's login
                "results": results
            }
            
            # Store results
            self._store_results(results_with_metadata)
            
            return results_with_metadata
            
        except Exception as e:
            logger.error(f"Research execution failed: {str(e)}", exc_info=True)
            raise Exception(f"Research execution failed: {str(e)}")
    
    def _tavily_search(self, query: str, search_depth: str) -> Dict[str, Any]:
        """Execute search using Tavily API with correct depth parameter"""
        try:
            response = self.tavily_client.search(
                query=query,
                search_depth=search_depth
            )
            logger.debug(f"Tavily API response received")
            return response
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}", exc_info=True)
            error_msg = str(e)
            return {"error": error_msg}
    
    def _store_results(self, results: Dict[str, Any]) -> None:
        """Store research results with timestamp and metadata"""
        try:
            # Create filename with timestamp and query
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            sanitized_query = "".join(c for c in results["query"][:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"research_{timestamp}_{sanitized_query}.json"
            
            # Ensure results directory exists
            self.results_dir.mkdir(parents=True, exist_ok=True)
            
            # Save results
            file_path = self.results_dir / filename
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Results stored in: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to store results: {str(e)}", exc_info=True)
            # Don't raise the exception - just log it
            # This way, the research results can still be returned even if storage fails
