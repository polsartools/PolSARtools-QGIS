import sys,os
import polsartools as pst  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from functions.utils.utils import progress_callback

if __name__ == "__main__":
    in_folder = sys.argv[1]
    ws_path = int(sys.argv[2])
    print(f"(polsartools) $ Running rlee with {in_folder} and {ws_path}", flush=True)
    pst.rlee(in_folder, ws_path, 
              progress_callback=progress_callback
              )
