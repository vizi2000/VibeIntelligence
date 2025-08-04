#!/usr/bin/env python3
"""
Project Analysis Report Generator
Analyzes the inventory data and generates actionable insights
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def load_inventory_report(path: str) -> Dict:
    """Load the inventory report JSON"""
    with open(path, 'r') as f:
        return json.load(f)

def analyze_duplicates(report: Dict) -> str:
    """Analyze duplicate projects and generate recommendations"""
    output = ["## Duplicate Projects Analysis\n"]
    duplicate_groups = report.get('duplicate_groups', [])
    
    output.append(f"Found {len(duplicate_groups)} groups of potential duplicates:\n")
    
    # Group duplicates by project type
    xpress_duplicates = []
    other_duplicates = []
    
    for group in duplicate_groups:
        if any('xpress' in path.lower() for path in group):
            xpress_duplicates.append(group)
        else:
            other_duplicates.append(group)
    
    if xpress_duplicates:
        output.append(f"\n### Xpress Delivery Duplicates ({len(xpress_duplicates)} groups)")
        output.append("These appear to be multiple versions of the same project:")
        for i, group in enumerate(xpress_duplicates[:5], 1):  # Show first 5
            output.append(f"\n**Group {i}:**")
            for path in group:
                output.append(f"  - {path}")
        if len(xpress_duplicates) > 5:
            output.append(f"\n... and {len(xpress_duplicates) - 5} more groups")
    
    if other_duplicates:
        output.append(f"\n### Other Duplicates ({len(other_duplicates)} groups)")
        for i, group in enumerate(other_duplicates[:5], 1):  # Show first 5
            output.append(f"\n**Group {i}:**")
            for path in group:
                output.append(f"  - {path}")
        if len(other_duplicates) > 5:
            output.append(f"\n... and {len(other_duplicates) - 5} more groups")
    
    output.append("\n### Recommendations:")
    output.append("1. **Xpress Delivery**: Consolidate all versions into a single project with version control")
    output.append("2. **Archive old versions**: Move outdated versions to archived-projects/")
    output.append("3. **Remove zip files**: Delete zip archives where extracted folders exist")
    
    return '\n'.join(output)

def analyze_undocumented(report: Dict) -> str:
    """Analyze undocumented projects"""
    output = ["## Undocumented Projects Analysis\n"]
    undocumented = report.get('undocumented_projects', [])
    projects = report.get('projects', [])
    
    output.append(f"Found {len(undocumented)} projects without documentation:\n")
    
    # Categorize undocumented projects
    undoc_by_type = {}
    for path in undocumented:
        project = next((p for p in projects if p['path'] == path), None)
        if project:
            ptype = project.get('project_type', 'Unknown')
            if ptype not in undoc_by_type:
                undoc_by_type[ptype] = []
            undoc_by_type[ptype].append(path)
    
    for ptype, paths in sorted(undoc_by_type.items()):
        output.append(f"\n### {ptype} ({len(paths)} projects)")
        for path in paths[:3]:  # Show first 3
            output.append(f"  - {path}")
        if len(paths) > 3:
            output.append(f"  ... and {len(paths) - 3} more")
    
    output.append("\n### Priority Documentation Targets:")
    output.append("1. Active/deployed projects (check DEPLOYMENT_REGISTRY.md)")
    output.append("2. Projects with Docker configurations")
    output.append("3. Projects larger than 50MB")
    
    return '\n'.join(output)

def analyze_tech_debt(report: Dict) -> str:
    """Analyze technical debt indicators"""
    output = ["## Technical Debt Analysis\n"]
    projects = report.get('projects', [])
    
    # Find problematic patterns
    no_git = [p for p in projects if not p.get('is_git_repo')]
    large_projects = [p for p in projects if p.get('size_mb', 0) > 100]
    
    output.append(f"### Version Control Issues")
    output.append(f"- {len(no_git)} projects without Git repositories")
    output.append(f"- Recommendation: Initialize Git for all active projects\n")
    
    output.append(f"### Large Projects (>100MB)")
    for project in sorted(large_projects, key=lambda x: x['size_mb'], reverse=True)[:5]:
        output.append(f"- {project['name']}: {project['size_mb']:.1f} MB")
    output.append("- Recommendation: Check for unnecessary files, build artifacts, or media files\n")
    
    output.append("### Mixed Content Issues")
    output.append("- Multiple images and PDFs in root directory")
    output.append("- Zip files alongside extracted folders")
    output.append("- Recommendation: Organize into proper directory structure")
    
    return '\n'.join(output)

def generate_action_plan(report: Dict) -> str:
    """Generate prioritized action plan"""
    output = ["## Prioritized Action Plan\n"]
    
    output.append("### Immediate Actions (Week 1)")
    output.append("1. **Backup Everything**")
    output.append("   - Create timestamped backup of entire AI folder")
    output.append("   - Verify backup integrity before proceeding\n")
    
    output.append("2. **Set Up Zenith Coder**")
    output.append("   - Create project structure in zenith coder folder")
    output.append("   - Initialize Git repository")
    output.append("   - Set up basic FastAPI backend\n")
    
    output.append("3. **Organize Active Projects**")
    output.append("   - Identify currently deployed projects from DEPLOYMENT_REGISTRY.md")
    output.append("   - Ensure they have proper documentation")
    output.append("   - Move to active-projects/ directory\n")
    
    output.append("### Short-term Actions (Week 2-3)")
    output.append("1. **Handle Duplicates**")
    output.append("   - Consolidate Xpress Delivery versions")
    output.append("   - Archive old versions with timestamps")
    output.append("   - Remove redundant zip files\n")
    
    output.append("2. **Organize Resources**")
    output.append("   - Move images to resources/images/")
    output.append("   - Move PDFs to resources/documents/")
    output.append("   - Create index of resources\n")
    
    output.append("### Medium-term Actions (Week 4+)")
    output.append("1. **Documentation Sprint**")
    output.append("   - Generate README for top 20 projects")
    output.append("   - Add CLAUDE.md to active projects")
    output.append("   - Create project dependency graphs\n")
    
    output.append("2. **Automation Setup**")
    output.append("   - Deploy Zenith Coder dashboard")
    output.append("   - Implement continuous monitoring")
    output.append("   - Set up automated backups")
    
    return '\n'.join(output)

def generate_markdown_report(report: Dict) -> str:
    """Generate comprehensive markdown report"""
    output = [
        "# AI Projects Organization Report",
        f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Projects**: {report['summary']['total_projects']}",
        f"**Total Size**: {report['summary']['total_size_gb']:.2f} GB\n",
        "---\n"
    ]
    
    # Add summary statistics
    output.append("## Summary Statistics\n")
    output.append("| Metric | Value |")
    output.append("|--------|-------|")
    for key, value in report['summary'].items():
        if key != 'total_size_gb':
            output.append(f"| {key.replace('_', ' ').title()} | {value} |")
    output.append("")
    
    # Add analyses
    output.append(analyze_duplicates(report))
    output.append("")
    output.append(analyze_undocumented(report))
    output.append("")
    output.append(analyze_tech_debt(report))
    output.append("")
    output.append(generate_action_plan(report))
    
    # Add tech stack distribution
    output.append("\n## Technology Stack Distribution\n")
    output.append("| Technology | Project Count |")
    output.append("|------------|---------------|")
    for tech, count in sorted(report['tech_stacks'].items(), key=lambda x: x[1], reverse=True)[:10]:
        output.append(f"| {tech} | {count} |")
    
    # Add project type distribution
    output.append("\n## Project Type Distribution\n")
    output.append("| Type | Count |")
    output.append("|------|-------|")
    for ptype, count in sorted(report['project_types'].items(), key=lambda x: x[1], reverse=True):
        output.append(f"| {ptype} | {count} |")
    
    return '\n'.join(output)

def main():
    # Load the inventory report
    report_path = '/Users/wojciechwiesner/ai/zenith coder/project_inventory_report.json'
    report = load_inventory_report(report_path)
    
    # Generate markdown report
    markdown_report = generate_markdown_report(report)
    
    # Save markdown report
    output_path = '/Users/wojciechwiesner/ai/zenith coder/PROJECT_ORGANIZATION_REPORT.md'
    with open(output_path, 'w') as f:
        f.write(markdown_report)
    
    print(f"Organization report generated: {output_path}")
    
    # Also generate a quick actions file
    quick_actions = [
        "# Quick Actions Checklist\n",
        "## Immediate Tasks",
        "- [ ] Create backup of AI folder",
        "- [ ] Review DEPLOYMENT_REGISTRY.md for active projects",
        "- [ ] Set up Zenith Coder project structure",
        "- [ ] Initialize Git repository for Zenith Coder\n",
        "## This Week",
        "- [ ] Move active projects to active-projects/",
        "- [ ] Consolidate Xpress Delivery duplicates",
        "- [ ] Move images and PDFs to resources/",
        "- [ ] Delete redundant zip files\n",
        "## Next Week",
        "- [ ] Generate documentation for top projects",
        "- [ ] Set up Docker environment for Zenith Coder",
        "- [ ] Create project dashboard",
        "- [ ] Implement automated scanning"
    ]
    
    actions_path = '/Users/wojciechwiesner/ai/zenith coder/QUICK_ACTIONS.md'
    with open(actions_path, 'w') as f:
        f.write('\n'.join(quick_actions))
    
    print(f"Quick actions checklist generated: {actions_path}")

if __name__ == "__main__":
    main()