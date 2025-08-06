"""
Tool Registry and Base Tool Classes for Pareng Boyong.

This module provides the foundation for tool management and execution
within the Filipino AI agent system.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass
import json
import importlib
from pathlib import Path

from .config import ParengBoyongConfig
from .exceptions import ToolError


@dataclass
class ToolResponse:
    """Standard response format for tool execution."""
    success: bool
    content: Any
    cost: float = 0.0
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseTool(ABC):
    """
    Base class for all Pareng Boyong tools.
    
    All tools inherit from this class and implement the execute method.
    This ensures consistent interface and behavior across all tools.
    """
    
    def __init__(self, config: ParengBoyongConfig):
        """
        Initialize the tool.
        
        Args:
            config: Pareng Boyong configuration
        """
        self.config = config
        self.name = self.__class__.__name__.lower().replace('tool', '')
        self.enabled = True
        self.cost_estimate = 0.0
        self.category = "general"
        self.description = "Base tool implementation"
        self.requirements = []  # Required API keys or dependencies
    
    @abstractmethod
    def execute(self, message: Dict[str, Any], context: Dict[str, Any]) -> ToolResponse:
        """
        Execute the tool's main functionality.
        
        Args:
            message: Processed user message
            context: Current conversation context
            
        Returns:
            ToolResponse with results
        """
        pass
    
    def estimate_cost(self, message: Dict[str, Any]) -> float:
        """
        Estimate the cost of executing this tool.
        
        Args:
            message: User message to analyze
            
        Returns:
            Estimated cost in USD
        """
        return self.cost_estimate
    
    def validate_requirements(self) -> bool:
        """
        Validate that all requirements are met for this tool.
        
        Returns:
            True if all requirements are satisfied
        """
        for requirement in self.requirements:
            if requirement.startswith("api_key:"):
                api_key = requirement.split(":")[1]
                if not self.config.get_api_key(api_key):
                    return False
            # Add other requirement types as needed
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "enabled": self.enabled,
            "cost_estimate": self.cost_estimate,
            "requirements": self.requirements,
            "requirements_met": self.validate_requirements()
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(enabled={self.enabled})"


class CostOptimizedVideoGeneratorTool(BaseTool):
    """Cost-optimized video generation tool - always tries FREE first."""
    
    def __init__(self, config: ParengBoyongConfig):
        super().__init__(config)
        self.category = "multimodal"
        self.description = "Generate videos using FREE services first, then paid alternatives"
        self.cost_estimate = 0.0  # Aims for FREE
    
    def execute(self, message: Dict[str, Any], context: Dict[str, Any]) -> ToolResponse:
        """Execute cost-optimized video generation."""
        try:
            prompt = message.get('content', '')
            
            # Try FREE services first
            result = self._try_free_services(prompt)
            if result['success']:
                return ToolResponse(
                    success=True,
                    content=result,
                    cost=0.0,
                    metadata={"service": "free", "method": result['method']}
                )
            
            # Fallback to low-cost paid services
            result = self._try_paid_services(prompt)
            return ToolResponse(
                success=result['success'],
                content=result,
                cost=result.get('cost', 0.01),
                metadata={"service": "paid", "method": result.get('method')}
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                content=None,
                error=str(e)
            )
    
    def _try_free_services(self, prompt: str) -> Dict[str, Any]:
        """Try FREE video generation services."""
        # Placeholder for actual implementation
        return {
            "success": True,
            "method": "comfyui_local",
            "video_url": f"generated_video_{hash(prompt)}.mp4",
            "message": "Generated using FREE ComfyUI service!"
        }
    
    def _try_paid_services(self, prompt: str) -> Dict[str, Any]:
        """Try low-cost paid video generation services."""
        # Placeholder for actual implementation
        return {
            "success": True,
            "method": "replicate_cogvideox",
            "cost": 0.008,
            "video_url": f"paid_video_{hash(prompt)}.mp4",
            "message": "Generated using cost-optimized paid service"
        }


class Imagen4GeneratorTool(BaseTool):
    """Google Imagen 4 Fast image generation tool."""
    
    def __init__(self, config: ParengBoyongConfig):
        super().__init__(config)
        self.category = "multimodal"
        self.description = "Generate images using Google Imagen 4 Fast"
        self.cost_estimate = 0.003
        self.requirements = ["api_key:google"]
    
    def execute(self, message: Dict[str, Any], context: Dict[str, Any]) -> ToolResponse:
        """Execute image generation with Google Imagen 4."""
        try:
            prompt = message.get('content', '')
            
            # Placeholder for actual Google Imagen 4 implementation
            result = {
                "success": True,
                "image_url": f"imagen4_{hash(prompt)}.jpg",
                "resolution": "1024x1024",
                "model": "Google Imagen 4 Fast",
                "cost": 0.003
            }
            
            return ToolResponse(
                success=True,
                content=result,
                cost=0.003,
                metadata={"model": "imagen4_fast", "provider": "google"}
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                content=None,
                error=str(e)
            )


class SystemSelfAwarenessTool(BaseTool):
    """System health monitoring and self-awareness tool."""
    
    def __init__(self, config: ParengBoyongConfig):
        super().__init__(config)
        self.category = "system"
        self.description = "Monitor system health and perform risk assessment"
        self.cost_estimate = 0.0  # FREE
    
    def execute(self, message: Dict[str, Any], context: Dict[str, Any]) -> ToolResponse:
        """Execute system health check."""
        try:
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_data = {
                "healthy": cpu_percent < 90 and memory.percent < 85,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "warnings": []
            }
            
            # Add warnings
            if cpu_percent > 90:
                health_data["warnings"].append("High CPU usage detected")
            if memory.percent > 85:
                health_data["warnings"].append("High memory usage detected")
            if disk.percent > 90:
                health_data["warnings"].append("Low disk space")
            
            return ToolResponse(
                success=True,
                content=health_data,
                cost=0.0,
                metadata={"type": "health_check"}
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                content=None,
                error=str(e)
            )


class ToolRegistry:
    """
    Registry for managing all available tools in Pareng Boyong.
    
    Handles tool loading, selection, and execution with cost optimization.
    """
    
    def __init__(self, config: ParengBoyongConfig):
        """
        Initialize tool registry.
        
        Args:
            config: Pareng Boyong configuration
        """
        self.config = config
        self.tools: Dict[str, BaseTool] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}
        
    def load_tools(self):
        """Load all available tools.""" 
        # Register built-in tools
        self._register_builtin_tools()
        
        # Load enabled tools
        for tool_name in self.config.enabled_tools:
            if tool_name in self._tool_classes:
                try:
                    tool_class = self._tool_classes[tool_name]
                    tool_instance = tool_class(self.config)
                    
                    # Check if requirements are met
                    if tool_instance.validate_requirements():
                        self.tools[tool_name] = tool_instance
                    else:
                        print(f"⚠️ Tool {tool_name} requirements not met, skipping")
                        
                except Exception as e:
                    print(f"❌ Failed to load tool {tool_name}: {e}")
    
    def _register_builtin_tools(self):
        """Register built-in tool classes."""
        self._tool_classes.update({
            "cost_optimized_video_generator": CostOptimizedVideoGeneratorTool,
            "imagen4_generator": Imagen4GeneratorTool,
            "system_self_awareness": SystemSelfAwarenessTool,
        })
    
    def select_tools(self, intent: str, cost_budget: float = 0.01) -> List[str]:
        """
        Select appropriate tools based on intent and budget.
        
        Args:
            intent: Request intent (video_generation, image_generation, etc.)
            cost_budget: Available budget
            
        Returns:
            List of tool names in priority order
        """
        available_tools = []
        
        # Get tools for this intent
        for tool_name, tool in self.tools.items():
            if self._tool_matches_intent(tool, intent):
                estimated_cost = tool.estimate_cost({})
                if estimated_cost <= cost_budget:
                    available_tools.append((tool_name, estimated_cost))
        
        # Sort by cost (FREE first, then lowest cost)
        available_tools.sort(key=lambda x: x[1])
        
        return [tool_name for tool_name, cost in available_tools]
    
    def _tool_matches_intent(self, tool: BaseTool, intent: str) -> bool:
        """Check if a tool matches the given intent."""
        intent_mapping = {
            "video_generation": ["cost_optimized_video_generator", "trending_video_generator", "advanced_video_generator"],
            "image_generation": ["imagen4_generator", "multimedia_generator", "image_generator"],
            "audio_generation": ["filipino_tts", "audio_studio", "music_generator"],
            "code_execution": ["enhanced_code_execution", "code_execution_tool"],
            "system_check": ["system_self_awareness", "comprehensive_system_test"],
            "general_chat": ["multimodal_coordinator", "enhanced_ui_renderer"]
        }
        
        matching_tools = intent_mapping.get(intent, [])
        return tool.name in matching_tools or any(keyword in tool.name for keyword in matching_tools)
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a specific tool by name."""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all loaded tools with their information."""
        return [tool.get_info() for tool in self.tools.values()]
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """Get all tools in a specific category."""
        return [tool for tool in self.tools.values() if tool.category == category]
    
    def execute_tool(self, tool_name: str, message: Dict[str, Any], context: Dict[str, Any]) -> ToolResponse:
        """
        Execute a specific tool.
        
        Args:
            tool_name: Name of tool to execute
            message: User message
            context: Current context
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResponse(
                success=False,
                content=None,
                error=f"Tool '{tool_name}' not found or not loaded"
            )
        
        if not tool.enabled:
            return ToolResponse(
                success=False,
                content=None,
                error=f"Tool '{tool_name}' is disabled"
            )
        
        try:
            return tool.execute(message, context)
        except Exception as e:
            return ToolResponse(
                success=False,
                content=None,
                error=f"Tool execution failed: {str(e)}"
            )
    
    def __len__(self) -> int:
        return len(self.tools)
    
    def __str__(self) -> str:
        return f"ToolRegistry({len(self.tools)} tools loaded)"
    
    def __repr__(self) -> str:
        return f"ToolRegistry(tools={list(self.tools.keys())})"