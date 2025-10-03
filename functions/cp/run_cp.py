import sys, os
import polsartools as pst
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from functions.utils.utils import progress_callback

if __name__ == "__main__":
    # if len(sys.argv) < 6:
    #     print("Error: Expected arguments: in_folder, ws_path, tau, psi, chi, function_name", flush=True)
    #     sys.exit(1)

    in_folder = sys.argv[1]
    ws_path = int(sys.argv[2])
    tau = int(sys.argv[3])
    psi = float(sys.argv[4])
    chi = float(sys.argv[5])
    func_name = sys.argv[6]

    if not in_folder or not os.path.isdir(in_folder):
        print("Please select a valid folder.", flush=True)
        sys.exit(1)

    print(f"(polsartools) $ Running {func_name} with folder: {in_folder}, tau: {tau}, psi: {psi}, chi: {chi}, ws: {ws_path}", flush=True)

    try:
        func = getattr(pst, func_name)
        # Call with standard CP signature
        # func(in_folder, tau, psi, chi, ws_path, progress_callback=progress_callback)
        func(in_folder, tau, 0, ws_path, progress_callback=progress_callback)
    except AttributeError:
        print(f"Error: Function '{func_name}' not found in polsartools.", flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"Error while running {func_name}: {str(e)}", flush=True)
        sys.exit(1)
