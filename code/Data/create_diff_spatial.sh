#!/bin/bash
# Create initial normalized features and distance to plaque anndata for differential spatial analysis
python code/Data/normalize_adata_features.py \
 --adata_path data/combined_adata/CaH_Xenium.2026-01-07.h5ad \
 --output_path scratch/normalized_features.h5ad

# Calculate distance to plaque and add as obs column to anndata
python code/Data/path_distance_anndata.py \
 --adata_path scratch/normalized_features.h5ad \
 --cell_path data/polygon_parquets_1/seaad_cah_cell_segmentation_polygons.2026-02-05.parquet \
 --landmark_path data/polygon_parquets_1/seaad_cah_plaque_polygons.2026-02-05.parquet \
 --distance_colname plaque_distance \
 --split_col barcode \
 --output_path results/seaad_cah_plaque_distance_adata.h5ad

# Calculate distance to Tau and add as obs column to anndata
python code/Data/path_distance_anndata.py \
 --adata_path scratch/normalized_features.h5ad \
 --cell_path data/polygon_parquets_1/seaad_cah_cell_segmentation_polygons.2026-02-05.parquet \
 --landmark_path data/polygon_parquets_1/seaad_cah_tau_polygons.2026-02-05.parquet \
 --distance_colname ptau_distance \
 --split_col barcode \
 --output_path results/seaad_cah_ptau_distance_adata.h5ad


# Calculate distance to microglia and add as obs column to anndata
python code/Data/path_distance_anndata.py \
    --adata_path scratch/normalized_features.h5ad \
    --cell_path data/polygon_parquets_1/seaad_cah_cell_segmentation_polygons.2026-02-05.parquet \
    --landmark_path data/polygon_parquets_1/seaad_cah_cell_segmentation_polygons.2026-02-05.parquet \
    --distance_colname microglia_distance \
    --split_col barcode \
    --output_path results/seaad_cah_microglia_distance_adata.h5ad \
    --subset_landmarks True \
    --subset_col Subclass \
    --subset_values "['Microglia-PVM_Subclass']"