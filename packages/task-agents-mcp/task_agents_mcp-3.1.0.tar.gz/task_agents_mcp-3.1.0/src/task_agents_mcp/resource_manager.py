"""
Resource Manager for Task-Agents MCP Server

Manages dynamic MCP resources that provide contextual information about agents
to client LLMs, automatically updating when agents are added or modified.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


class AgentResourceManager:
    """Manages dynamic MCP resources for agents."""
    
    def __init__(self, mcp_server: FastMCP, agent_manager):
        """
        Initialize the resource manager.
        
        Args:
            mcp_server: The FastMCP server instance
            agent_manager: The AgentManager instance for accessing agent configs
        """
        self.mcp = mcp_server
        self.agent_manager = agent_manager
        self.registered_resources = {}
        
        # Track BMad workflow positions if applicable
        self.bmad_workflow = [
            "analyst", "pm", "ux_expert", "architect", 
            "po", "sm", "dev", "qa"
        ]
        
    def register_all_resources(self):
        """Register all available resources for agents."""
        logger.info("Registering MCP resources for agents...")
        
        # Register static resources
        self._register_static_resources()
        
        # Register dynamic resources
        self._register_dynamic_resources()
        
        logger.info(f"Registered {len(self.registered_resources)} resources")
        
    def _register_static_resources(self):
        """Register static resources that don't depend on specific agents."""
        
        # Register agents://list resource
        @self.mcp.resource("agents://list")
        async def list_agents() -> Dict[str, Any]:
            """List all available agents with basic information."""
            agents_info = []
            
            for name, agent in self.agent_manager.agents.items():
                agent_info = {
                    "name": name,
                    "display_name": agent.agent_name,
                    "description": agent.description,
                    "model": agent.model,
                    "uri": f"agents://{name}"
                }
                
                # Add workflow position if it's a BMad agent
                if name in self.bmad_workflow:
                    agent_info["workflow_position"] = self.bmad_workflow.index(name) + 1
                    agent_info["workflow_total"] = len(self.bmad_workflow)
                
                agents_info.append(agent_info)
            
            return {
                "total_agents": len(agents_info),
                "agents": agents_info,
                "workflow": {
                    "type": "BMad",
                    "stages": self.bmad_workflow
                } if any(name in self.bmad_workflow for name in self.agent_manager.agents.keys()) else None
            }
        
        self.registered_resources["agents://list"] = "Static list of all agents"
        logger.info("Registered resource: agents://list")
        
        # Register agents://schema resource for documentation
        @self.mcp.resource("agents://schema")
        async def get_resource_schema() -> Dict[str, Any]:
            """Get the schema documentation for agent resources."""
            return {
                "description": "Agent resources provide contextual information about available AI agents",
                "resources": {
                    "agents://list": {
                        "description": "List all available agents",
                        "returns": "Array of agent summaries with URIs"
                    },
                    "agents://{agent_name}": {
                        "description": "Get detailed information about a specific agent",
                        "parameters": {
                            "agent_name": "The internal name of the agent (e.g., 'analyst', 'dev')"
                        },
                        "returns": "Complete agent configuration and metadata"
                    },
                    "agents://{agent_name}/config": {
                        "description": "Get the configuration for a specific agent",
                        "returns": "Agent configuration including tools, model, and settings"
                    },
                    "agents://{agent_name}/examples": {
                        "description": "Get usage examples for a specific agent",
                        "returns": "Example prompts and use cases"
                    }
                },
                "agent_fields": {
                    "name": "Internal identifier",
                    "display_name": "Human-readable name",
                    "description": "What the agent does",
                    "model": "LLM model used (opus/sonnet)",
                    "tools": "Available tools for the agent",
                    "session_support": "Session resumption configuration",
                    "resource_dirs": "Additional directories the agent can access",
                    "workflow_position": "Position in BMad workflow (if applicable)"
                }
            }
        
        self.registered_resources["agents://schema"] = "Resource schema documentation"
        logger.info("Registered resource: agents://schema")
        
    def _register_dynamic_resources(self):
        """Register dynamic resources with parameters."""
        
        # Register agents://{agent_name} resource
        @self.mcp.resource("agents://{agent_name}")
        async def get_agent_details(agent_name: str) -> Dict[str, Any]:
            """Get detailed information about a specific agent."""
            agent = self.agent_manager.agents.get(agent_name)
            
            if not agent:
                return {
                    "error": f"Agent '{agent_name}' not found",
                    "available_agents": list(self.agent_manager.agents.keys())
                }
            
            # Build comprehensive agent information
            agent_details = {
                "name": agent.name,
                "display_name": agent.agent_name,
                "description": agent.description,
                "model": agent.model,
                "tools": agent.tools,
                "working_directory": agent.cwd,
                "session_support": {
                    "enabled": bool(agent.resume_session),
                    "max_exchanges": (
                        agent.resume_session if isinstance(agent.resume_session, int) 
                        else 5 if agent.resume_session else 0
                    )
                }
            }
            
            # Add resource directories if present
            if agent.resource_dirs:
                agent_details["resource_directories"] = agent.resource_dirs
            
            # Add workflow information for BMad agents
            if agent.name in self.bmad_workflow:
                position = self.bmad_workflow.index(agent.name)
                agent_details["workflow"] = {
                    "type": "BMad",
                    "position": position + 1,
                    "total_stages": len(self.bmad_workflow),
                    "previous": self.bmad_workflow[position - 1] if position > 0 else None,
                    "next": self.bmad_workflow[position + 1] if position < len(self.bmad_workflow) - 1 else None
                }
            
            # Add recommended use cases based on agent type
            agent_details["recommended_for"] = self._get_agent_recommendations(agent.name)
            
            return agent_details
        
        self.registered_resources["agents://{agent_name}"] = "Dynamic agent details"
        logger.info("Registered resource: agents://{agent_name}")
        
        # Register agents://{agent_name}/config resource
        @self.mcp.resource("agents://{agent_name}/config")
        async def get_agent_config(agent_name: str) -> Dict[str, Any]:
            """Get the configuration for a specific agent."""
            agent = self.agent_manager.agents.get(agent_name)
            
            if not agent:
                return {
                    "error": f"Agent '{agent_name}' not found",
                    "available_agents": list(self.agent_manager.agents.keys())
                }
            
            return {
                "agent_name": agent.agent_name,
                "description": agent.description,
                "tools": agent.tools,
                "model": agent.model,
                "working_directory": agent.cwd,
                "resume_session": agent.resume_session,
                "resource_dirs": agent.resource_dirs or []
            }
        
        self.registered_resources["agents://{agent_name}/config"] = "Dynamic agent configuration"
        logger.info("Registered resource: agents://{agent_name}/config")
        
        # Register agents://{agent_name}/examples resource
        @self.mcp.resource("agents://{agent_name}/examples")
        async def get_agent_examples(agent_name: str) -> Dict[str, Any]:
            """Get usage examples for a specific agent."""
            agent = self.agent_manager.agents.get(agent_name)
            
            if not agent:
                return {
                    "error": f"Agent '{agent_name}' not found",
                    "available_agents": list(self.agent_manager.agents.keys())
                }
            
            # Generate examples based on agent type
            examples = self._generate_agent_examples(agent.name, agent.agent_name)
            
            return {
                "agent": agent.agent_name,
                "examples": examples,
                "tips": self._get_agent_tips(agent.name)
            }
        
        self.registered_resources["agents://{agent_name}/examples"] = "Dynamic agent usage examples"
        logger.info("Registered resource: agents://{agent_name}/examples")
        
    def _get_agent_recommendations(self, agent_name: str) -> List[str]:
        """Get recommended use cases for an agent."""
        recommendations = {
            "analyst": [
                "Market research and competitive analysis",
                "Project discovery and requirements gathering",
                "Brainstorming and ideation sessions",
                "Creating project briefs and documentation",
                "Analyzing existing systems (brownfield projects)"
            ],
            "pm": [
                "Creating product requirements documents (PRDs)",
                "Defining success metrics and KPIs",
                "Stakeholder communication planning",
                "Product roadmap development",
                "Feature prioritization"
            ],
            "ux_expert": [
                "User interface design and wireframing",
                "User experience flow optimization",
                "Design system creation",
                "Accessibility planning",
                "User journey mapping"
            ],
            "architect": [
                "System architecture design",
                "Technology stack selection",
                "Integration planning",
                "Performance optimization strategies",
                "Security architecture"
            ],
            "po": [
                "User story creation and refinement",
                "Acceptance criteria definition",
                "Backlog prioritization",
                "Sprint planning preparation",
                "Stakeholder requirement validation"
            ],
            "sm": [
                "Sprint planning and organization",
                "Task breakdown and estimation",
                "Team coordination planning",
                "Agile ceremony facilitation",
                "Progress tracking setup"
            ],
            "dev": [
                "Code implementation",
                "API development",
                "Database schema design",
                "Integration development",
                "Bug fixing and refactoring"
            ],
            "qa": [
                "Code review and quality assurance",
                "Test case design and implementation",
                "Performance testing",
                "Security testing",
                "Documentation review"
            ],
            "default_assistant": [
                "General programming assistance",
                "Code explanation and debugging",
                "Quick prototypes and examples",
                "Documentation writing",
                "General Q&A"
            ]
        }
        
        return recommendations.get(agent_name, ["General task assistance"])
    
    def _generate_agent_examples(self, agent_name: str, display_name: str) -> List[Dict[str, str]]:
        """Generate usage examples for an agent."""
        examples_map = {
            "analyst": [
                {
                    "prompt": "Research the current state of AI code assistants market",
                    "description": "Performs competitive analysis and market research"
                },
                {
                    "prompt": "Analyze our existing authentication system and document improvement opportunities",
                    "description": "Analyzes brownfield projects and suggests enhancements"
                },
                {
                    "prompt": "Brainstorm features for a new task management application",
                    "description": "Facilitates ideation and feature discovery"
                }
            ],
            "pm": [
                {
                    "prompt": "Create a PRD for a user notification system",
                    "description": "Generates comprehensive product requirements"
                },
                {
                    "prompt": "Define success metrics for our new feature launch",
                    "description": "Establishes measurable KPIs and success criteria"
                }
            ],
            "dev": [
                {
                    "prompt": "Implement a REST API endpoint for user authentication",
                    "description": "Creates production-ready code implementation"
                },
                {
                    "prompt": "Refactor the payment processing module for better error handling",
                    "description": "Improves existing code quality and structure"
                }
            ],
            "qa": [
                {
                    "prompt": "Review the recent changes to the user service and suggest improvements",
                    "description": "Performs thorough code review and quality checks"
                },
                {
                    "prompt": "Create comprehensive test cases for the checkout flow",
                    "description": "Designs test strategies and implementations"
                }
            ]
        }
        
        # Return specific examples or generic ones
        return examples_map.get(agent_name, [
            {
                "prompt": f"Help me with [your specific task]",
                "description": f"Uses {display_name} to assist with your request"
            }
        ])
    
    def _get_agent_tips(self, agent_name: str) -> List[str]:
        """Get usage tips for an agent."""
        tips_map = {
            "analyst": [
                "Call this agent FIRST when starting new projects",
                "Provide context about your business domain for better analysis",
                "Use interactive checkpoints to guide the research direction"
            ],
            "pm": [
                "Provide the analyst's output for context when creating PRDs",
                "Be specific about target users and business goals",
                "Review and refine the success metrics before proceeding"
            ],
            "dev": [
                "Ensure architecture and design are complete before implementation",
                "Provide clear acceptance criteria from the PO",
                "The agent will follow existing code patterns in your project"
            ],
            "qa": [
                "Run this after development is complete",
                "The agent will check for code quality, security, and performance",
                "Provides actionable feedback for improvements"
            ]
        }
        
        return tips_map.get(agent_name, [
            "Be specific about your requirements",
            "Provide relevant context for better results"
        ])