#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# Run the SignalMgrApp from App directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from App.SignalMgrApp import main

if __name__ == "__main__":
    main() 