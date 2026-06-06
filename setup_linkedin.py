from dotenv import load_dotenv
load_dotenv()

from linkedin.oauth import run_oauth_flow

if __name__ == "__main__":
    print("=== LinkedIn OAuth Setup ===")
    print("This runs once to connect your LinkedIn account.\n")
    run_oauth_flow()
    print("\nSetup complete! You can now run: python main.py")
