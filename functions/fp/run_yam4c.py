import sys, os
import polsartools as pst
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from functions.utils.utils import progress_callback

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Missing required arguments. Expected: in_folder, ws_path, [model]", flush=True)
        sys.exit(1)

    in_folder = sys.argv[1]
    ws_path = int(sys.argv[2])
    model = sys.argv[3] if len(sys.argv) > 3 else ""

    if not in_folder or not os.path.isdir(in_folder):
        print("Please select a valid folder.", flush=True)
        sys.exit(1)

    print(f"(polsartools) $ Running yam4c_fp with folder: {in_folder}, ws: {ws_path}, model: {model}", flush=True)

    try:
        pst.yam4c_fp(
            in_dir=in_folder,
            model=model,
            win=ws_path,
            progress_callback=progress_callback
        )
    except Exception as e:
        print(f"Error while running yam4c_fp: {str(e)}", flush=True)
        sys.exit(1)
