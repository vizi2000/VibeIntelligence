"""
MCP Integration for Zenith Coder
Connects to shared MCP Toolbox and Vector Knowledge Base
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio
from pathlib import Path
import sys

# Add MCP client to path
sys.path.append("/Users/wojciechwiesner/ai/mcp_toolbox/clients")

from mcp_client import MCPClient
from ..models.project import Project
from ..core.config import settings

logger = logging.getLogger(__name__)


class ZenithMCPIntegration:
    """
    MCP integration for Zenith Coder
    Provides knowledge management and tool access
    """
    
    def __init__(self):
        self.client: Optional[MCPClient] = None
        self.project_name = "zenith_coder"
        self._initialized = False
        
    async def initialize(self):
        """Initialize MCP connection"""
        try:
            self.client = MCPClient(
                project_name=self.project_name,
                toolbox_url="http://localhost:8210",
                vector_db_url="http://localhost:8200"
            )
            
            await self.client.connect()
            
            # Update project context
            await self.client.update_project_context(
                description="AI-powered project organization system with vibecoding principles",
                vibe_score=90,
                eco_score=85
            )
            
            self._initialized = True
            logger.info("✅ MCP integration initialized for Zenith Coder!")
            
        except Exception as e:
            logger.error(f"❌ MCP initialization failed: {e}")
            logger.warning("⚠️ Running without MCP integration")
            self._initialized = False
    
    async def add_project_to_knowledge_base(self, project: Project) -> bool:
        """Add project information to shared knowledge base"""
        if not self._initialized:
            return False
        
        try:
            # Create project summary
            summary = f"""
Project: {project.name}
Path: {project.path}
Type: {project.project_type}
Technologies: {', '.join(project.technologies or [])}
Has Tests: {project.has_tests}
Has Documentation: {project.has_documentation}
Vibe Score: {project.vibe_score}
Eco Score: {project.eco_score}

Description: Well-organized project following best practices.
Status: {'Active' if project.is_active else 'Archived'}
            """
            
            # Add to knowledge base
            result = await self.client.add_knowledge(
                content=summary,
                doc_id=f"project_{project.id}",
                doc_type="project",
                metadata={
                    "project_id": project.id,
                    "project_name": project.name,
                    "vibe_score": project.vibe_score,
                    "eco_score": project.eco_score,
                    "has_tests": project.has_tests,
                    "has_docs": project.has_documentation
                }
            )
            
            logger.info(f"📝 Added project {project.name} to knowledge base")
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Failed to add project to KB: {e}")
            return False
    
    async def search_similar_projects(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar projects in knowledge base"""
        if not self._initialized:
            return []
        
        try:
            # Search across all projects
            results = await self.client.search_knowledge(
                query=query,
                n_results=n_results,
                filter_project=False  # Search all projects
            )
            
            # Filter for project documents
            project_results = [
                r for r in results
                if r.get("metadata", {}).get("doc_type") == "project"
            ]
            
            return project_results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def analyze_project_with_mcp(self, project: Project) -> Dict[str, Any]:
        """Analyze project using MCP tools"""
        if not self._initialized:
            return {"error": "MCP not initialized"}
        
        try:
            results = {}
            
            # Get project insights
            insights = await self.client.get_project_insights()
            results["insights"] = insights.get("result", {}).get("insights", [])
            
            # Check if project has code to analyze
            if project.path and Path(project.path).exists():
                # Sample some code files for analysis
                code_files = list(Path(project.path).glob("**/*.py"))[:3]
                
                for code_file in code_files:
                    try:
                        with open(code_file, 'r', encoding='utf-8') as f:
                            code = f.read()[:1000]  # First 1000 chars
                        
                        # Eco analysis
                        eco_result = await self.client.analyze_code_eco_impact(code)
                        if "eco_results" not in results:
                            results["eco_results"] = []
                        results["eco_results"].append({
                            "file": str(code_file.name),
                            "eco_score": eco_result.get("result", {}).get("eco_score", 0)
                        })
                        
                        # DEI check
                        dei_result = await self.client.check_dei_compliance(code)
                        if dei_result.get("result", {}).get("issues"):
                            if "dei_issues" not in results:
                                results["dei_issues"] = []
                            results["dei_issues"].extend(dei_result["result"]["issues"])
                            
                    except Exception as e:
                        logger.error(f"Error analyzing file {code_file}: {e}")
            
            # Generate creative suggestion
            quantum_idea = await self.client.generate_quantum_idea(f"{project.project_type} project")
            results["quantum_suggestion"] = quantum_idea
            
            # Calculate overall scores
            avg_eco = sum(r["eco_score"] for r in results.get("eco_results", [])) / max(1, len(results.get("eco_results", [])))
            results["overall_eco_score"] = int(avg_eco) if results.get("eco_results") else project.eco_score
            
            results["dei_compliant"] = len(results.get("dei_issues", [])) == 0
            
            return results
            
        except Exception as e:
            logger.error(f"MCP analysis error: {e}")
            return {"error": str(e)}
    
    async def add_code_snippet(self, project_id: int, code: str, description: str, tags: List[str] = []):
        """Add code snippet to knowledge base for future reference"""
        if not self._initialized:
            return False
        
        try:
            content = f"Description: {description}\n\nCode:\n```\n{code}\n```"
            
            result = await self.client.add_knowledge(
                content=content,
                doc_id=f"code_snippet_{project_id}_{asyncio.get_event_loop().time()}",
                doc_type="code",
                metadata={
                    "project_id": project_id,
                    "tags": tags,
                    "language": "python"  # Auto-detect in future
                }
            )
            
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Failed to add code snippet: {e}")
            return False
    
    async def find_code_patterns(self, pattern: str) -> List[Dict[str, Any]]:
        """Find similar code patterns across all projects"""
        if not self._initialized:
            return []
        
        try:
            return await self.client.find_similar_code(pattern, n_results=10)
        except Exception as e:
            logger.error(f"Pattern search error: {e}")
            return []
    
    async def boost_developer_vibe(self, team_size: int = 1) -> Dict[str, Any]:
        """Boost developer morale with MCP vibe booster"""
        if not self._initialized:
            return {"message": "Keep coding with joy! 🌟"}
        
        try:
            result = await self.client.boost_team_vibe(
                team_size=team_size,
                current_vibe=75
            )
            return result.get("result", {"message": "You're doing great!"})
            
        except Exception as e:
            logger.error(f"Vibe boost error: {e}")
            return {"message": "Stay positive! 💪"}
    
    async def format_for_accessibility(self, text: str) -> str:
        """Format text for better accessibility"""
        if not self._initialized:
            return text
        
        try:
            return await self.client.format_for_adhd(text)
        except Exception:
            return text
    
    async def cleanup(self):
        """Cleanup MCP connection"""
        if self.client:
            await self.client.disconnect()
            self._initialized = False
            logger.info("🧹 MCP integration cleaned up")


# Global MCP integration instance
mcp_integration = ZenithMCPIntegration()


# Convenience functions for easy access
async def add_to_knowledge_base(content: str, doc_type: str = "general", metadata: Dict = None):
    """Quick function to add content to knowledge base"""
    if mcp_integration._initialized:
        return await mcp_integration.client.add_knowledge(
            content=content,
            doc_type=doc_type,
            metadata=metadata
        )
    return None


async def search_knowledge(query: str, n_results: int = 10):
    """Quick function to search knowledge base"""
    if mcp_integration._initialized:
        return await mcp_integration.client.search_knowledge(query, n_results)
    return []


async def get_quantum_idea(context: str = "coding"):
    """Quick function to get creative idea"""
    if mcp_integration._initialized:
        return await mcp_integration.client.generate_quantum_idea(context)
    return "Keep creating amazing things! 🌟"