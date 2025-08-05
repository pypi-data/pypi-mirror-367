#!/usr/bin/env python3
"""
Test script to reproduce the exact user issue.
"""

import os
import tempfile
import shutil
from pathlib import Path

# Add the current directory to Python path
import sys
sys.path.insert(0, '.')

from a3 import A3

def test_user_exact_code():
    """Test the exact user code."""
    
    # Use the exact same path structure as user
    project_path = r"C:\Users\milin\Documents\A3 Testing User Issue"
    project_path_obj = Path(project_path)
    
    # Clean up if exists
    if project_path_obj.exists():
        shutil.rmtree(project_path_obj)
    project_path_obj.mkdir(parents=True)
    
    print(f"Testing user's exact code in: {project_path}")
    
    # User's exact code
    a3 = A3(project_path=project_path)
    
    # Configure A3 settings
    a3.set_api_key("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")
    a3.set_model("qwen/qwen3-coder:free")
    a3.set_generate_tests(True)                
    a3.set_code_style("black")                 
    
    plan = a3.plan("A web scraper for news articles with sentiment analysis")
    specs = a3.generate_specs(project_path=project_path)
    
    # Check the state before implement
    progress = a3._state_manager.get_current_progress()
    print(f"Progress before implement: {progress}")
    if progress:
        print(f"Current phase: {progress.current_phase}")
        print(f"Current phase value: {a3._get_phase_value(progress.current_phase)}")
    
    implementation = a3.implement(project_path=project_path)
    integration = a3.integrate(project_path=project_path)
    
    print("Project created successfully!")

if __name__ == "__main__":
    test_user_exact_code()