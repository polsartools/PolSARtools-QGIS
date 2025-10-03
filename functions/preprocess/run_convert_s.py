import sys,os
import polsartools as pst  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from functions.utils.utils import progress_callback


if __name__ == "__main__":
    in_folder = sys.argv[1]
    ws_path = int(sys.argv[2])
    azlks = int(sys.argv[3])
    rglks = int(sys.argv[4])
    mat_index = int(sys.argv[5])

    mat_labels = ["C2", "T2", "C3", "T3", "C4", "T4", "C2HX", "C2VX", "C2HV"]

    mat_label = mat_labels[mat_index-1]
    
    if not in_folder or not os.path.isdir(in_folder):
        print("(polsartools) $ Please select a valid folder.", flush=True)
     #    sys.exit(1)
    else:      
        print(f"(polsartools) $ Running convert_s with folder: {in_folder}, "
                    f"azlks: {azlks}, rglks: {rglks}, mat: {mat_label}", flush=True)
        pst.convert_S(in_folder, mat_label, azlks, rglks, 
                    progress_callback=progress_callback
                    )