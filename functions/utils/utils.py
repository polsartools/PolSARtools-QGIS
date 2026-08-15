# polsar_tools/utils/utils.py

def progress_callback(p):
    percentage = int(p * 100)
    # Print every 5% so stdout receives the text to parse
    if percentage == 100:
        print("progress: 100%", flush=True)
        print("Writing files...", flush=True)
    elif percentage % 1 == 0:
        print(f"progress: {percentage}%", flush=True)