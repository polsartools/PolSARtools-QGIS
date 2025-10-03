import sys, os
import polsartools as pst
import importlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from functions.utils.utils import progress_callback

if __name__ == "__main__":
    # if len(sys.argv) < 4:
    #     print("Error: Missing required arguments. Expected: in_folder, ws_path, function_name", flush=True)
    #     sys.exit(1)

    in_folder = sys.argv[1]
    ws_path = int(sys.argv[2])
    func_name = sys.argv[3]

    print(f"(polsartools) $ Running {func_name} with folder: {in_folder}, ws: {ws_path}", flush=True)

    try:
        func = getattr(pst, func_name)
        func(in_folder, ws_path, progress_callback=progress_callback)
    except AttributeError:
        print(f"Error: Function '{func_name}' not found in polsartools.", flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"Error while running {func_name}: {str(e)}", flush=True)
        sys.exit(1)
