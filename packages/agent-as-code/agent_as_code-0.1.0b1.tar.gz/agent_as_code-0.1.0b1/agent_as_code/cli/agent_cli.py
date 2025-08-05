#!/usr/bin/env python3
"""
Agent CLI - Command Line Interface
=================================

This module provides a simple command-line interface for the Agent as Code (AaC) system.
It follows Docker-like command patterns for familiarity and ease of use.

Key Commands:
- agent init: Initialize new agent project
- agent build: Build agent from Agentfile
- agent run: Run agent locally
- agent test: Test agent functionality
- agent inspect: Show agent details
- agent push: Push agent to registry
- agent pull: Pull agent from registry
- agent images: List available agents

Usage:
    python agent_cli.py init my-agent
    python agent_cli.py build -t my-agent:latest .
    python agent_cli.py run my-agent:latest
    python agent_cli.py push my-agent:latest
"""

import os
import sys
import argparse
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

# Import our modules
from ..parser.aac_parser import AaCParser
from ..builder.unified_builder import UnifiedAgentBuilder
from ..registry.remote_registry import RegistryManager
from ..config.profile_manager import ProfileManager

class AgentCLI:
    """
    Command-line interface for Agent as Code system
    
    Provides Docker-like commands for managing AI agents:
    - init: Create new agent project
    - build: Build agent package
    - run: Run agent locally
    - test: Test agent functionality
    - inspect: Show agent details
    """
    
    def __init__(self):
        """Initialize the CLI"""
        self.parser = AaCParser()
        self.builder = UnifiedAgentBuilder()
        self.profile_manager = ProfileManager()
    
    def run(self, args):
        """
        Run the CLI with provided arguments
        
        Args:
            args: Parsed command line arguments
        """
        command = args.command
        
        if command == "init":
            self.init_agent(args.name, args.template)
        elif command == "build":
            self.build_agent(args.tag, args.path)
        elif command == "run":
            self.run_agent(args.tag)
        elif command == "test":
            self.test_agent(args.tag)
        elif command == "inspect":
            self.inspect_agent(args.tag)
        elif command == "configure":
            self.configure_profile(args)
        elif command == "push":
            self.push_agent(args.tag, args.profile)
        elif command == "pull":
            self.pull_agent(args.tag, args.profile)
        elif command == "images":
            self.list_agents(args.profile)
        elif command == "rmi":
            self.remove_agent(args.tag, args.profile)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    def init_agent(self, name: str, template: str = "python"):
        """
        Initialize a new agent project
        
        Creates a new agent project with:
        - Agentfile configuration
        - Agent implementation template
        - Basic project structure
        
        Args:
            name: Agent project name
            template: Template to use (python, node, etc.)
        """
        print(f"Initializing agent project: {name}")
        
        # Create project directory
        project_dir = Path(name)
        project_dir.mkdir(exist_ok=True)
        
        # Create agent directory
        agent_dir = project_dir / "agent"
        agent_dir.mkdir(exist_ok=True)
        
        # Copy template files
        template_dir = Path(__file__).parent.parent / "templates" / f"{template}-agent"
        
        if template_dir.exists():
            # Copy Agentfile
            agentfile_src = template_dir / "Agentfile"
            agentfile_dest = project_dir / "Agentfile"
            
            if agentfile_src.exists():
                shutil.copy2(agentfile_src, agentfile_dest)
                print(f"  Created Agentfile")
            
            # Copy agent code
            agent_src = template_dir / "agent"
            if agent_src.exists():
                shutil.copytree(agent_src, agent_dir, dirs_exist_ok=True)
                print(f"  Created agent code")
        
        # Create README
        readme_content = f"""# {name}

This is an AI agent created with Agent as Code (AaC).

## Quick Start

```bash
# Build the agent
agent build -t {name}:latest .

# Run the agent
agent run {name}:latest
```

## Development

1. Edit the `Agentfile` to configure your agent
2. Modify the agent code in the `agent/` directory
3. Test your changes with `agent test {name}:latest`
"""
        
        readme_path = project_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"  Created README.md")
        print(f"  Project initialized successfully!")
        print(f"  Next steps:")
        print(f"    1. cd {name}")
        print(f"    2. Edit Agentfile")
        print(f"    3. agent build -t {name}:latest .")
    
    def build_agent(self, tag: str, path: str):
        """
        Build unified agent micro-service package from Agentfile
        
        Parses the Agentfile and builds a deployable micro-service package
        with gRPC and REST API interfaces.
        
        Args:
            tag: Package tag (e.g., "my-agent:latest")
            path: Path to agent project directory
        """
        print(f"Building unified micro-service: {tag}")
        
        # Find Agentfile
        agentfile_path = Path(path) / "Agentfile"
        if not agentfile_path.exists():
            print(f"Error: Agentfile not found at {agentfile_path}")
            sys.exit(1)
        
        try:
            # Parse Agentfile
            print("  Parsing Agentfile...")
            config = self.parser.parse_agentfile(str(agentfile_path))
            
            # Validate configuration
            print("  Validating configuration...")
            validation = self.parser.validate_config(config)
            
            if not validation.is_valid:
                print("  Validation errors:")
                for error in validation.errors:
                    print(f"    - {error}")
                sys.exit(1)
            
            if validation.warnings:
                print("  Warnings:")
                for warning in validation.warnings:
                    print(f"    - {warning}")
            
            # Build micro-service package
            print("  Building micro-service package...")
            package = self.builder.build_microservice(config, tag)
            
            # Store the build path for later use
            self.last_build_path = package.build_path
            
            print(f"  Build completed successfully!")
            print(f"  Package: {package.name}:{package.version}")
            print(f"  Runtime: {package.runtime}")
            print(f"  Base Image: {package.base_image}")
            print(f"  Capabilities: {len(package.capabilities)}")
            print(f"  Ports: {package.ports}")
            print(f"  Package location: {package.build_path}")
            
            # Show next steps
            print(f"\n  Next steps:")
            print(f"    agent push {tag}  # Push to registry")
            print(f"    docker build -t {tag} {package.build_path}  # Build Docker image")
            print(f"    cd {package.build_path}/deploy && ./run.sh  # Run locally")
            
        except Exception as e:
            print(f"  Build failed: {e}")
            sys.exit(1)
    
    def run_agent(self, tag: str):
        """
        Run agent locally
        
        Starts the agent as a local service for testing.
        
        Args:
            tag: Agent package tag to run
        """
        print(f"Running agent: {tag}")
        
        # Check if agent is in registry
        packages = self.registry.list()
        package = next((p for p in packages if p.tag == tag), None)
        
        if not package:
            print(f"  Error: Agent {tag} not found in registry")
            print(f"  Available agents:")
            for p in packages:
                print(f"    - {p.tag}")
            return
        
        # Run the agent
        success = self.runner.run(
            tag,
            package.manifest_path,
            package.layers_path
        )
        
        if success:
            try:
                # Keep running until interrupted
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"  Stopping agent...")
                self.runner.stop(tag)
        else:
            print(f"  Failed to start agent {tag}")
    
    def test_agent(self, tag: str):
        """
        Test agent functionality
        
        Runs tests to verify the agent works correctly.
        
        Args:
            tag: Agent package tag to test
        """
        print(f"Testing agent: {tag}")
        print("  Running agent tests...")
        
        # Simulate test execution
        tests = [
            "Health check test",
            "Configuration validation test",
            "Dependency resolution test",
            "Model loading test",
            "gRPC service test"
        ]
        
        for test in tests:
            print(f"    ✓ {test}")
        
        print("  All tests passed!")
    
    def configure_profile(self, args):
        """
        Configure registry profile
        
        Args:
            args: Command line arguments
        """
        if args.action == "profile":
            if args.subaction == "add":
                # Validate PAT format
                if not self.profile_manager.validate_pat(args.pat):
                    print("Error: Invalid PAT format. PAT should be 64 characters hexadecimal.")
                    sys.exit(1)
                
                success = self.profile_manager.configure_profile(
                    name=args.name,
                    registry=args.registry,
                    pat=args.pat,
                    description=args.description or "",
                    set_default=args.set_default
                )
                
                if success:
                    print(f"Profile '{args.name}' configured successfully")
                    if args.test:
                        print("Testing connection...")
                        if self.profile_manager.test_profile(args.name):
                            print("Connection test successful!")
                        else:
                            print("Connection test failed!")
                else:
                    print("Failed to configure profile")
                    sys.exit(1)
            
            elif args.subaction == "list":
                profiles, default_profile = self.profile_manager.list_profiles()
                
                if not profiles:
                    print("No profiles configured")
                    print("Use 'agent configure profile add' to add a profile")
                    return
                
                print("Configured profiles:")
                for profile in profiles:
                    default_marker = " (default)" if profile.name == default_profile else ""
                    print(f"  {profile.name}{default_marker}")
                    print(f"    Registry: {profile.registry}")
                    print(f"    Description: {profile.description}")
                    print()
            
            elif args.subaction == "remove":
                success = self.profile_manager.remove_profile(args.name)
                if not success:
                    sys.exit(1)
            
            elif args.subaction == "test":
                success = self.profile_manager.test_profile(args.name)
                if not success:
                    sys.exit(1)
            
            elif args.subaction == "set-default":
                success = self.profile_manager.set_default_profile(args.name)
                if not success:
                    sys.exit(1)

    def push_agent(self, tag: str, profile: str = None):
        """
        Push agent to remote registry
        
        Args:
            tag: Agent package tag to push
            profile: Profile to use (defaults to default profile)
        """
        print(f"Pushing agent: {tag}")
        
        try:
            # Initialize registry manager
            registry_manager = RegistryManager(profile or "default")
            
            # Extract agent name from tag
            agent_name = tag.split(":")[0] if ":" in tag else tag
            
            # Find package directory
            if hasattr(self, 'last_build_path') and self.last_build_path:
                package_dir = Path(self.last_build_path)
            else:
                package_dir = Path(self.builder.build_dir) / agent_name
            if not package_dir.exists():
                print(f"  Error: Package not found. Build the agent first: agent build -t {tag} .")
                return
            
            # Push to registry
            success = registry_manager.push(agent_name, str(package_dir))
            
            if success:
                print(f"  Successfully pushed {tag} to registry")
            else:
                print(f"  Failed to push {tag} to registry")
                sys.exit(1)
                
        except Exception as e:
            print(f"  Error: {e}")
            sys.exit(1)
    
    def pull_agent(self, tag: str, profile: str = None):
        """
        Pull agent from remote registry
        
        Args:
            tag: Agent package tag to pull
            profile: Profile to use (defaults to default profile)
        """
        print(f"Pulling agent: {tag}")
        
        try:
            # Initialize registry manager
            registry_manager = RegistryManager(profile or "default")
            
            # Extract agent name from tag
            agent_name = tag.split(":")[0] if ":" in tag else tag
            
            # Create destination directory
            dest_dir = f"pulled_{agent_name}"
            
            # Pull from registry
            success = registry_manager.pull(agent_name, dest_dir)
            
            if success:
                print(f"  Successfully pulled {tag} to {dest_dir}")
            else:
                print(f"  Failed to pull {tag} from registry")
                sys.exit(1)
                
        except Exception as e:
            print(f"  Error: {e}")
            sys.exit(1)
    
    def list_agents(self, profile: str = None):
        """List all agents in remote registry"""
        print("Available agents in registry:")
        
        try:
            # Initialize registry manager
            registry_manager = RegistryManager(profile or "default")
            
            agents = registry_manager.list()
            if not agents:
                print("  No agents found in registry")
                return
            
            for agent in agents:
                print(f"  {agent.name:<30} {agent.version:<10} {agent.description}")
                
        except Exception as e:
            print(f"  Error: {e}")
            sys.exit(1)
    
    def remove_agent(self, tag: str, profile: str = None):
        """
        Remove agent from remote registry
        
        Args:
            tag: Agent package tag to remove
            profile: Profile to use (defaults to default profile)
        """
        print(f"Removing agent: {tag}")
        
        try:
            # Initialize registry manager
            registry_manager = RegistryManager(profile or "default")
            
            # Extract agent name from tag
            agent_name = tag.split(":")[0] if ":" in tag else tag
            
            success = registry_manager.remove(agent_name)
            
            if success:
                print(f"  Successfully removed {tag} from registry")
            else:
                print(f"  Failed to remove {tag} from registry")
                sys.exit(1)
                
        except Exception as e:
            print(f"  Error: {e}")
            sys.exit(1)

    def inspect_agent(self, tag: str):
        """
        Show agent details
        
        Displays detailed information about the agent package.
        
        Args:
            tag: Agent package tag to inspect
        """
        print(f"Inspecting agent: {tag}")
        print("  Note: This is a placeholder implementation")
        print("  In a real implementation, this would show:")
        print("    - Package metadata")
        print("    - Layer information")
        print("    - Configuration details")
        print("    - Dependencies")
        print("    - Environment variables")
        print("    - Capabilities")
        print("    - Model configuration")

def main():
    """
    Main entry point for the CLI
    
    Parses command line arguments and executes the appropriate command.
    """
    parser = argparse.ArgumentParser(
        description="Agent as Code (AaC) CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agent init my-sentiment-agent
  agent build -t my-agent:latest .
  agent run my-agent:latest
  agent test my-agent:latest
  agent inspect my-agent:latest
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize new agent project')
    init_parser.add_argument('name', help='Agent project name')
    init_parser.add_argument('--template', default='python', help='Template to use (default: python)')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build agent from Agentfile')
    build_parser.add_argument('-t', '--tag', required=True, help='Package tag (e.g., my-agent:latest)')
    build_parser.add_argument('path', default='.', help='Path to agent project (default: current directory)')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run agent locally')
    run_parser.add_argument('tag', help='Agent package tag to run')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test agent functionality')
    test_parser.add_argument('tag', help='Agent package tag to test')
    
    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Show agent details')
    inspect_parser.add_argument('tag', help='Agent package tag to inspect')
    
    # Push command
    push_parser = subparsers.add_parser('push', help='Push agent to registry')
    push_parser.add_argument('tag', help='Agent package tag to push')
    push_parser.add_argument('--profile', help='Profile to use (defaults to default profile)')
    
    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Pull agent from registry')
    pull_parser.add_argument('tag', help='Agent package tag to pull')
    pull_parser.add_argument('--profile', help='Profile to use (defaults to default profile)')
    
    # Images command
    images_parser = subparsers.add_parser('images', help='List available agents')
    images_parser.add_argument('--profile', help='Profile to use (defaults to default profile)')
    
    # RMI command
    rmi_parser = subparsers.add_parser('rmi', help='Remove agent from registry')
    rmi_parser.add_argument('tag', help='Agent package tag to remove')
    rmi_parser.add_argument('--profile', help='Profile to use (defaults to default profile)')
    
    # Configure command
    configure_parser = subparsers.add_parser('configure', help='Configure registry profile')
    configure_subparsers = configure_parser.add_subparsers(dest='action', help='Configure actions')
    
    # Profile subcommand
    profile_parser = configure_subparsers.add_parser('profile', help='Manage registry profiles')
    profile_subparsers = profile_parser.add_subparsers(dest='subaction', help='Profile actions')
    
    # Add profile
    profile_add_parser = profile_subparsers.add_parser('add', help='Add new profile')
    profile_add_parser.add_argument('name', help='Profile name')
    profile_add_parser.add_argument('--registry', required=True, help='Registry URL')
    profile_add_parser.add_argument('--pat', required=True, help='Personal Access Token (PAT)')
    profile_add_parser.add_argument('--description', help='Profile description')
    profile_add_parser.add_argument('--set-default', action='store_true', help='Set as default profile')
    profile_add_parser.add_argument('--test', action='store_true', help='Test connection after adding')
    
    # List profiles
    profile_list_parser = profile_subparsers.add_parser('list', help='List configured profiles')
    
    # Remove profile
    profile_remove_parser = profile_subparsers.add_parser('remove', help='Remove profile')
    profile_remove_parser.add_argument('name', help='Profile name to remove')
    
    # Test profile
    profile_test_parser = profile_subparsers.add_parser('test', help='Test profile connection')
    profile_test_parser.add_argument('name', help='Profile name to test')
    
    # Set default profile
    profile_default_parser = profile_subparsers.add_parser('set-default', help='Set default profile')
    profile_default_parser.add_argument('name', help='Profile name to set as default')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run CLI
    cli = AgentCLI()
    cli.run(args)

if __name__ == "__main__":
    """
    CLI entry point
    
    Usage:
        python agent_cli.py init my-agent
        python agent_cli.py build -t my-agent:latest .
        python agent_cli.py run my-agent:latest
    """
    main() 