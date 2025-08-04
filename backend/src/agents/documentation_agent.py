"""
Documentation Agent - AI-powered documentation generation
Following Directive 8: Multi-provider AI orchestration
Implements Directive 18: DEI-friendly documentation
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json

from ..ai.orchestrator import orchestrator, TaskType
from ..core.exceptions import DocumentationException

logger = logging.getLogger(__name__)


class DocumentationAgent:
    """
    AI agent for generating and maintaining documentation
    Following vibecoding principles with joy and inclusivity
    """
    
    def __init__(self):
        self.templates = self._load_templates()
        self.dei_guidelines = self._load_dei_guidelines()
        
    def _load_templates(self) -> Dict[str, str]:
        """Load documentation templates with ADHD-friendly structure"""
        return {
            "readme": """# {project_name}

{emoji} **{tagline}**

## 🎯 What is this?
{description}

## 🚀 Quick Start (ADHD-Friendly!)
{quick_start}

## ✨ Features
{features}

## 🛠️ Installation
{installation}

## 📖 Usage
{usage}

## 🌈 Contributing
{contributing}

## 💚 Sustainability
- Eco-Score: {eco_score}%
- Optimized for minimal resource usage

## 📝 License
{license}

---
*Generated with love by Zenith Coder's Documentation Agent* 🤖✨
""",
            "contributing": """# Contributing to {project_name}

We love your input! 💖 We want to make contributing as easy and transparent as possible.

## 🎯 Quick Contribution Guide

### For ADHD Warriors:
1. **Small PRs are perfect!** Don't feel you need to solve everything
2. **Break tasks down** - One feature/fix per PR
3. **Ask questions** - We're here to help!

## 🚀 Getting Started
{getting_started}

## 🐛 Reporting Bugs
{bug_reporting}

## 💡 Suggesting Features
{feature_suggestions}

## 📋 Code Style
{code_style}

## 🌍 Our Values
- **Inclusivity**: All backgrounds welcome
- **Accessibility**: Code should work for everyone
- **Sustainability**: Consider eco-impact
- **Joy**: Coding should be fun!

## 🤝 Code of Conduct
Be kind, be inclusive, spread joy! Full details in CODE_OF_CONDUCT.md

---
*Happy coding!* 🌈
""",
            "adr": """# ADR-{number}: {title}

## 📅 Date
{date}

## 🎯 Status
{status}

## 🤔 Context
{context}

## 💡 Decision
{decision}

## 🌟 Consequences
### Positive
{positive_consequences}

### Negative
{negative_consequences}

## 🔄 Alternatives Considered
{alternatives}

## 📚 References
{references}
"""
        }
        
    def _load_dei_guidelines(self) -> Dict[str, List[str]]:
        """
        Load DEI guidelines for inclusive documentation
        Following Directive 18: Global DEI considerations
        """
        return {
            "inclusive_language": [
                "Use 'they' as default pronoun",
                "Avoid ableist language (crazy, insane, blind to)",
                "Use simple, clear language",
                "Provide multiple examples",
                "Consider global audience"
            ],
            "accessibility": [
                "Use proper heading hierarchy",
                "Include alt text for images",
                "Keep paragraphs short",
                "Use bullet points for clarity",
                "Provide code examples"
            ],
            "cultural_awareness": [
                "Avoid idioms and colloquialisms",
                "Use international date formats",
                "Consider timezone differences",
                "Respect diverse workflows"
            ]
        }
        
    async def generate_readme(self, project_info: Dict[str, Any]) -> str:
        """
        Generate README with AI assistance
        Following Directive 5: ADHD-friendly documentation
        """
        try:
            # Build context-aware prompt
            prompt = self._build_readme_prompt(project_info)
            
            # Generate with AI
            response = await orchestrator.generate(
                prompt=prompt,
                task_type=TaskType.DOCUMENTATION,
                temperature=0.7,
                max_tokens=1500
            )
            
            # Extract sections from AI response
            readme_content = self._parse_ai_response(response["content"], project_info)
            
            # Apply DEI guidelines
            readme_content = self._apply_dei_guidelines(readme_content)
            
            # Fill template
            readme = self.templates["readme"].format(**readme_content)
            
            logger.info(f"✅ Generated README for {project_info['name']} with vibe!")
            return readme
            
        except Exception as e:
            logger.error(f"Failed to generate README: {e}")
            raise DocumentationException(f"README generation failed: {str(e)}")
            
    def _build_readme_prompt(self, project_info: Dict[str, Any]) -> str:
        """Build context-aware prompt for README generation"""
        return f"""
        Generate a comprehensive, ADHD-friendly README for this project:
        
        Project: {project_info['name']}
        Type: {project_info['type']}
        Languages: {', '.join(project_info['languages'])}
        Has Tests: {project_info['has_tests']}
        Health Score: {project_info['health_score']}
        
        Guidelines:
        1. Use emojis for visual breaks
        2. Keep sections short and scannable
        3. Include a "Quick Start" section with numbered steps
        4. Be inclusive and welcoming
        5. Add humor where appropriate
        6. Consider developers with ADHD
        
        Generate these sections:
        - emoji: A fitting emoji for the project
        - tagline: One-line description (catchy!)
        - description: 2-3 sentences about what it does
        - quick_start: 3-5 numbered steps to get started
        - features: Bullet list of key features
        - installation: Step-by-step installation
        - usage: Basic usage examples
        - contributing: How to contribute
        - license: Suggested license
        
        Make it vibrant, inclusive, and joyful!
        """
        
    async def generate_contributing_guide(self, project_info: Dict[str, Any]) -> str:
        """Generate CONTRIBUTING.md with inclusivity focus"""
        try:
            prompt = f"""
            Create a welcoming CONTRIBUTING.md for {project_info['name']}.
            
            Focus on:
            1. ADHD-friendly contribution process
            2. Inclusive language for all backgrounds
            3. Clear, numbered steps
            4. Encouragement for small contributions
            5. Multiple ways to contribute (not just code)
            
            Include sections for:
            - getting_started: Setup steps
            - bug_reporting: How to report bugs
            - feature_suggestions: How to suggest features
            - code_style: Basic style guidelines
            """
            
            response = await orchestrator.generate(
                prompt=prompt,
                task_type=TaskType.DOCUMENTATION,
                temperature=0.8,
                max_tokens=800
            )
            
            content = self._parse_contributing_response(response["content"], project_info)
            guide = self.templates["contributing"].format(**content)
            
            return guide
            
        except Exception as e:
            logger.error(f"Failed to generate CONTRIBUTING.md: {e}")
            raise DocumentationException(f"Contributing guide generation failed: {str(e)}")
            
    async def generate_adr(self, decision_context: Dict[str, Any]) -> str:
        """
        Generate Architecture Decision Record
        Following Directive 6: Clear documentation
        """
        try:
            prompt = f"""
            Create an Architecture Decision Record for:
            Title: {decision_context['title']}
            Context: {decision_context['context']}
            
            Consider:
            1. Technical trade-offs
            2. Sustainability impact
            3. Accessibility implications
            4. Team cognitive load
            
            Format as:
            - status: Current status
            - context: Expanded context
            - decision: What was decided and why
            - positive_consequences: Benefits
            - negative_consequences: Drawbacks
            - alternatives: Other options considered
            """
            
            response = await orchestrator.generate(
                prompt=prompt,
                task_type=TaskType.DOCUMENTATION,
                temperature=0.6,
                max_tokens=600
            )
            
            adr_content = self._parse_adr_response(response["content"], decision_context)
            adr = self.templates["adr"].format(**adr_content)
            
            return adr
            
        except Exception as e:
            logger.error(f"Failed to generate ADR: {e}")
            raise DocumentationException(f"ADR generation failed: {str(e)}")
            
    async def analyze_documentation_quality(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze existing documentation quality
        Returns score and improvement suggestions
        """
        analysis = {
            "score": 0,
            "has_readme": False,
            "has_contributing": False,
            "has_license": False,
            "has_code_of_conduct": False,
            "suggestions": [],
            "dei_score": 0,
            "accessibility_score": 0
        }
        
        # Check for essential files
        readme_path = project_path / "README.md"
        if readme_path.exists():
            analysis["has_readme"] = True
            analysis["score"] += 25
            
            # Analyze README quality
            readme_analysis = await self._analyze_readme_quality(readme_path)
            analysis.update(readme_analysis)
        else:
            analysis["suggestions"].append("Add README.md for better discoverability")
            
        # Check other docs
        if (project_path / "CONTRIBUTING.md").exists():
            analysis["has_contributing"] = True
            analysis["score"] += 15
        else:
            analysis["suggestions"].append("Add CONTRIBUTING.md to welcome contributors")
            
        if (project_path / "LICENSE").exists() or (project_path / "LICENSE.md").exists():
            analysis["has_license"] = True
            analysis["score"] += 10
        else:
            analysis["suggestions"].append("Add LICENSE file for legal clarity")
            
        if (project_path / "CODE_OF_CONDUCT.md").exists():
            analysis["has_code_of_conduct"] = True
            analysis["score"] += 10
            analysis["dei_score"] += 20
        else:
            analysis["suggestions"].append("Add CODE_OF_CONDUCT.md for inclusive community")
            
        # Calculate final scores
        analysis["vibe_level"] = self._calculate_doc_vibe(analysis)
        
        return analysis
        
    async def _analyze_readme_quality(self, readme_path: Path) -> Dict[str, Any]:
        """Analyze README for quality and inclusivity"""
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        analysis = {
            "readme_quality": {
                "has_badges": "![" in content,
                "has_quick_start": any(x in content.lower() for x in ["quick start", "getting started"]),
                "has_examples": "```" in content,
                "has_emojis": any(ord(c) > 127 for c in content),
                "sections_count": content.count("#"),
                "word_count": len(content.split())
            }
        }
        
        # DEI analysis
        dei_score = 0
        if "contribut" in content.lower():
            dei_score += 20
        if "inclusive" in content.lower() or "welcom" in content.lower():
            dei_score += 20
        if "accessibility" in content.lower() or "a11y" in content.lower():
            dei_score += 20
            
        analysis["dei_score"] = dei_score
        
        # Accessibility scoring
        acc_score = 0
        if analysis["readme_quality"]["has_quick_start"]:
            acc_score += 30
        if analysis["readme_quality"]["sections_count"] > 3:
            acc_score += 20
        if analysis["readme_quality"]["word_count"] < 2000:  # Not too long
            acc_score += 20
            
        analysis["accessibility_score"] = acc_score
        
        return analysis
        
    def _calculate_doc_vibe(self, analysis: Dict[str, Any]) -> str:
        """Calculate documentation vibe level"""
        total_score = analysis["score"] + (analysis.get("dei_score", 0) / 2)
        
        if total_score >= 80:
            return "peak_documentation_flow"
        elif total_score >= 60:
            return "high_vibe"
        elif total_score >= 40:
            return "medium_vibe"
        else:
            return "needs_documentation_love"
            
    def _parse_ai_response(self, response: str, project_info: Dict[str, Any]) -> Dict[str, str]:
        """Parse AI response into README sections"""
        # This would parse the structured response
        # For now, return defaults
        sections = {
            "project_name": project_info["name"],
            "emoji": "🚀",
            "tagline": "An awesome project built with love",
            "description": response.split("\n")[0] if response else "A vibecoding project",
            "quick_start": "1. Clone the repo\n2. Install dependencies\n3. Run the project",
            "features": "- Fast and efficient\n- Built with modern tech\n- Sustainable design",
            "installation": "```bash\ngit clone <repo>\ncd " + project_info["name"] + "\n```",
            "usage": "See documentation for usage examples",
            "contributing": "We welcome contributions! See CONTRIBUTING.md",
            "eco_score": project_info.get("health_score", 80),
            "license": "MIT"
        }
        
        return sections
        
    def _parse_contributing_response(self, response: str, project_info: Dict[str, Any]) -> Dict[str, str]:
        """Parse AI response for contributing guide"""
        return {
            "project_name": project_info["name"],
            "getting_started": response.split("\n")[0] if response else "1. Fork the repo\n2. Create your feature branch\n3. Make your changes",
            "bug_reporting": "Please use GitHub issues with clear descriptions",
            "feature_suggestions": "Open an issue with [FEATURE] tag",
            "code_style": "Follow existing code style in the project"
        }
        
    def _parse_adr_response(self, response: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Parse AI response for ADR"""
        return {
            "number": context.get("number", "001"),
            "title": context["title"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "Accepted",
            "context": context["context"],
            "decision": response.split("\n")[0] if response else "Decision details here",
            "positive_consequences": "- Improved clarity\n- Better maintainability",
            "negative_consequences": "- Additional complexity",
            "alternatives": "- Alternative approaches considered",
            "references": "- Team discussion notes"
        }
        
    def _apply_dei_guidelines(self, content: Dict[str, str]) -> Dict[str, str]:
        """Apply DEI guidelines to documentation content"""
        # This would apply various transformations
        # For now, return as-is
        return content


# Global agent instance
documentation_agent = DocumentationAgent()