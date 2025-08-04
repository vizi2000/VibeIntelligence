"""
Monetization Advisor Agent
Helps developers find monetization opportunities
Following vibecoding principles for sustainable income
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from ..models.agent_task import AgentTask, AgentType
from ..models.project import Project
from ..models.developer_profile import DeveloperProfile
from ..ai.orchestrator import TaskType

logger = logging.getLogger(__name__)


class MonetizationAgent(BaseAgent):
    """
    Agent that identifies and suggests monetization opportunities
    - Analyzes projects for commercial potential
    - Finds matching freelance opportunities
    - Suggests SaaS/product ideas
    - Tracks market trends
    """
    
    def __init__(self):
        super().__init__(AgentType.MONETIZATION, "Monetization Advisor")
        self.opportunity_sources = [
            "freelance_platforms",
            "job_boards",
            "startup_ideas",
            "open_source_sponsorship"
        ]
    
    async def execute_task(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Execute monetization task"""
        task_type = task.input_data.get("monetization_type", "opportunity_scan")
        
        if task_type == "opportunity_scan":
            return await self._scan_opportunities(task, db)
        elif task_type == "project_monetization":
            return await self._analyze_project_monetization(task, db)
        elif task_type == "skill_matching":
            return await self._match_skills_to_opportunities(task, db)
        elif task_type == "market_analysis":
            return await self._analyze_market_trends(task, db)
        elif task_type == "pricing_strategy":
            return await self._suggest_pricing(task, db)
        else:
            return await self._general_monetization_advice(task, db)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze monetization opportunities"""
        developer_skills = context.get("skills", [])
        current_projects = context.get("projects", [])
        
        analysis = {
            "opportunities_available": False,
            "opportunity_types": [],
            "potential_monthly_income": 0,
            "recommendations": []
        }
        
        # Check if developer has marketable skills
        marketable_skills = self._identify_marketable_skills(developer_skills)
        if marketable_skills:
            analysis["opportunities_available"] = True
            analysis["opportunity_types"].append("freelance")
            analysis["potential_monthly_income"] += len(marketable_skills) * 1000
        
        # Check project monetization potential
        for project in current_projects:
            if self._has_monetization_potential(project):
                analysis["opportunities_available"] = True
                analysis["opportunity_types"].append("saas")
                analysis["recommendations"].append(f"Consider turning {project} into a SaaS")
        
        return analysis
    
    async def _scan_opportunities(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Scan for monetization opportunities"""
        developer_id = task.developer_id
        developer = db.query(DeveloperProfile).filter(
            DeveloperProfile.id == developer_id
        ).first()
        
        if not developer:
            raise ValueError(f"Developer {developer_id} not found")
        
        logger.info(f"💰 Scanning monetization opportunities for {developer.username}")
        
        opportunities = {
            "freelance": [],
            "products": [],
            "sponsorship": [],
            "consulting": []
        }
        
        # Analyze developer skills for freelance matching
        if developer.primary_languages:
            prompt = f"""
            Based on these developer skills:
            Languages: {developer.primary_languages}
            Frameworks: {developer.frameworks}
            Specializations: {developer.specializations}
            
            Suggest:
            1. Top 5 freelance project types that match these skills
            2. Estimated hourly rates for each skill level
            3. Most in-demand combinations of these skills
            4. Niche markets where these skills are valuable
            5. Platforms best suited for these skills
            
            Format as actionable opportunities with estimated earnings.
            """
            
            ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
            freelance_opportunities = ai_response.get("content", "")
            
            # Parse AI response to extract opportunities
            opportunities["freelance"] = self._parse_freelance_opportunities(freelance_opportunities)
        
        # Analyze projects for product potential
        projects = db.query(Project).filter(
            Project.is_active == True
        ).all()
        
        for project in projects[:5]:  # Analyze top 5 projects
            if project.has_documentation and project.tech_stack:
                prompt = f"""
                Analyze this project for monetization potential:
                Name: {project.name}
                Tech Stack: {project.tech_stack}
                Type: {project.project_type}
                
                Suggest:
                1. Can this be turned into a SaaS? How?
                2. Potential target market
                3. MVP features for monetization
                4. Estimated development time to MVP
                5. Potential pricing model
                6. Competition analysis needed
                """
                
                ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
                
                if "yes" in ai_response.get("content", "").lower():
                    opportunities["products"].append({
                        "project_name": project.name,
                        "project_id": project.id,
                        "monetization_strategy": ai_response.get("content", ""),
                        "estimated_revenue": "$500-5000/month",
                        "time_to_market": "2-3 months"
                    })
        
        # Open source sponsorship opportunities
        if any(p.is_git_repo for p in projects):
            opportunities["sponsorship"].append({
                "type": "GitHub Sponsors",
                "requirements": "Active open source contributions",
                "potential": "$100-1000/month",
                "action": "Set up GitHub Sponsors profile"
            })
        
        # Consulting opportunities based on experience
        if developer.total_projects > 10:
            opportunities["consulting"].append({
                "type": "Technical Consulting",
                "rate": "$100-200/hour",
                "specialization": developer.specializations[0] if developer.specializations else "General",
                "platforms": ["Clarity.fm", "LinkedIn", "Direct outreach"]
            })
        
        # Calculate total potential
        total_potential = self._calculate_income_potential(opportunities)
        
        # Log activity
        await self.log_activity(
            developer_id,
            "Scanned monetization opportunities",
            None,
            {
                "freelance_count": len(opportunities["freelance"]),
                "product_count": len(opportunities["products"]),
                "total_potential": total_potential
            }
        )
        
        return {
            "opportunities": opportunities,
            "total_monthly_potential": total_potential,
            "immediate_actions": self._get_immediate_actions(opportunities),
            "long_term_strategy": self._get_long_term_strategy(developer, opportunities)
        }
    
    async def _analyze_project_monetization(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Analyze specific project for monetization"""
        project_id = task.input_data.get("project_id")
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        logger.info(f"💡 Analyzing monetization for {project.name}")
        
        # Comprehensive monetization analysis
        prompt = f"""
        Perform detailed monetization analysis for this project:
        
        Project: {project.name}
        Type: {project.project_type}
        Tech Stack: {project.tech_stack}
        Has Documentation: {project.has_documentation}
        Has Tests: {project.has_tests}
        
        Analyze:
        1. SaaS Potential:
           - Target audience
           - Core features for MVP
           - Pricing tiers ($X/month)
           - Competition landscape
        
        2. API Monetization:
           - Can it be offered as an API?
           - Usage-based pricing model
           - Target developers/companies
        
        3. Marketplace/Plugin:
           - Platform integration possibilities
           - One-time vs subscription pricing
        
        4. Educational Content:
           - Course/tutorial potential
           - Target learning audience
           - Platform recommendations
        
        5. Licensing:
           - Enterprise licensing opportunities
           - White-label potential
        
        Provide specific, actionable recommendations with revenue estimates.
        """
        
        ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
        monetization_analysis = ai_response.get("content", "")
        
        # Extract key metrics
        strategies = self._extract_monetization_strategies(monetization_analysis)
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "monetization_analysis": monetization_analysis,
            "recommended_strategies": strategies,
            "next_steps": self._get_project_next_steps(strategies),
            "estimated_time_to_revenue": "1-3 months",
            "required_investment": "$0-500"
        }
    
    async def _match_skills_to_opportunities(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Match developer skills to opportunities"""
        developer_id = task.developer_id
        developer = db.query(DeveloperProfile).filter(
            DeveloperProfile.id == developer_id
        ).first()
        
        if not developer:
            raise ValueError(f"Developer {developer_id} not found")
        
        # Get skill levels
        skills_data = {
            "languages": developer.primary_languages or [],
            "frameworks": developer.frameworks or [],
            "skill_levels": developer.skill_levels or {},
            "specializations": developer.specializations or []
        }
        
        # AI matching
        prompt = f"""
        Match these developer skills to high-paying opportunities:
        
        Skills: {skills_data}
        
        Find:
        1. Top 10 matching freelance gigs with rates
        2. Remote job opportunities with salary ranges
        3. Consulting niches that pay premium
        4. Side project ideas that can generate passive income
        5. Skills to learn next for higher rates
        
        Focus on opportunities that can start generating income within 30 days.
        Include specific platforms, companies, or markets to target.
        """
        
        ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
        matches = ai_response.get("content", "")
        
        # Parse and structure opportunities
        structured_matches = self._structure_skill_matches(matches, skills_data)
        
        return {
            "developer_id": developer_id,
            "skills_analyzed": skills_data,
            "matching_opportunities": structured_matches,
            "quick_wins": self._identify_quick_wins(structured_matches),
            "skill_gaps": self._identify_skill_gaps(matches),
            "action_plan": self._create_30_day_plan(structured_matches)
        }
    
    async def _analyze_market_trends(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Analyze current market trends"""
        focus_area = task.input_data.get("focus_area", "general")
        
        prompt = f"""
        Analyze current market trends for developers in {focus_area}:
        
        Research:
        1. Highest paying skills right now
        2. Emerging technologies with high demand
        3. Declining technologies to avoid
        4. Remote work opportunities growth
        5. Startup sectors hiring most
        6. Freelance vs full-time trends
        7. AI impact on developer jobs
        
        Provide specific data points, rates, and actionable insights.
        Focus on trends that developers can capitalize on within 3-6 months.
        """
        
        ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
        trends = ai_response.get("content", "")
        
        return {
            "focus_area": focus_area,
            "market_analysis": trends,
            "top_opportunities": self._extract_top_opportunities(trends),
            "skills_to_learn": self._extract_trending_skills(trends),
            "sectors_to_target": self._extract_hot_sectors(trends)
        }
    
    async def _suggest_pricing(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Suggest pricing strategies"""
        service_type = task.input_data.get("service_type", "freelance")
        skill_level = task.input_data.get("skill_level", "intermediate")
        location = task.input_data.get("location", "remote")
        
        prompt = f"""
        Suggest pricing strategy for:
        Service Type: {service_type}
        Skill Level: {skill_level}
        Location: {location}
        
        Provide:
        1. Hourly rates (minimum, standard, premium)
        2. Project-based pricing guidelines
        3. Retainer pricing models
        4. Value-based pricing examples
        5. How to increase rates over time
        6. Negotiation strategies
        
        Include specific numbers and real examples.
        """
        
        ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
        pricing_guide = ai_response.get("content", "")
        
        return {
            "service_type": service_type,
            "pricing_guide": pricing_guide,
            "recommended_rates": self._extract_rate_recommendations(pricing_guide),
            "pricing_calculator": self._create_pricing_calculator(skill_level, service_type)
        }
    
    async def _general_monetization_advice(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Provide general monetization advice"""
        developer_id = task.developer_id
        
        prompt = """
        Provide comprehensive monetization advice for a developer:
        
        Cover:
        1. Quick wins (can start this week)
        2. Medium-term strategies (1-3 months)
        3. Long-term wealth building (6-12 months)
        4. Passive income streams
        5. Common mistakes to avoid
        6. Success stories and examples
        
        Be specific and actionable.
        """
        
        ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
        
        return {
            "general_advice": ai_response.get("content", ""),
            "action_items": self._extract_action_items(ai_response.get("content", ""))
        }
    
    def _identify_marketable_skills(self, skills: List[str]) -> List[str]:
        """Identify skills with high market demand"""
        high_demand_skills = [
            "python", "javascript", "react", "nodejs", "aws", "docker",
            "kubernetes", "typescript", "golang", "rust", "machine learning",
            "data science", "blockchain", "mobile", "devops"
        ]
        
        marketable = []
        for skill in skills:
            if any(demand in skill.lower() for demand in high_demand_skills):
                marketable.append(skill)
        
        return marketable
    
    def _has_monetization_potential(self, project: Dict[str, Any]) -> bool:
        """Check if project has monetization potential"""
        indicators = [
            "api", "dashboard", "automation", "tool", "platform",
            "analytics", "management", "tracker", "optimizer"
        ]
        
        project_name = project.get("name", "").lower()
        return any(indicator in project_name for indicator in indicators)
    
    def _parse_freelance_opportunities(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI response for freelance opportunities"""
        opportunities = []
        
        # Simple parsing - in production, use more sophisticated parsing
        lines = ai_response.split('\n')
        current_opp = {}
        
        for line in lines:
            if "project" in line.lower() or "opportunity" in line.lower():
                if current_opp:
                    opportunities.append(current_opp)
                current_opp = {"description": line, "skills": [], "rate": "$50-100/hr"}
            elif "$" in line:
                # Extract rate
                rate_match = re.search(r'\$[\d,]+(?:-\$?[\d,]+)?(?:/\w+)?', line)
                if rate_match and current_opp:
                    current_opp["rate"] = rate_match.group()
        
        if current_opp:
            opportunities.append(current_opp)
        
        return opportunities[:5]  # Return top 5
    
    def _calculate_income_potential(self, opportunities: Dict[str, List]) -> int:
        """Calculate total income potential"""
        total = 0
        
        # Freelance potential
        total += len(opportunities.get("freelance", [])) * 2000
        
        # Product potential
        total += len(opportunities.get("products", [])) * 1000
        
        # Sponsorship
        total += len(opportunities.get("sponsorship", [])) * 500
        
        # Consulting
        total += len(opportunities.get("consulting", [])) * 3000
        
        return total
    
    def _get_immediate_actions(self, opportunities: Dict[str, List]) -> List[str]:
        """Get immediate actionable steps"""
        actions = []
        
        if opportunities.get("freelance"):
            actions.append("Create profiles on Upwork, Toptal, and Freelancer.com")
            actions.append("Set up a professional portfolio website")
        
        if opportunities.get("products"):
            actions.append("Choose one project to turn into MVP")
            actions.append("Research competitors and pricing")
        
        if opportunities.get("sponsorship"):
            actions.append("Set up GitHub Sponsors profile")
            actions.append("Create Patreon account")
        
        if opportunities.get("consulting"):
            actions.append("Update LinkedIn profile for consulting")
            actions.append("Join Clarity.fm as an expert")
        
        return actions[:5]  # Top 5 actions
    
    def _get_long_term_strategy(self, developer: DeveloperProfile, opportunities: Dict) -> str:
        """Create long-term monetization strategy"""
        strategy_parts = []
        
        if developer.total_projects > 5:
            strategy_parts.append("Build a portfolio of SaaS products")
        
        if developer.specializations:
            strategy_parts.append(f"Become a recognized expert in {developer.specializations[0]}")
        
        if opportunities.get("consulting"):
            strategy_parts.append("Transition from freelancing to high-value consulting")
        
        strategy_parts.append("Build passive income streams through courses and content")
        
        return " → ".join(strategy_parts)
    
    def _extract_monetization_strategies(self, analysis: str) -> List[Dict[str, Any]]:
        """Extract monetization strategies from AI analysis"""
        strategies = []
        
        # Simple extraction - enhance in production
        if "saas" in analysis.lower():
            strategies.append({
                "type": "SaaS",
                "potential": "$1000-10000/month",
                "timeline": "3-6 months",
                "difficulty": "medium"
            })
        
        if "api" in analysis.lower():
            strategies.append({
                "type": "API Service",
                "potential": "$500-5000/month",
                "timeline": "1-2 months",
                "difficulty": "low"
            })
        
        return strategies
    
    def _get_project_next_steps(self, strategies: List[Dict]) -> List[str]:
        """Get next steps for project monetization"""
        steps = []
        
        for strategy in strategies:
            if strategy["type"] == "SaaS":
                steps.extend([
                    "Define target customer persona",
                    "Create landing page to validate idea",
                    "Build MVP with core features",
                    "Set up payment processing"
                ])
            elif strategy["type"] == "API Service":
                steps.extend([
                    "Document API endpoints",
                    "Set up API key management",
                    "Create usage-based billing",
                    "Build developer portal"
                ])
        
        return steps[:6]  # Top 6 steps
    
    def _structure_skill_matches(self, matches: str, skills: Dict) -> Dict[str, List]:
        """Structure skill matching results"""
        return {
            "freelance_gigs": self._parse_freelance_opportunities(matches),
            "remote_jobs": [],  # Would parse from matches
            "consulting": [],  # Would parse from matches
            "side_projects": []  # Would parse from matches
        }
    
    def _identify_quick_wins(self, matches: Dict) -> List[Dict[str, Any]]:
        """Identify quick monetization wins"""
        quick_wins = []
        
        # Add freelance quick wins
        for gig in matches.get("freelance_gigs", [])[:3]:
            quick_wins.append({
                "type": "freelance",
                "description": gig.get("description", ""),
                "potential": gig.get("rate", "$50/hr"),
                "time_to_start": "This week"
            })
        
        return quick_wins
    
    def _identify_skill_gaps(self, analysis: str) -> List[str]:
        """Identify skills to learn for better opportunities"""
        # Simple extraction - enhance in production
        gaps = []
        
        high_value_skills = ["AWS", "Kubernetes", "React", "TypeScript", "Go", "Rust"]
        for skill in high_value_skills:
            if skill.lower() in analysis.lower():
                gaps.append(f"Learn {skill} to increase rates by 20-30%")
        
        return gaps[:3]
    
    def _create_30_day_plan(self, matches: Dict) -> List[Dict[str, Any]]:
        """Create 30-day monetization plan"""
        plan = [
            {
                "week": 1,
                "tasks": [
                    "Set up freelance profiles",
                    "Create portfolio website",
                    "Apply to 5 matching gigs"
                ]
            },
            {
                "week": 2,
                "tasks": [
                    "Start first freelance project",
                    "Network in relevant communities",
                    "Optimize profiles based on responses"
                ]
            },
            {
                "week": 3,
                "tasks": [
                    "Deliver first project",
                    "Get testimonials",
                    "Increase rates by 10%"
                ]
            },
            {
                "week": 4,
                "tasks": [
                    "Analyze what worked",
                    "Double down on successful strategies",
                    "Plan next month's targets"
                ]
            }
        ]
        
        return plan
    
    def _extract_top_opportunities(self, trends: str) -> List[str]:
        """Extract top opportunities from trends"""
        # Simple extraction
        opportunities = []
        
        keywords = ["high demand", "growing", "shortage", "needed"]
        lines = trends.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                opportunities.append(line.strip())
        
        return opportunities[:5]
    
    def _extract_trending_skills(self, trends: str) -> List[str]:
        """Extract trending skills from analysis"""
        skills = []
        
        # Look for skill mentions
        skill_keywords = ["learn", "skill", "technology", "framework", "language"]
        lines = trends.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in skill_keywords):
                skills.append(line.strip())
        
        return skills[:5]
    
    def _extract_hot_sectors(self, trends: str) -> List[str]:
        """Extract hot sectors from trends"""
        sectors = []
        
        sector_keywords = ["sector", "industry", "market", "companies"]
        lines = trends.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in sector_keywords):
                sectors.append(line.strip())
        
        return sectors[:5]
    
    def _extract_rate_recommendations(self, pricing_guide: str) -> Dict[str, str]:
        """Extract rate recommendations from pricing guide"""
        rates = {
            "minimum": "$50/hour",
            "standard": "$75/hour",
            "premium": "$150/hour"
        }
        
        # Extract actual rates from guide
        rate_matches = re.findall(r'\$(\d+)(?:-\$?(\d+))?/hour', pricing_guide)
        if rate_matches:
            if len(rate_matches) >= 1:
                rates["minimum"] = f"${rate_matches[0][0]}/hour"
            if len(rate_matches) >= 2:
                rates["standard"] = f"${rate_matches[1][0]}/hour"
            if len(rate_matches) >= 3:
                rates["premium"] = f"${rate_matches[2][0]}/hour"
        
        return rates
    
    def _create_pricing_calculator(self, skill_level: str, service_type: str) -> Dict[str, Any]:
        """Create pricing calculator based on parameters"""
        base_rates = {
            "beginner": 40,
            "intermediate": 75,
            "advanced": 120,
            "expert": 200
        }
        
        service_multipliers = {
            "freelance": 1.0,
            "consulting": 1.5,
            "training": 1.3,
            "retainer": 0.9
        }
        
        base_rate = base_rates.get(skill_level, 75)
        multiplier = service_multipliers.get(service_type, 1.0)
        
        return {
            "hourly_rate": f"${int(base_rate * multiplier)}/hour",
            "daily_rate": f"${int(base_rate * multiplier * 8)}/day",
            "weekly_rate": f"${int(base_rate * multiplier * 40)}/week",
            "monthly_retainer": f"${int(base_rate * multiplier * 160 * 0.8)}/month"
        }
    
    def _extract_action_items(self, advice: str) -> List[str]:
        """Extract action items from general advice"""
        action_items = []
        
        # Look for action-oriented lines
        action_keywords = ["create", "build", "start", "join", "apply", "set up", "develop"]
        lines = advice.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in action_keywords):
                action_items.append(line.strip())
        
        return action_items[:10]  # Top 10 actions