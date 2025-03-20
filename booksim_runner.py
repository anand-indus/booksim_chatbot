import subprocess
import os

# Mapping user input to config files
CONFIG_MAP = {
    "8x8 mesh": "mesh88_lat",
    "8x8 torus": "torus88",
    "fat tree": "fattree_config"
}

def get_config_from_input(user_input):
    """Find the matching config based on user input."""
    user_input = user_input.lower()
    for key, config_file in CONFIG_MAP.items():
        if key in user_input:
            return config_file
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

