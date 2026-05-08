import sys,os
import polsartools as pst  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from functions.utils.utils import progress_callback

if __name__ == "__main__":
    in_file = sys.argv[1]
    
    print(f"(polsartools) $ Running NISAR with {in_file} ", flush=True)
    pst.import_nisar_gcov(in_file, 
              progress_callback=progress_callback
              )
