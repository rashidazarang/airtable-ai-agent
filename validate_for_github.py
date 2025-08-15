#!/usr/bin/env python3
"""
✅ GitHub Deployment Validation Script
Final validation that everything is ready for GitHub deployment.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any

def validate_file_structure() -> List[Dict[str, Any]]:
    """Validate all required files exist"""
    issues = []
    required_files = [
        # Core application files
        "src/__init__.py",
        "src/agent.py",
        "src/agent_basic.py", 
        "src/context_manager.py",
        "src/context_manager_basic.py",
        "src/mcp_client.py",
        "src/airtable_expert.py",
        
        # Documentation files
        "docs/airtable-web-api-complete.md",
        "docs/airtable-js-complete.md",
        "docs/mcp-integration-complete.md",
        "docs/airtable-formulas-complete.md",
        "docs/airtable-apps-extensions.md",
        
        # Configuration files
        "requirements.txt",
        "requirements-basic.txt",
        "Dockerfile",
        "Dockerfile.test",
        "docker-compose.yml",
        
        # CI/CD files
        ".github/workflows/ci-cd.yml",
        
        # Test files
        "tests/test_agent.py",
        "test_complete.py",
        
        # Project files
        "README.md",
        "__init__.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append({
                'type': 'missing_file',
                'severity': 'high',
                'message': f"Required file missing: {file_path}"
            })
    
    return issues

def validate_readme() -> List[Dict[str, Any]]:
    """Validate README.md content"""
    issues = []
    
    try:
        readme_path = Path("README.md")
        if not readme_path.exists():
            issues.append({
                'type': 'missing_readme',
                'severity': 'high',
                'message': "README.md is missing"
            })
            return issues
        
        content = readme_path.read_text()
        
        required_sections = [
            "# 🤖 Airtable AI Agent",
            "## 🚀 Quick Start",
            "## 💬 Usage Examples",
            "## 🎯 Core Features",
            "## 🔧 Configuration",
            "## 🚀 Deployment",
            "## 🧪 Testing"
        ]
        
        for section in required_sections:
            if section not in content:
                issues.append({
                    'type': 'missing_readme_section',
                    'severity': 'medium',
                    'message': f"Missing README section: {section}"
                })
        
        # Check for placeholder content
        if "your_token_here" in content.lower() or "example.com" in content.lower():
            issues.append({
                'type': 'placeholder_content',
                'severity': 'low',
                'message': "README contains placeholder content - update before deployment"
            })
            
    except Exception as e:
        issues.append({
            'type': 'readme_error',
            'severity': 'high',
            'message': f"Error validating README: {e}"
        })
    
    return issues

def validate_docker_files() -> List[Dict[str, Any]]:
    """Validate Docker configuration"""
    issues = []
    
    # Check Dockerfile
    dockerfile_path = Path("Dockerfile")
    if dockerfile_path.exists():
        content = dockerfile_path.read_text()
        
        if "COPY requirements.txt" not in content:
            issues.append({
                'type': 'docker_requirements',
                'severity': 'medium',
                'message': "Dockerfile should copy requirements.txt"
            })
        
        if "EXPOSE" not in content:
            issues.append({
                'type': 'docker_expose',
                'severity': 'medium',
                'message': "Dockerfile should expose a port"
            })
    
    # Check docker-compose.yml
    compose_path = Path("docker-compose.yml")
    if compose_path.exists():
        try:
            import yaml
            with open(compose_path) as f:
                compose_data = yaml.safe_load(f)
            
            if 'services' not in compose_data:
                issues.append({
                    'type': 'compose_structure',
                    'severity': 'high',
                    'message': "docker-compose.yml missing services section"
                })
                
        except Exception as e:
            issues.append({
                'type': 'compose_parse_error',
                'severity': 'high',
                'message': f"Error parsing docker-compose.yml: {e}"
            })
    
    return issues

def validate_github_actions() -> List[Dict[str, Any]]:
    """Validate GitHub Actions workflow"""
    issues = []
    
    workflow_path = Path(".github/workflows/ci-cd.yml")
    if not workflow_path.exists():
        issues.append({
            'type': 'missing_workflow',
            'severity': 'high',
            'message': "GitHub Actions workflow file missing"
        })
        return issues
    
    try:
        import yaml
        with open(workflow_path) as f:
            workflow_data = yaml.safe_load(f)
        
        # Check for required jobs
        jobs = workflow_data.get('jobs', {})
        required_jobs = ['quality', 'test', 'build']
        
        for job in required_jobs:
            if job not in jobs:
                issues.append({
                    'type': 'missing_job',
                    'severity': 'medium',
                    'message': f"Missing CI job: {job}"
                })
                
    except Exception as e:
        issues.append({
            'type': 'workflow_parse_error',
            'severity': 'high',
            'message': f"Error parsing workflow file: {e}"
        })
    
    return issues

def validate_requirements() -> List[Dict[str, Any]]:
    """Validate requirements.txt files"""
    issues = []
    
    for req_file in ["requirements.txt", "requirements-basic.txt"]:
        if Path(req_file).exists():
            try:
                with open(req_file) as f:
                    content = f.read()
                
                # Check for version pins
                lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                unpinned = [line for line in lines if '>=' not in line and '==' not in line and '~=' not in line]
                
                if unpinned:
                    issues.append({
                        'type': 'unpinned_dependencies',
                        'severity': 'low',
                        'message': f"{req_file} has unpinned dependencies: {unpinned}"
                    })
                    
            except Exception as e:
                issues.append({
                    'type': 'requirements_error',
                    'severity': 'medium',
                    'message': f"Error reading {req_file}: {e}"
                })
    
    return issues

async def validate_functionality():
    """Run basic functionality tests"""
    issues = []
    
    try:
        # Import test
        import sys
        sys.path.insert(0, str(Path.cwd()))
        
        from src.agent_basic import AirtableAIAgentBasic
        
        # Quick initialization test
        agent = AirtableAIAgentBasic()
        await agent.initialize()
        
        # Quick query test
        response = await agent.process_query("What is Airtable?")
        
        if not response.get('answer'):
            issues.append({
                'type': 'functionality_error',
                'severity': 'high',
                'message': "Agent not responding to queries properly"
            })
        
        await agent.shutdown()
        
    except Exception as e:
        issues.append({
            'type': 'functionality_error',
            'severity': 'high',
            'message': f"Basic functionality test failed: {e}"
        })
    
    return issues

async def main():
    """Run complete validation suite"""
    print("🔍 GitHub Deployment Validation")
    print("=" * 50)
    
    all_issues = []
    
    # Run all validations
    validations = [
        ("File Structure", validate_file_structure()),
        ("README Content", validate_readme()),
        ("Docker Configuration", validate_docker_files()),
        ("GitHub Actions", validate_github_actions()),
        ("Requirements", validate_requirements()),
        ("Basic Functionality", await validate_functionality())
    ]
    
    for name, issues in validations:
        print(f"\n📋 {name}")
        if not issues:
            print("   ✅ All checks passed")
        else:
            for issue in issues:
                severity = issue['severity'].upper()
                icon = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🔵"
                print(f"   {icon} [{severity}] {issue['message']}")
            all_issues.extend(issues)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Validation Summary")
    print("=" * 50)
    
    high_issues = [i for i in all_issues if i['severity'] == 'high']
    medium_issues = [i for i in all_issues if i['severity'] == 'medium']
    low_issues = [i for i in all_issues if i['severity'] == 'low']
    
    print(f"🔴 High severity issues: {len(high_issues)}")
    print(f"🟡 Medium severity issues: {len(medium_issues)}")
    print(f"🔵 Low severity issues: {len(low_issues)}")
    
    # Overall assessment
    if len(high_issues) == 0:
        if len(medium_issues) <= 2:
            print("\n🎉 READY FOR GITHUB DEPLOYMENT!")
            print("   The project meets all requirements for public release.")
            deployment_ready = True
        else:
            print("\n⚠️  MOSTLY READY - Address medium issues for best results")
            deployment_ready = True
    else:
        print("\n❌ NOT READY - Fix high severity issues first")
        deployment_ready = False
    
    # Provide next steps
    print("\n📝 Next Steps:")
    if deployment_ready:
        print("   1. Address any remaining medium/low issues")
        print("   2. Update placeholder content in README")
        print("   3. Test Docker build if Docker daemon available")
        print("   4. Create GitHub repository and push code")
        print("   5. Verify GitHub Actions workflow runs successfully")
    else:
        print("   1. Fix all high severity issues")
        print("   2. Re-run validation script")
        print("   3. Address medium and low issues")
        print("   4. Proceed with deployment")
    
    return deployment_ready

if __name__ == "__main__":
    import sys
    
    # Suppress some logging for cleaner output
    import logging
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)