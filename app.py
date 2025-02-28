import streamlit as st
from agents.research_agent import ResearchAgent
from agents.synthesis_agent import SynthesisAgent
from config import settings, SearchDepth
import time
from datetime import datetime
import json
from pathlib import Path
import plotly.graph_objects as go
from rich.console import Console
import sys
from io import StringIO
import logging
from streamlit_lottie import st_lottie

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CURRENT_TIMESTAMP = "2025-02-28 13:13:43"
CURRENT_USER = "srikrishnavansi"

def load_lottie_animation():
    """Load local Lottie animation file"""
    try:
        with open('static/animations/research_animation.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading animation: {str(e)}")
        return None

def initialize_session_state():
    """Initialize session state variables"""
    if 'research_history' not in st.session_state:
        st.session_state.research_history = []
    if 'current_process' not in st.session_state:
        st.session_state.current_process = None
    if 'progress' not in st.session_state:
        st.session_state.progress = 0

def inject_custom_css():
    """Inject custom CSS"""
    with open('static/css/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def create_progress_chart(progress):
    """Create a circular progress chart using plotly"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=progress,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': "#fafafa"},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "#1f2937",
            'bordercolor': "#374151",
            'steps': [
                {'range': [0, 50], 'color': "rgba(59, 130, 246, 0.2)"},
                {'range': [50, 100], 'color': "rgba(59, 130, 246, 0.4)"}
            ],
        },
        title={'text': "Research Progress", 'font': {'color': "#fafafa"}}
    ))
    
    fig.update_layout(
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#fafafa"}
    )
    return fig

def display_research_process(title, description, progress):
    """Display research process with animation"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
            <div class="process-step">
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.plotly_chart(create_progress_chart(progress), use_container_width=True)

def execute_research(query: str, depth: str):
    """Execute research process with UI updates"""
    try:
        # Initialize agents
        research_agent = ResearchAgent(settings)
        synthesis_agent = SynthesisAgent(settings)
        
        # Research Phase
        st.session_state.progress = 25
        display_research_process(
            "🔍 Research Phase",
            "Gathering information from various sources...",
            st.session_state.progress
        )
        
        research_start = time.time()
        research_results = research_agent.execute(query, depth)
        research_time = time.time() - research_start
        
        # Update progress
        st.session_state.progress = 75
        display_research_process(
            "📊 Processing Data",
            "Analyzing and structuring gathered information...",
            st.session_state.progress
        )
        
        # Synthesis Phase
        synthesis_start = time.time()
        synthesis = synthesis_agent.process_results(research_results, query)
        synthesis_time = time.time() - synthesis_start
        
        # Update progress
        st.session_state.progress = 100
        display_research_process(
            "✅ Research Complete",
            "Final results ready!",
            st.session_state.progress
        )
        
        # Store results
        result = {
            "query": query,
            "timestamp": CURRENT_TIMESTAMP,
            "user": CURRENT_USER,
            "research_time": f"{research_time:.2f}s",
            "synthesis_time": f"{synthesis_time:.2f}s",
            "depth": depth,
            "results": synthesis
        }
        
        st.session_state.research_history.append(result)
        return result
        
    except Exception as e:
        st.error(f"Error during research: {str(e)}")
        logger.error(f"Research error: {str(e)}", exc_info=True)
        return None

def main():
    st.set_page_config(
        page_title="Deep Research Assistant",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    inject_custom_css()
    
    # Load animation
    animation_data = load_lottie_animation()
    
    # Sidebar
    with st.sidebar:
        st.title("🔬 Research Settings")
        
        # Display Lottie animation in sidebar
        if animation_data:
            st_lottie(
                animation_data,
                speed=1,
                reverse=False,
                loop=True,
                quality="high",
                height=200,
                key="sidebar_animation"
            )
        
        # Depth selector
        depth = st.select_slider(
            "Research Depth",
            options=[SearchDepth.BASIC, SearchDepth.ADVANCED],
            value=SearchDepth.BASIC,
            format_func=lambda x: x.value,
            help="Choose the depth of research"
        )
        
        st.markdown("---")
        
        # History section
        st.markdown("""
        <div class="history-header slide-up">
            <h3>📚 Research History</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for idx, item in enumerate(reversed(st.session_state.research_history)):
            with st.expander(f"🔍 {item['query'][:30]}...", expanded=idx==0):
                st.markdown(f"""
                <div class="history-item fade-in">
                    <p><strong>Depth:</strong> {item['depth']}</p>
                    <p><strong>Time:</strong> {item['timestamp']}</p>
                    <p><strong>Research:</strong> {item['research_time']}</p>
                    <p><strong>Synthesis:</strong> {item['synthesis_time']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Main content
    st.markdown("""
    <div class="main-header slide-up">
        <h1>🔬 Deep Research Assistant</h1>
        <p class="subtitle">Conduct comprehensive research powered by AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display main Lottie animation
    if animation_data:
        st_lottie(
            animation_data,
            speed=1,
            reverse=False,
            loop=True,
            quality="high",
            height=300,
            key="main_animation"
        )
    
    # Current session info
    st.markdown(f"""
    <div class="session-info fade-in">
        <p><strong>Session Time (UTC):</strong> {CURRENT_TIMESTAMP}</p>
        <p><strong>User:</strong> {CURRENT_USER}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Query input
    query = st.text_input(
        "Research Query",
        placeholder="Enter your research topic...",
        help="Enter the topic you want to research"
    )
    
    # Execute button
    if st.button("Start Research", type="primary"):
        if not query:
            st.warning("Please enter a research query")
            return
            
        with st.spinner("🔍 Conducting research..."):
            result = execute_research(query, depth.value)
            
        if result:
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["📊 Summary", "📋 Details", "🔍 Raw Data"])
            
            with tab1:
                st.markdown("""
                    <div class="results-summary slide-up">
                        <h3>Research Summary</h3>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f'<div class="summary-content fade-in">{result["results"]["synthesis"]}</div>', 
                           unsafe_allow_html=True)
            
            with tab2:
                st.markdown("""
                    <div class="results-details slide-up">
                        <h3>Research Details</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        <div class="metric-container fade-in">
                            <p class="metric-label">Research Time</p>
                            <h4 class="metric-value">{result['research_time']}</h4>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class="metric-container fade-in">
                            <p class="metric-label">Synthesis Time</p>
                            <h4 class="metric-value">{result['synthesis_time']}</h4>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="details-card slide-up">
                        <p><strong>Query:</strong> {result['query']}</p>
                        <p><strong>Depth:</strong> {result['depth']}</p>
                        <p><strong>Timestamp:</strong> {result['timestamp']}</p>
                        <p><strong>User:</strong> {result['user']}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with tab3:
                st.json(result)

if __name__ == "__main__":
    main()