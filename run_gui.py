#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform

# Add the current directory to the path so modules can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the application class and main function
from App.SignalMgrApp import main

# Run the application
if __name__ == "__main__":
    # Print platform information for debugging
    print(f"Starting SignalMgrGUI on: {platform.system()} {platform.release()}")
    print(f"Python version: {platform.python_version()}")
    
    # Start the application
    main()
