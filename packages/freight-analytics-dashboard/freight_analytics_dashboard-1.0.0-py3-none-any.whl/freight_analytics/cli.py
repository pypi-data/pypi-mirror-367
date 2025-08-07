"""Command-line interface for the Freight Analytics Dashboard."""

import argparse
import sys
import os
import subprocess
from pathlib import Path

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="US Freight Analytics Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  freight-dashboard                    # Launch dashboard on default port
  freight-dashboard --port 8502        # Launch on custom port
  freight-dashboard --host 0.0.0.0    # Launch accessible from network
  freight-dashboard --demo             # Launch with demo data
        """
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8501,
        help="Port to run the dashboard on (default: 8501)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="localhost", 
        help="Host to bind to (default: localhost)"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with demo data"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"freight-analytics-dashboard {get_version()}"
    )
    
    args = parser.parse_args()
    
    # Get the package directory
    package_dir = Path(__file__).parent
    app_file = package_dir / "app.py"
    
    # Build streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(app_file),
        "--server.port", str(args.port),
        "--server.address", args.host,
        "--server.headless", "true"
    ]
    
    if args.demo:
        os.environ["FREIGHT_DEMO_MODE"] = "1"
    
    print("🚛 Starting Freight Analytics Dashboard...")
    print(f"📍 URL: http://{args.host}:{args.port}")
    print("📊 Loading data...")
    print("📈 Dashboard will open in your browser automatically")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running dashboard: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install with: pip install streamlit")
        sys.exit(1)

def get_version():
    """Get package version."""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "1.0.0"

if __name__ == "__main__":
    main()
