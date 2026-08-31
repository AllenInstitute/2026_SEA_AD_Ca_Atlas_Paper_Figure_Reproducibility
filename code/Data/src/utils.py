import pandas as pd
import scanpy as sc
import rapids_singlecell as rsc
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats as sp_stats
import seaborn as sns
from pathlib import Path
import geopandas as gpd
from h5py import File
from anndata.io import read_elem

class NotASubsetError(ValueError):
    """Raised when the first iterable is not a subset of the second."""
    def __init__(self, missing_elements, *args):
        self.missing_elements = missing_elements

        missing_list = sorted(missing_elements)
        max_display = 10
        display_items = missing_list[:max_display]

        pretty = "\n".join(f"- {repr(e)}" for e in display_items)

        if len(missing_list) > max_display:
            remaining = len(missing_list) - max_display
            pretty += f"\n...and {remaining} more missing elements."

        msg = f"The following elements are missing from the second iterable:\n{pretty}"
        super().__init__(msg, *args)


def assert_subset(small, big):
    """
    Assert that `small` is a subset of `big`.
    
    Raises NotASubsetError listing up to 10 missing elements if not.
    """
    set_small = set(small)
    set_big = set(big)
    missing = set_small - set_big
    if missing:
        raise NotASubsetError(missing)


def read_obs(path):
    with File(path) as f:
        return read_elem(f['obs'])
        
def read_latent_adata(path:Path, additional_obs:pd.DataFrame | None = None):
    latent_X = np.load(path / "X_scVI.npy")
    obs_probs = pd.read_csv(path / "probabilities.csv", index_col = 0)

    if additional_obs:
        assert_subset(obs_probs.index.tolist(), addtional_obs.index.tolist())
        obs_probs = obs_probs.merge(additional_obs, left_index = True, right_index = True, how = "left")
    
    return sc.AnnData(X = latent_X, obs = obs_probs)

def prep_umap(adata, leiden_resolution = 1):
    rsc.get.anndata_to_GPU(adata)
    rsc.pp.neighbors(adata)
    rsc.tl.leiden(adata, leiden_resolution)
    rsc.tl.umap(adata)
    rsc.get.anndata_to_CPU(adata)

def calculate_batch_entropy(adata, batch_key = "_scvi_batch", nn_key = 'connectivities'):
    '''
    cluster_key can be set as connectivities or distances
    where connectivities is based on simplicial set
    and distance is the top-k
    '''
    x, y = np.nonzero(adata.obsp[nn_key]) # Get the indices of the non-zero elements from knn matrix
    batch_ids = adata.obs[batch_key].factorize()[0] # Change batch ids to ordered integers
    n_cats = len(np.unique(batch_ids)) # Get the number of unique batch ids
    batch_id_array = batch_ids[y] # Convert neighbor indices to batch ids
    batch_id_split = np.split(batch_id_array, np.unique(x, return_index=True)[1][1:]) # Split the batch ids by cell (noticed that there were unequal number of neighbors for each cell)
    batch_prob_array = np.vstack([np.bincount(batch_id, minlength = n_cats) / len(batch_id) for batch_id in batch_id_split]) # Calculate the probability of each batch for each cell
    return sp_stats.entropy(batch_prob_array.T)

# def plot_histograms(
def check_level(path, level):
    df = pd.read_csv(path / "probabilities.csv", index_col = 0)
    label_name = df.columns[0].split("_")[0]
    return label_name == level

# Do not move to functions box 
def plot_umaps_and_histograms(latent_adata,label_name, leiden_resolution = 1, hist_bins = 100, qc_metrics = ["Genes detected", "Fraction mitochondrial UMIs",  "Doublet score"]):
    sns.barplot(latent_adata.obs[f"{label_name}_scANVI"].value_counts(), orient = "h")
    prep_umap(latent_adata, leiden_resolution)
    latent_adata.obs["dataset"] = latent_adata.obs[f"{label_name}_stash"].apply(lambda x: "CN-MTG Reference" if x!="Unknown" else "SEA-AD Caudate Nucleus")
    batch_entropy = calculate_batch_entropy(latent_adata, batch_key = "dataset")
    latent_adata.obs["dataset_mixing"] = batch_entropy
    sc.pl.umap(latent_adata, color = ["dataset", "dataset_mixing", f"{label_name}_scANVI", f"{label_name}_conf_scANVI", "leiden", "Doublet score", "Genes detected","Fraction mitochondrial UMIs"], ncols = 2, frameon = False)
    for metric in qc_metrics:
        qc_series = latent_adata.obs.groupby("leiden")[metric].mean()
        sns.displot(qc_series, bins = hist_bins)

def sdata_read_polygons(
    zarr_dir:Path | str,
    element: str,
    ):
    """
    Read in polygon parquet file from spatialdata directory
    """
    zarr_dir = zarr_dir if isinstance(zarr_dir, Path) else Path(zarr_dir)
    polygon_path = zarr_dir / "shapes" / element / "shapes.parquet"
    return gpd.read_parquet(polygon_path) 