import pandas as pd
from datetime import datetime
import scanpy as sc
import geopandas as gpd
import argparse
from pathlib import Path
import numpy as np

def main() -> None:
    parser = argparse.ArgumentParser("Generate anndata object with distance to landmark features.")
    parser.add_argument("--adata_path", type=str, required=True, help="Path to the input anndata file.")
    parser.add_argument("--cell_path", type=str, required=True, help="Path to the cell parquet file.")
    parser.add_argument("--landmark_path", type=str, required=True, help="Path to the landmark parquet file.")
    parser.add_argument("--split_col", type=str, required=True, help="Column in the anndata obs to split by (e.g. 'sample_id').")
    parser.add_argument("--distance_colname", type=str, required=True, help="Name of the new column to store the distance to the nearest landmark.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to the output anndata file.")
    parser.add_argument("--subset_landmarks", default = False, type = bool, help="Whether to subset landmarks based on the anndata obs.")
    parser.add_argument("--subset_col", type=str, default="sample_id", help="Column to use for subsetting landmarks.")
    parser.add_argument("--subset_values", type=str, default="[]", help="Values to keep in the subset.")
    args = parser.parse_args()

    datetime_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(f"{args.output_path.rstrip('.h5ad')}_{datetime_str}.h5ad")
    if output_dir.exists():
        print("Output file already exists. Skipping processing.")
        return None
    adata = sc.read_h5ad(args.adata_path)
    landmarks = gpd.read_parquet(args.landmark_path)
    if args.subset_landmarks:
        args.subset_values = eval(args.subset_values)
        print(args.subset_values)
        landmarks = landmarks[landmarks[args.subset_col].isin(args.subset_values)]
    
    cells = gpd.read_parquet(args.cell_path)

    barcodes = landmarks[args.split_col].unique().tolist()
    distance_gpds = []
    for barcode in barcodes:
        print(f"Processing barcode: {barcode}")
        reference_polygons = landmarks[landmarks[args.split_col] == barcode]
        query_polygons = cells[cells[args.split_col] == barcode]
        idx, distance = reference_polygons.geometry.sindex.nearest(
            query_polygons.geometry,
            return_all=False,
            return_distance=True
            )
        query_polygons[args.distance_colname] = distance
        distance_gpds.append(query_polygons)
    
    distance_gpd = pd.concat(distance_gpds)
    distance_adata = adata[distance_gpd.index.tolist(), :].copy()
    distance_adata.obs[args.distance_colname] = distance_gpd[args.distance_colname]
    distance_adata.obs[f'{args.distance_colname}_norm'] = np.exp(-(distance_adata.obs[args.distance_colname]/distance_adata.obs[args.distance_colname].mean()))
    distance_adata.write_h5ad(f"{args.output_path.rstrip('.h5ad')}_{datetime_str}.h5ad")


if __name__ == "__main__":
    main()
