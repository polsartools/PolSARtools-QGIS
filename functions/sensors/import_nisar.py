import sys,os
import polsartools as pst  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from functions.utils.utils import progress_callback

# if __name__ == "__main__":
#     in_file = sys.argv[1]
    
#     print(f"(polsartools) $ Running NISAR with {in_file} ", flush=True)
#     pst.import_nisar_gcov(in_file, 
#               progress_callback=progress_callback
#               )


if __name__ == "__main__":
    # Standard mapping based on the list above
    in_file      = sys.argv[1]
    product_type = sys.argv[2]
    matrix_type  = sys.argv[3]
    azlks        = int(sys.argv[4])
    rglks        = int(sys.argv[5])
    reciprocity  = sys.argv[6] == 'true'
    out_format   = sys.argv[7]
    compression  = sys.argv[8] == 'true'
    
    print(f"(polsartools) $ Processing {product_type} product: {in_file}", flush=True)
    print(f"(polsartools) $ Matrix: {matrix_type}, Looks: {azlks}x{rglks}", flush=True)

    if product_type == "GCOV":
        # Call your library function with all parameters
        pst.import_nisar_gcov(
            in_file, 
            # product_type=product_type,
            mat=matrix_type,
            azlks=azlks,
            rglks=rglks,
            recip=reciprocity,
            fmt=out_format,
            comp=compression,
            progress_callback=progress_callback
        )
    elif product_type == "RSLC":
        pst.import_nisar_rslc(
            in_file, 
            mat=matrix_type,
            azlks=azlks,
            rglks=rglks,
            recip=reciprocity,
            fmt=out_format,
            comp=compression,
            progress_callback=progress_callback
        )
    elif product_type == "GSLC":
        pst.import_nisar_gslc(
            in_file, 
            mat=matrix_type,
            azlks=azlks,
            rglks=rglks,
            recip=reciprocity,
            fmt=out_format,
            comp=compression,
            progress_callback=progress_callback
        )
    else:
        print(f"(polsartools) $ Unknown product type: {product_type}", flush=True)