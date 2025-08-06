from a3.core.models import ProjectPhase
from datetime import datetime
from pathlib import Path
import json
import os
import sys

from a3 import A3
import shutil
import tempfile

#!/usr/bin/env python3
"""
Test script to simulate corrupted state scenario.
"""


# Add the current directory to Python path
sys.path.insert(0, '.')


def create_corrupted_state(project_path):
    """Create a corrupted state where plan exists but progress is wrong."""
    
    a3_dir = Path(project_path) / ".A3"
    a3_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a plan file
    plan_data = {
        "objective": "A web scraper for news articles with sentiment analysis",
        "modules": [
            {
                "name": "main",
                "file_path": "src/main.py",
                "functions": [
                    {
                        "name": "main",
                        "description": "Main entry point",
                        "arguments": [],
                        "return_type": "None"
                    }
                ]
            }
        ]
    }
    
    with open(a3_dir / "project_plan.json", "w") as f:
        json.dump(plan_data, f)
    
    # Create corrupted progress - still in PLANNING phase but with plan
    progress_data = {
        "current_phase": "planning",  # This is the issue - should be SPECIFICATION after generate_specs
        "completed_phases": [],
        "total_functions": 1,
        "implemented_functions": 0,
        "failed_functions": [],
        "completed_functions": [],
        "last_updated": datetime.now().isoformat()
    }
    
    with open(a3_dir / "progress.json", "w") as f:
        json.dump(progress_data, f)

def test_corrupted_state_scenario():
    """Test the corrupted state scenario."""
    
    project_path = r"C:\Users\milin\Documents\A3 Testing Corrupted"
    project_path_obj = Path(project_path)
    
    # Clean up if exists
    if project_path_obj.exists():
        shutil.rmtree(project_path_obj)
    project_path_obj.mkdir(parents=True)
    
    # Create corrupted state
    create_corrupted_state(project_path)
    
    print(f"Testing corrupted state scenario in: {project_path}")
    
    # Initialize A3 with existing corrupted state
    a3 = A3(project_path=project_path)
    a3.set_api_key("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")
    a3.set_model("qwen/qwen3-coder:free")
    a3.set_generate_tests(True)
    a3.set_code_style("black")
    
    # Check initial state
    progress = a3._state_manager.get_current_progress()
    print(f"Initial progress: {progress}")
    if progress:
        print(f"Initial phase: {progress.current_phase}")
    
    print("Running generate_specs()...")
    try:
        specs = a3.generate_specs(project_path=project_path)
        print(f"Specs generated with {len(specs.functions)} functions")
        
        # Check progress after generate_specs
        progress = a3._state_manager.get_current_progress()
        if progress:
            print(f"Phase after generate_specs: {progress.current_phase}")
        
    except Exception as e:
        print(f"Generate specs failed: {e}")
        return
    
    print("Running implement()...")
    try:
        implementation = a3.implement(project_path=project_path)
        print("Implementation successful!")
        
    except Exception as e:
        print(f"Implementation failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return

if __name__ == "__main__":
    test_corrupted_state_scenario()