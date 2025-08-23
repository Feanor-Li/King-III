from typing import Dict, Any
from langgraph.graph import StateGraph, START, END

from .models.state import PhotoSystemState
from .nodes import (
    UploadNode,
    ImageAnalyzerNode, 
    RefinementNode,
    iPhoneControlNode,
    PhotoCaptureNode
)


class SmartPhotoGraph:
    """LangGraph workflow for smart photo system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize nodes
        self.upload_node = UploadNode(
            upload_dir=self.config.get("upload_dir", "/tmp/smart_photo_uploads")
        )
        self.analyzer_node = ImageAnalyzerNode()
        self.refinement_node = RefinementNode()
        self.control_node = iPhoneControlNode(
            iphone_api_endpoint=self.config.get("iphone_api_endpoint")
        )
        self.capture_node = PhotoCaptureNode(
            capture_api_endpoint=self.config.get("capture_api_endpoint"),
            output_dir=self.config.get("output_dir", "/tmp/smart_photo_output")
        )
        
        # Create and compile graph
        self.compiled_graph = self._create_graph()
    
    def _create_graph(self):
        """Create LangGraph workflow"""
        # Create StateGraph
        graph = StateGraph(PhotoSystemState)
        
        # Define node functions
        async def upload_step(state: PhotoSystemState) -> PhotoSystemState:
            return await self.upload_node.execute(state)
        
        async def analyze_step(state: PhotoSystemState) -> PhotoSystemState:
            return await self.analyzer_node.execute(state)
        
        async def refine_step(state: PhotoSystemState) -> PhotoSystemState:
            return await self.refinement_node.execute(state)
        
        async def control_step(state: PhotoSystemState) -> PhotoSystemState:
            return await self.control_node.execute(state)
        
        async def capture_step(state: PhotoSystemState) -> PhotoSystemState:
            return await self.capture_node.execute(state)
        
        # Add nodes to graph
        graph.add_node("upload", upload_step)
        graph.add_node("analyze", analyze_step)
        graph.add_node("refine", refine_step)
        graph.add_node("control", control_step)
        graph.add_node("capture", capture_step)
        
        # Define workflow paths
        graph.add_edge(START, "upload")
        graph.add_edge("upload", "analyze")
        graph.add_edge("analyze", "refine")
        
        # Conditional edges: after refinement may need re-control or direct capture
        def should_recapture(state: PhotoSystemState) -> str:
            if state.current_step == "capture_ready":
                return "control"
            elif state.current_step == "completed":
                return END
            else:
                return "capture"
        
        graph.add_conditional_edges(
            "refine",
            should_recapture,
            {
                "control": "control",
                "capture": "capture",
                END: END
            }
        )
        
        graph.add_edge("control", "capture")
        graph.add_edge("capture", END)
        
        return graph.compile()
    
    async def run(self, initial_state: PhotoSystemState) -> PhotoSystemState:
        """Run complete workflow"""
        try:
            # Run compiled graph
            final_state = await self.compiled_graph.ainvoke(initial_state)
            return final_state
        except Exception as e:
            print(f"Workflow execution failed: {str(e)}")
            # Return state with error message
            initial_state.error_message = f"Workflow execution failed: {str(e)}"
            return initial_state
    
    async def run_single_step(self, state: PhotoSystemState, step: str) -> PhotoSystemState:
        """Run single step"""
        try:
            if step == "upload":
                return await self.upload_node.execute(state)
            elif step == "analyze":
                return await self.analyzer_node.execute(state)
            elif step == "refine":
                return await self.refinement_node.execute(state)
            elif step == "control":
                return await self.control_node.execute(state)
            elif step == "capture":
                return await self.capture_node.execute(state)
            else:
                raise ValueError(f"Unknown step: {step}")
        except Exception as e:
            print(f"Step {step} execution failed: {str(e)}")
            state.error_message = f"Step {step} execution failed: {str(e)}"
            return state
    
    async def process_refinement(self, state: PhotoSystemState, user_input: str) -> PhotoSystemState:
        """Process user's refinement input"""
        try:
            # Use refinement node to process user input
            updated_state = await self.refinement_node.process_user_input(state, user_input)
            return updated_state
        except Exception as e:
            print(f"Failed to process refinement: {str(e)}")
            state.error_message = f"Failed to process refinement: {str(e)}"
            return state
    
    def get_graph_visualization(self) -> str:
        """Get graph visualization description"""
        return """
        Smart Photo System Workflow:
        
        START → upload (Upload Image)
          ↓
        analyze (Analyze Image)
          ↓ 
        refine (Prepare Refinement)
          ↓
        [Conditional Branch]
          ↓
        control (Control iPhone) → capture (Capture) → END
        
        Loop Support: Users can perform multiple refinements, each will re-call control and capture.
        """
    
    def get_supported_steps(self) -> list:
        """Get list of supported steps"""
        return ["upload", "analyze", "refine", "control", "capture"]
