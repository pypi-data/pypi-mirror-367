"""
Main Pareng Boyong AI Agent Class

This module implements the core ParengBoyong agent with Filipino cultural
integration, cost optimization, and multimodal capabilities.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, AsyncIterator
from datetime import datetime
import json

from .config import ParengBoyongConfig
from .exceptions import ParengBoyongError, ConfigurationError
from .tools import ToolRegistry
from ..cultural.identity import FilipinoIdentity
from ..cultural.language import LanguageProcessor
from ..helpers.cost_optimizer import CostOptimizer
from ..helpers.system_monitor import SystemMonitor

logger = logging.getLogger(__name__)


class ParengBoyong:
    """
    Main Pareng Boyong AI Agent class.
    
    Your intelligent Filipino coding assistant with cost optimization,
    cultural awareness, and multimodal capabilities.
    
    Features:
    - 44+ specialized AI tools with automatic cost optimization
    - Filipino cultural integration and context awareness
    - Multimodal generation (text, images, video, audio)
    - Multi-agent architecture with subordinate agents
    - Self-healing and system monitoring
    - Web interface and CLI integration
    
    Example:
        >>> config = ParengBoyongConfig(api_keys={"openai": "sk-xxx"})
        >>> agent = ParengBoyong(config)
        >>> response = agent.chat("Kumusta! Create a Manila sunset image")
        >>> print(response.content)
    """
    
    def __init__(self, config: Optional[ParengBoyongConfig] = None):
        """
        Initialize Pareng Boyong agent.
        
        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or ParengBoyongConfig()
        self.session_id = f"pb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Core components
        self.tool_registry = ToolRegistry(self.config)
        self.filipino_identity = FilipinoIdentity(self.config.cultural_mode)
        self.language_processor = LanguageProcessor()
        self.cost_optimizer = CostOptimizer(self.config)
        self.system_monitor = SystemMonitor()
        
        # Session state
        self.conversation_history: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        self.subordinate_agents: List['ParengBoyong'] = []
        
        # Initialize system
        self._initialize()
        
        logger.info(f"Pareng Boyong initialized - Session: {self.session_id}")
    
    def _initialize(self):
        """Initialize agent systems and perform health checks."""
        try:
            # System health check
            health = self.system_monitor.health_check()
            if not health.get('healthy', True):
                logger.warning(f"System health issues detected: {health}")
            
            # Load tools with cost optimization
            self.tool_registry.load_tools()
            
            # Cultural context initialization
            if self.config.cultural_mode:
                self.filipino_identity.initialize()
                
            # Set up cost tracking
            self.cost_optimizer.initialize_session(self.session_id)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Pareng Boyong: {e}")
    
    def chat(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Union[str, AsyncIterator[str]]:
        """
        Main chat interface for interacting with Pareng Boyong.
        
        Args:
            message: User message/query
            context: Additional context for the conversation
            stream: Whether to stream the response
            
        Returns:
            Response string or async iterator if streaming
            
        Example:
            >>> response = agent.chat("Create a video of Filipino sunset")
            >>> print(response)
        """
        try:
            # Cultural greeting detection
            if self.filipino_identity.is_greeting(message):
                greeting_response = self.filipino_identity.generate_greeting()
                if not stream:
                    return greeting_response
            
            # Process message with Filipino context
            processed_message = self.language_processor.process_message(
                message, 
                cultural_context=self.config.cultural_mode
            )
            
            # Update conversation context
            self._update_context(processed_message, context)
            
            # Route to appropriate tools with cost optimization
            if stream:
                return self._process_message_stream(processed_message)
            else:
                return self._process_message(processed_message)
                
        except Exception as e:
            logger.error(f"Chat processing error: {e}")
            return self._error_response(str(e))
    
    def _process_message(self, message: Dict[str, Any]) -> str:
        """Process message through the AI pipeline."""
        try:
            # Analyze request type and optimize tool selection
            analysis = self.cost_optimizer.analyze_request(message['content'])
            
            # Select optimal tools based on cost and capability
            selected_tools = self.tool_registry.select_tools(
                analysis['intent'],
                cost_budget=analysis.get('cost_budget', 0.01)
            )
            
            # Execute tools in order of cost optimization
            results = []
            total_cost = 0.0
            
            for tool_name in selected_tools:
                tool = self.tool_registry.get_tool(tool_name)
                
                # Cost check before execution
                estimated_cost = tool.estimate_cost(message)
                if total_cost + estimated_cost > self.config.max_daily_cost:
                    results.append({
                        'tool': tool_name,
                        'error': 'Daily cost limit reached',
                        'suggestion': 'Try FREE alternatives or increase budget'
                    })
                    break
                
                # Execute tool
                result = tool.execute(message, self.context)
                results.append({
                    'tool': tool_name,
                    'result': result,
                    'cost': result.get('cost', 0.0)
                })
                total_cost += result.get('cost', 0.0)
                
                # Break early if result is sufficient
                if result.get('success') and not analysis.get('requires_multiple_tools'):
                    break
            
            # Track costs
            self.cost_optimizer.track_usage(self.session_id, total_cost)
            
            # Generate Filipino-contextual response
            response = self._generate_response(results, message)
            
            # Update conversation history
            self._update_history(message, response, total_cost)
            
            return response
            
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            return self._error_response(str(e))
    
    async def _process_message_stream(self, message: Dict[str, Any]) -> AsyncIterator[str]:
        """Process message with streaming response."""
        # Implement streaming version
        yield f"🇵🇭 Pareng Boyong is thinking about: {message['content'][:50]}...\n"
        
        # Process normally and yield chunks
        response = self._process_message(message)
        
        # Yield response in chunks for streaming effect
        words = response.split()
        for i in range(0, len(words), 5):
            chunk = ' '.join(words[i:i+5]) + ' '
            yield chunk
            await asyncio.sleep(0.1)  # Small delay for streaming effect
    
    def _generate_response(self, results: List[Dict], original_message: Dict) -> str:
        """Generate Filipino-contextual response from tool results."""
        if not results:
            return self.filipino_identity.generate_error_response()
        
        # Check for errors
        errors = [r for r in results if 'error' in r]
        if errors:
            return self.filipino_identity.generate_error_response(errors)
        
        # Generate success response with cultural context
        successful_results = [r for r in results if r.get('result', {}).get('success')]
        
        if not successful_results:
            return "Hindi ko po na-accomplish ang request ninyo. Subukan natin ulit?"
        
        # Cultural response generation
        response_parts = []
        
        # Add Filipino greeting/acknowledgment
        response_parts.append(self.filipino_identity.generate_acknowledgment())
        
        # Add results summary
        for result in successful_results:
            tool_name = result['tool']
            tool_result = result['result']
            
            if tool_name.startswith('cost_optimized'):
                response_parts.append(
                    f"✅ Gumawa po ako ng {tool_result.get('type', 'content')} "
                    f"gamit ang FREE na serbisyo (Cost: ${result.get('cost', 0):.3f})"
                )
            else:
                response_parts.append(
                    f"✅ Success sa {tool_name}: {tool_result.get('summary', 'Completed')}"
                )
        
        # Add cost summary with Filipino context
        total_cost = sum(r.get('cost', 0) for r in results)
        if total_cost > 0:
            response_parts.append(
                f"💰 Total cost: ${total_cost:.3f} - "
                f"{'Sobrang mura!' if total_cost < 0.01 else 'Sulit pa rin!'}"
            )
        
        # Add cultural closing
        response_parts.append(self.filipino_identity.generate_closing())
        
        return "\n\n".join(response_parts)
    
    def _update_context(self, message: Dict[str, Any], additional_context: Optional[Dict] = None):
        """Update conversation context."""
        self.context.update({
            'last_message': message,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
        })
        
        if additional_context:
            self.context.update(additional_context)
    
    def _update_history(self, message: Dict, response: str, cost: float):
        """Update conversation history."""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'response': response,
            'cost': cost,
            'session_id': self.session_id
        })
        
        # Keep history size manageable
        if len(self.conversation_history) > self.config.max_history_size:
            self.conversation_history = self.conversation_history[-self.config.max_history_size:]
    
    def _error_response(self, error: str) -> str:
        """Generate Filipino-contextual error response."""
        return self.filipino_identity.generate_error_response([{'error': error}])
    
    def create_subordinate(self, task: str, context: Optional[Dict] = None) -> 'ParengBoyong':
        """
        Create a subordinate agent for handling subtasks.
        
        Args:
            task: Specific task for the subordinate
            context: Additional context for the subordinate
            
        Returns:
            New ParengBoyong instance configured as subordinate
        """
        subordinate_config = self.config.copy()
        subordinate_config.subordinate_mode = True
        subordinate_config.parent_session = self.session_id
        
        subordinate = ParengBoyong(subordinate_config)
        subordinate.context.update(context or {})
        subordinate.context['task'] = task
        subordinate.context['parent'] = self.session_id
        
        self.subordinate_agents.append(subordinate)
        
        logger.info(f"Created subordinate agent for task: {task}")
        return subordinate
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities summary."""
        return {
            'tools': self.tool_registry.list_tools(),
            'cultural_features': self.filipino_identity.get_features(),
            'cost_optimization': self.cost_optimizer.get_settings(),
            'system_health': self.system_monitor.health_check(),
            'session_info': {
                'session_id': self.session_id,
                'conversation_count': len(self.conversation_history),
                'subordinates': len(self.subordinate_agents)
            }
        }
    
    def reset_session(self):
        """Reset the current session."""
        self.session_id = f"pb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history.clear()
        self.context.clear()
        self.subordinate_agents.clear()
        self.cost_optimizer.initialize_session(self.session_id)
        
        logger.info(f"Session reset - New session: {self.session_id}")
    
    def __str__(self) -> str:
        return f"ParengBoyong(session={self.session_id}, tools={len(self.tool_registry.tools)})"
    
    def __repr__(self) -> str:
        return (
            f"ParengBoyong(session_id='{self.session_id}', "
            f"cultural_mode={self.config.cultural_mode}, "
            f"tools={len(self.tool_registry.tools)})"
        )