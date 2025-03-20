import subprocess
import os
import re
from thefuzz import process

# Mapping user input to config files
CONFIG_MAP = {
    "8x8 mesh": "mesh88_lat",
    "8x8 torus": "torus88",
    "fat tree": "fattree_config",
    "cmesh": "cmeshconfig",
    "dragonfly": "dragonflyconfig",
    "flatfly": "flatflyconfig",
    "single": "singleconfig"
}

def extract_relevant_keywords(user_input):
    """Extract relevant keywords for better matching."""
    # Define possible keywords
    keywords = [
        "mesh", "torus", "fat tree", "cmesh", "dragonfly",
        "flatfly", "single", "8x8"
    ]
    
    # Extract keywords that exist in the user's input
    found_keywords = [word for word in keywords if word in user_input.lower()]
    
    # Return a clean, joined string of relevant keywords
    return " ".join(found_keywords)

def get_best_match(user_input):
    """Find the best matching config based on fuzzy logic."""
    cleaned_input = extract_relevant_keywords(user_input)
    
    if not cleaned_input:
        return None  # No relevant keywords found, avoid bad matches
    
    best_match, score = process.extractOne(cleaned_input, CONFIG_MAP.keys())
    
    if score >= 70:  # Accept match only if confidence is 70% or higher
        return best_match
    return None

def run_simulation(config_file):
    """Run BookSim simulation with the selected config."""
    config_path = f"/home/param/Desktop/noc_tools/booksim2/src/examples/{config_file}"
    cmd_list = ["/home/param/Desktop/noc_tools/booksim2/src/booksim", config_path]
    
    print(f"📄 Checking config file at: {config_path}")
    print(f"🛠️ Running Command with List: {cmd_list}")
    
    # Double-check if the config file exists
    if not os.path.exists(config_path):
        print(f"❌ Error: Config file not found at {config_path}")
        return

    try:
        # Run the process and print output in real-time
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/home/param/Desktop/noc_tools/booksim2/src/",
            env=os.environ
        )

        # Show the output directly in the terminal
        for line in process.stdout:
            print(line, end="")

        # Show errors if any
        for line in process.stderr:
            print(f"⚠️ {line}", end="")

        # Wait for the process to complete
        process.wait()

        # Check return code
        if process.returncode == 0:
            print("✅ Simulation Successful!")
        else:
            print(f"❌ Simulation Failed! Return Code: {process.returncode}")
    
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")

# Continuous loop until 'exit' or 'quit' is entered
if __name__ == "__main__":
    while True:
        user_input = input("\nEnter simulation details (or type 'exit' to quit): ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting simulation. Goodbye!")
            break
        
        best_match = get_best_match(user_input)
        
        if best_match:
            config_file = CONFIG_MAP[best_match]
            confirmation = input(f"🤔 Did you mean '{best_match}'? (yes/no): ").strip().lower()

            if confirmation in ["yes", "y"]:
                print(f"🔍 Matching config confirmed: {best_match}")
                run_simulation(config_file)
            else:
                print("🔄 Please rephrase or provide more details.")
        else:
            print("❌ No matching configuration found. Please try again!")
