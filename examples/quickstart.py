"""Example script demonstrating minimal start-up sequence."""

import os

# Optional environment configuration
os.environ.setdefault("CRM_DEBUG", "1")

# Start the application
import main
main.main()
