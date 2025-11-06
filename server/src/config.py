import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Load secrets from environment variables
JWT_SECRET = os.getenv("JWT_SECRET")
SOLVER_API_KEY = os.getenv("SOLVER_API_KEY")
VISUALIZER_API_KEY = os.getenv("VISUALIZER_API_KEY")

# Validate that all required secrets are set
if not JWT_SECRET:
    raise ValueError("JWT_SECRET is not set in environment variables")
if not SOLVER_API_KEY:
    raise ValueError("SOLVER_API_KEY is not set in environment variables")
if not VISUALIZER_API_KEY:
    raise ValueError("VISUALIZER_API_KEY is not set in environment variables")

# Load other configurations
ALGORITHM = os.getenv("ALGORITHM", "HS256")
PORT = os.getenv("PORT", "8080")
