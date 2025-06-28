import sys
import polsartools as pst  

def progress_callback(p):
    print(f"[PROGRESS]{int(p * 100)}", flush=True)

if __name__ == "__main__":
    in_folder = sys.argv[1]
    ws_path = int(sys.argv[2])
    print(f"Running dopfp with {in_folder} and {ws_path}", flush=True)
    pst.dopfp(in_folder, ws_path, 
            #   progress_callback=progress_callback
              )
