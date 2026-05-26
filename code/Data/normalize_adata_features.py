
import scanpy as sc
import pandas as pd
import argparse
from scipy.sparse import issparse
import numpy as np

def get_n_genes(adata):
    if "Genes detected" not in adata.obs.columns.tolist():
            if issparse(adata.X):
                if adata.X.getformat() != "csr":
                    return np.diff(adata.X.tocsr().indptr)
                else:
                    return np.diff(adata.X.indptr)
            else:
                return np.sum(arr > 0, axis=1)
    else:
        return adata.obs["Genes detected"]

def main() -> None: 
    parser = argparse.ArgumentParser(
            description="Run differential expression analysis by cell type using nebula."
        )
    
    parser.add_argument(
        "--adata_path", type=str, required=True,
        help="Filename of the dataset to load from /data/adata/"
    )

    parser.add_argument(
        "--output_path", type=str, required=True,
        help="Filename to save the normalized dataset to in /data/adata/"
    )

    args = parser.parse_args()
    adata = sc.read_h5ad(args.adata_path)
    metadata = adata.obs.copy()

    # Normalize covariates
    metadata["Sex"] = metadata["Sex"].astype("category")
    metadata["Sex"] = metadata["Sex"].cat.reorder_categories(["Male", "Female"])
    metadata["Sex_codes"] = metadata["Sex"].cat.codes
    metadata["Sex_codes"] = metadata["Sex_codes"] / metadata["Sex_codes"].max()


    metadata["Age_at_Death_binned"] = pd.cut(metadata["Age at Death"], bins=5)
    metadata["Age_at_Death_binned_codes"] = metadata["Age_at_Death_binned"].cat.codes
    metadata["Age_at_Death_binned_codes"] = (
        metadata["Age_at_Death_binned_codes"]
        / metadata["Age_at_Death_binned_codes"].max()
    )
    del metadata["Age_at_Death_binned"]

    metadata["APOE4_Status"] = metadata["APOE Genotype"].str.contains("4")
    metadata["APOE4_Status"] = metadata["APOE4_Status"].astype("category")
    metadata["APOE4_Status"] = metadata["APOE4_Status"].cat.reorder_categories(
        [False, True]
    )
    metadata["APOE4_Status"] = metadata["APOE4_Status"].cat.rename_categories(
        {
            False: "N",
            True: "Y",
        }
    )
    metadata["APOE4_Status_codes"] = metadata["APOE4_Status"].cat.codes
    metadata["APOE4_Status_codes"] = (
        metadata["APOE4_Status_codes"] / metadata["APOE4_Status_codes"].max()
    )
    metadata["path_level"] = metadata["Donor ID"].apply(lambda x: 1 if x in ['H20.33.026', 'H21.33.002', 'H20.33.017', 'H20.33.031'] else 0)
    adata.obs = metadata
    
    adata.obs['Genes detected'] = get_n_genes(adata)

    adata.write_h5ad(args.output_path)

if __name__ == "__main__":
    main()