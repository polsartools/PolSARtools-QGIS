import sys,os
import polsartools as pst  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from functions.utils.utils import progress_callback

if __name__ == "__main__":
    in_folder = sys.argv[1]
    ws_path = int(sys.argv[2])
    azlks = int(sys.argv[3])
    rglks = int(sys.argv[4])

    print(f"(polsartools) $ Running mlook with folder: {in_folder}, azlks: {azlks}, rglks: {rglks}", flush=True)
    pst.mlook(in_folder,  azlks, rglks, 
              progress_callback=progress_callback
              )