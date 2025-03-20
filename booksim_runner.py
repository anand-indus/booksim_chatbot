import subprocess
import os
import re
from thefuzz import fuzz

# Mapping user input to config files
CONFIG_MAP = {
    "8x8 mesh": "mesh88_lat",
    "8x8 torus": "torus88",
    "fat tree": "fattree_config",
    "cmesh": "cmeshconfig",
    "dragonfly": "dragonflyconfig",
    "flat fly": "flatflyconfig",
    "single": "singleconfig"
}

def clean_input(user_input):
    """Clean and preprocess the input for better matching."""
    # Convert to lowercase and remove special characters
    cleaned_input = re.sub(r'[^a-zA-Z0-9\s]', '', user_input.lower())
    return cleaned_input

def get_config_from_input(user_input):
    """Find the best matching config using fuzzy matching."""
    cleaned_input = clean_input(user_input)

    best_match = None
    highest_ratio = 0

    # Compare user input with all possible config options
    for key in CONFIG_MAP.keys():
        similarity_ratio = fuzz.partial_ratio(cleaned_input, key)
        
        if similarity_ratio > highest_ratio and similarity_ratio >= 70:  # Threshold at 70 for good match
            highest_ratio = similarity_ratio
            best_match = CONFIG_MAP[key]

    if best_match:
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
        
        config_file = get_config_from_input(user_input)
        
        if config_file:
            print(f"🔍 Matching config found: {config_file}")
            run_simulation(config_file)
        else:
            print("❌ No matching configuration found. Please try again!")
