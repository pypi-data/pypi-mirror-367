import os 
import sys 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append((os.path.dirname(os.path.abspath(__file__))))

from src import server

def main():
    server.main()

# Optionally expose other important items at package level
__all__ = ["main", "server"]