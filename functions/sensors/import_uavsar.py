# polsar_tools/functions/sensors/import_uavsar.py

import sys,os
import polsartools as pst  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from functions.utils.utils import progress_callback


if __name__ == "__main__":
    # Standard mapping based on the list above
    in_file      = sys.argv[1]
    product_type = sys.argv[2]
    matrix_type  = sys.argv[3]
    # azlks        = int(sys.argv[4])
    # rglks        = int(sys.argv[5])
    # reciprocity  = sys.argv[6] == 'true'
    out_format   = sys.argv[4]
    compression  = sys.argv[5] == 'true'
    
    print(f" Processing {product_type} product: {in_file}", flush=True)
    print(f" Matrix: {matrix_type}", flush=True)

    if product_type == "GRD":
        
        pst.import_uavsar_grd(
            in_file, 
            # product_type=product_type,
            mat=matrix_type,
            # azlks=azlks,
            # rglks=rglks,
            # recip=reciprocity,
            fmt=out_format,
            comp=compression,
            # progress_callback=progress_callback
        )
    elif product_type == "MLC":
        pst.import_uavsar_mlc(
            in_file, 
            mat=matrix_type,
            # azlks=azlks,
            # rglks=rglks,
            # recip=reciprocity,
            fmt=out_format,
            comp=compression,
            # progress_callback=progress_callback
        )

    else:
        print(f" Unknown product type: {product_type}", flush=True)