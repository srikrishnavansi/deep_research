from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any
from datetime import datetime
import json
from pathlib import Path
import logging
from utils.llm_setup import create_gemini_llm

logger = logging.getLogger(__name__)

class SynthesisAgent:
    def __init__(self, settings):
        self.settings = settings
        self.llm = create_gemini_llm(
            api_key=settings.google_api_key.get_secret_value(),
            model_name=settings.synthesis_agent_model,
            temperature=0.7
        )

    def process_results(self, research_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Process research results and generate a synthesis"""
        try:
            # Define the prompt template using the new ChatPromptTemplate
            prompt = ChatPromptTemplate.from_messages([
                ("human", """
                Based on the following research data, provide a comprehensive synthesis about: {query}

                Research Data:
                {research_data}

                Please provide:
                1. A summary of the main findings
                2. Key points and insights
                3. Any relevant applications or implications

                Format the response in a clear, well-structured manner.
                """)
            ])

            # Create the chain using the new pattern
            chain = prompt | self.llm | StrOutputParser()

            # Execute the chain
            result = chain.invoke({
                "query": query,
                "research_data": json.dumps(research_data, indent=2)
            })

            # Format the final output
            synthesis = {
                "query": query,
                "synthesis": result,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "metadata": {
                    "model": self.settings.synthesis_agent_model,
                    "user": "srikrishnavansi"
                }
            }

            # Store the synthesis
            self._store_synthesis(synthesis)

            return synthesis

        except Exception as e:
            logger.error(f"Error in synthesis: {str(e)}", exc_info=True)
            raise

    def _store_synthesis(self, synthesis: Dict[str, Any]) -> None:
        """Store the synthesis results"""
        try:
            results_dir = Path(self.settings.results_dir)
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Use formatted timestamp for filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_path = results_dir / f"synthesis_{timestamp}.json"
            
            with file_path.open('w') as f:
                json.dump(synthesis, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to store synthesis: {str(e)}", exc_info=True)