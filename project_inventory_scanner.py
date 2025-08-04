#!/usr/bin/env python3
"""
Project Inventory Scanner for AI Projects
Scans the AI directory and creates a comprehensive inventory of all projects
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
import subprocess

class ProjectInventoryScanner:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.projects = []
        self.duplicates = {}
        self.file_types = {}
        self.tech_stacks = {}
        
    def scan_directory(self) -> Dict:
        """Scan the entire AI directory and collect project information"""
        print(f"Scanning directory: {self.base_path}")
        
        for root, dirs, files in os.walk(self.base_path):
            # Skip hidden directories and node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            root_path = Path(root)
            
            # Check if this is a project root
            if self._is_project_root(root_path, files):
                project_info = self._analyze_project(root_path, files)
                self.projects.append(project_info)
                
            # Collect file type statistics
            for file in files:
                ext = Path(file).suffix.lower()
                self.file_types[ext] = self.file_types.get(ext, 0) + 1
                
        return self._generate_report()
    
    def _is_project_root(self, path: Path, files: List[str]) -> bool:
        """Determine if a directory is a project root"""
        project_indicators = {
            'package.json', 'requirements.txt', 'setup.py', 'Dockerfile',
            'docker-compose.yml', '.git', 'README.md', 'pom.xml',
            'build.gradle', 'Cargo.toml', 'go.mod', '*.csproj'
        }
        
        for indicator in project_indicators:
            if indicator in files:
                return True
            if indicator.startswith('*'):
                ext = indicator[1:]
                if any(f.endswith(ext) for f in files):
                    return True
                    
        return False
    
    def _analyze_project(self, path: Path, files: List[str]) -> Dict:
        """Analyze a project directory"""
        project_info = {
            'name': path.name,
            'path': str(path),
            'relative_path': str(path.relative_to(self.base_path)),
            'files': files,
            'tech_stack': self._detect_tech_stack(path, files),
            'has_readme': 'README.md' in files or 'readme.md' in files,
            'has_documentation': self._check_documentation(files),
            'is_git_repo': '.git' in os.listdir(path) if os.path.isdir(path) else False,
            'size_mb': self._get_directory_size(path) / (1024 * 1024),
            'last_modified': self._get_last_modified(path),
            'project_type': self._detect_project_type(path, files),
            'has_docker': 'Dockerfile' in files or 'docker-compose.yml' in files,
            'potential_duplicates': []
        }
        
        # Check for deployment info
        if 'docker-compose.yml' in files:
            project_info['docker_compose_file'] = 'docker-compose.yml'
            
        return project_info
    
    def _detect_tech_stack(self, path: Path, files: List[str]) -> List[str]:
        """Detect the technology stack of a project"""
        tech_stack = []
        
        # Check for various technology indicators
        tech_indicators = {
            'package.json': ['Node.js', 'JavaScript'],
            'requirements.txt': ['Python'],
            'setup.py': ['Python'],
            'Pipfile': ['Python'],
            'Dockerfile': ['Docker'],
            'docker-compose.yml': ['Docker Compose'],
            'pom.xml': ['Java', 'Maven'],
            'build.gradle': ['Java', 'Gradle'],
            'Cargo.toml': ['Rust'],
            'go.mod': ['Go'],
            'composer.json': ['PHP'],
            'Gemfile': ['Ruby'],
            '.csproj': ['.NET', 'C#']
        }
        
        for indicator, techs in tech_indicators.items():
            if indicator in files:
                tech_stack.extend(techs)
            elif indicator.endswith('proj'):
                if any(f.endswith(indicator) for f in files):
                    tech_stack.extend(techs)
                    
        # Check package.json for specific frameworks
        if 'package.json' in files:
            try:
                with open(path / 'package.json', 'r') as f:
                    package_data = json.load(f)
                    deps = package_data.get('dependencies', {})
                    dev_deps = package_data.get('devDependencies', {})
                    all_deps = {**deps, **dev_deps}
                    
                    if 'react' in all_deps:
                        tech_stack.append('React')
                    if 'vue' in all_deps:
                        tech_stack.append('Vue')
                    if 'angular' in all_deps:
                        tech_stack.append('Angular')
                    if 'next' in all_deps:
                        tech_stack.append('Next.js')
                    if 'express' in all_deps:
                        tech_stack.append('Express')
                    if 'fastapi' in all_deps:
                        tech_stack.append('FastAPI')
            except:
                pass
                
        return list(set(tech_stack))
    
    def _check_documentation(self, files: List[str]) -> bool:
        """Check if project has documentation"""
        doc_files = ['README.md', 'readme.md', 'DOCUMENTATION.md', 'docs', 
                     'CONTRIBUTING.md', 'CHANGELOG.md', 'LICENSE']
        return any(doc in files for doc in doc_files)
    
    def _get_directory_size(self, path: Path) -> float:
        """Get the total size of a directory in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except:
            pass
        return total_size
    
    def _get_last_modified(self, path: Path) -> str:
        """Get the last modified date of a directory"""
        try:
            timestamp = os.path.getmtime(path)
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return 'Unknown'
    
    def _detect_project_type(self, path: Path, files: List[str]) -> str:
        """Detect the type of project"""
        name_lower = path.name.lower()
        
        # Check by name patterns
        if 'xpress' in name_lower or 'delivery' in name_lower:
            return 'Xpress Delivery'
        elif 'agent' in name_lower:
            return 'AI Agent'
        elif 'borg' in name_lower:
            return 'Borg Tools'
        elif 'charity' in name_lower:
            return 'CharityPay'
        elif 'auction' in name_lower or 'scraper' in name_lower:
            return 'Web Scraper'
        elif 'vote' in name_lower or 'voting' in name_lower:
            return 'Voting Tool'
        elif 'test' in name_lower or 'demo' in name_lower:
            return 'Test/Demo'
        
        # Check by tech stack
        tech_stack = self._detect_tech_stack(path, files)
        if 'React' in tech_stack or 'Vue' in tech_stack:
            return 'Web Application'
        elif 'FastAPI' in tech_stack or 'Express' in tech_stack:
            return 'API/Backend'
        elif 'Python' in tech_stack and not any(web in tech_stack for web in ['FastAPI', 'Flask', 'Django']):
            return 'Python Script/Tool'
            
        return 'Unknown'
    
    def _find_duplicates(self):
        """Find potential duplicate projects"""
        # Group projects by normalized name
        name_groups = {}
        for project in self.projects:
            # Normalize name for comparison
            normalized = project['name'].lower().replace('-', '').replace('_', '').replace(' ', '')
            # Remove version numbers
            normalized = ''.join([c for c in normalized if not c.isdigit()])
            
            if normalized not in name_groups:
                name_groups[normalized] = []
            name_groups[normalized].append(project)
        
        # Mark duplicates
        for group_name, group_projects in name_groups.items():
            if len(group_projects) > 1:
                for project in group_projects:
                    project['potential_duplicates'] = [
                        p['path'] for p in group_projects if p['path'] != project['path']
                    ]
    
    def _generate_report(self) -> Dict:
        """Generate a comprehensive report"""
        self._find_duplicates()
        
        # Count projects by type
        project_types = {}
        for project in self.projects:
            ptype = project['project_type']
            project_types[ptype] = project_types.get(ptype, 0) + 1
        
        # Count tech stacks
        all_tech_stacks = {}
        for project in self.projects:
            for tech in project['tech_stack']:
                all_tech_stacks[tech] = all_tech_stacks.get(tech, 0) + 1
        
        # Find projects without documentation
        undocumented = [p for p in self.projects if not p['has_documentation']]
        
        # Find duplicate groups
        duplicate_groups = {}
        for project in self.projects:
            if project['potential_duplicates']:
                key = tuple(sorted([project['path']] + project['potential_duplicates']))
                if key not in duplicate_groups:
                    duplicate_groups[key] = []
                duplicate_groups[key].append(project['path'])
        
        # Clean duplicate groups
        unique_duplicate_groups = []
        seen = set()
        for paths in duplicate_groups.values():
            key = tuple(sorted(paths))
            if key not in seen:
                seen.add(key)
                unique_duplicate_groups.append(list(key))
        
        report = {
            'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'base_path': str(self.base_path),
            'summary': {
                'total_projects': len(self.projects),
                'total_size_gb': sum(p['size_mb'] for p in self.projects) / 1024,
                'projects_with_docker': len([p for p in self.projects if p['has_docker']]),
                'projects_with_git': len([p for p in self.projects if p['is_git_repo']]),
                'undocumented_projects': len(undocumented),
                'duplicate_groups': len(unique_duplicate_groups)
            },
            'project_types': project_types,
            'tech_stacks': all_tech_stacks,
            'file_types': dict(sorted(self.file_types.items(), key=lambda x: x[1], reverse=True)[:20]),
            'projects': sorted(self.projects, key=lambda x: x['name']),
            'undocumented_projects': [p['path'] for p in undocumented],
            'duplicate_groups': unique_duplicate_groups
        }
        
        return report

def main():
    scanner = ProjectInventoryScanner('/Users/wojciechwiesner/ai')
    report = scanner.scan_directory()
    
    # Save report as JSON
    output_path = '/Users/wojciechwiesner/ai/zenith coder/project_inventory_report.json'
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("PROJECT INVENTORY SCAN COMPLETE")
    print("="*60)
    print(f"Total Projects Found: {report['summary']['total_projects']}")
    print(f"Total Size: {report['summary']['total_size_gb']:.2f} GB")
    print(f"Projects with Docker: {report['summary']['projects_with_docker']}")
    print(f"Undocumented Projects: {report['summary']['undocumented_projects']}")
    print(f"Duplicate Groups: {report['summary']['duplicate_groups']}")
    print("\nProject Types:")
    for ptype, count in report['project_types'].items():
        print(f"  - {ptype}: {count}")
    print("\nTop Tech Stacks:")
    for tech, count in sorted(report['tech_stacks'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {tech}: {count}")
    print(f"\nFull report saved to: {output_path}")

if __name__ == "__main__":
    main()