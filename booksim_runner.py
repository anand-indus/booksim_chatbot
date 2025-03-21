import subprocess
import os
import re
import shutil
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

def modify_config(config_path):
    """Modify parameters dynamically in the config file."""
    temp_config_path = f"{config_path}_temp"  # Fix: Create a distinct temp file
    shutil.copy(config_path, temp_config_path)  # Copy original config to temp

    with open(temp_config_path, "r") as f:
        config_lines = f.readlines()

    print("\n⚙️ Here are the available parameters which you can modify.")
    print("If you don't want to change any parameter and want to simulate the example, type 'done' to move on to simulation.")
    print("Type 'exit' or 'quit' anytime to stop immediately.")

    param_map = {}
    for i, line in enumerate(config_lines):
        match = re.match(r"(\w+)\s*=\s*(.+)", line.strip())
        if match:
            param_name, param_value = match.groups()
            param_map[param_name] = i
            print(f"🔧 {param_name} = {param_value}")

    while True:
        param_to_modify = input("\nEnter parameter(s) to modify (e.g., 'k=4, n=3') or type 'done' to finish: ").strip()
        
        # Check if the user wants to exit
        if param_to_modify.lower() in ["exit", "quit"]:
            print("👋 Exiting simulation. Goodbye!")
            exit(0)

        if param_to_modify.lower() == "done":
            break
        
        # Split and process multiple parameter changes in one go
        param_changes = [param.strip() for param in param_to_modify.split(",")]
        
        for change in param_changes:
            match = re.match(r"(\w+)\s*=\s*([\d.]+)", change)
            if not match:
                match = re.match(r"(change|update|set)?\s*(\w+)\s*(to|is|=)\s*([\d.]+)", change)

            if match:
                param_name = match.group(2)  # Extracted parameter name
                new_value = match.group(4)   # Extracted new value
                
                if param_name in param_map:
                    line_index = param_map[param_name]
                    config_lines[line_index] = f"{param_name} = {new_value};\n"
                    print(f"✅ Updated: {param_name} = {new_value}")
                else:
                    print(f"❌ Parameter '{param_name}' not found in config.")
            else:
                print(f"❌ Couldn't understand '{change}'. Use format like 'k=4, n=3'")

    with open(temp_config_path, "w") as f:
        f.writelines(config_lines)

    print(f"✅ Modified config saved as: {temp_config_path}")
    return temp_config_path

def run_simulation(config_file):
    """Run BookSim simulation with the selected config."""
    config_path = f"/home/param/Desktop/noc_tools/booksim2/src/examples/{config_file}"
    temp_config_path = modify_config(config_path)  # Get modified config
    
    cmd_list = ["/home/param/Desktop/noc_tools/booksim2/src/booksim", temp_config_path]
    
    print(f"📄 Using modified config at: {temp_config_path}")
    print(f"🛠️ Running Command: {cmd_list}")
    
    try:
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/home/param/Desktop/noc_tools/booksim2/src/",
            env=os.environ
        )

        for line in process.stdout:
            print(line, end="")
        for line in process.stderr:
            print(f"⚠️ {line}", end="")

        process.wait()

        if process.returncode == 0:
            print("✅ Simulation Successful!")
        else:
            print(f"❌ Simulation Failed! Return Code: {process.returncode}")
    
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")
    
    os.remove(temp_config_path)  # Cleanup temp file
    print(f"🧹 Temporary config '{temp_config_path}' deleted after simulation.")


# Continuous loop until 'exit' or 'quit' is entered
if __name__ == "__main__":
    while True:
        user_input = input("\nEnter simulation details (or type 'exit' to quit): ").strip()
        
        # Check if user wants to quit from the main loop
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting simulation. Goodbye!")
            break
        
        best_match = get_best_match(user_input)
        
        if best_match:
            config_file = CONFIG_MAP[best_match]
            confirmation = input(
                f"🤔 I sense that you want to simulate a NoC {best_match.lower()} topology. "
                f"I have a default config file for the same. Do you want to continue with it? "
                f"You can customize the parameters according to your need in the next step. (yes/no): "
            ).strip().lower()

            if confirmation in ["yes", "y"]:
                print(f"🔍 Matching config confirmed: {best_match}")
                run_simulation(config_file)
            else:
                print("🔄 Please rephrase or provide more details.")
        else:
            print("❌ No matching configuration found. Please try again!")

