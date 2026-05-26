import anndata as ad
import pandas as pd
import numpy as np

adata = ad.read_h5ad("/root/capsule/data/adata/CaH_filtered_nuclei.2026-05-11.h5ad")

metadata = adata.obs.copy()

# Extract library sample prep label from each index.
metadata['library_prep'] = np.array([i.split("-")[1] for i in metadata.index])

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
del metadata['Age_at_Death_binned']
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

metadata["Cognitive_Status"] = metadata["Cognitive Status"].astype("category")
metadata["Cognitive_Status"] = metadata["Cognitive_Status"].cat.reorder_categories(
    ["No dementia", "Dementia"]
)
metadata["Cognitive_Status_codes"] = metadata["Cognitive_Status"].cat.codes
metadata["Cognitive_Status_codes"] = (
    metadata["Cognitive_Status_codes"] / metadata["Cognitive_Status_codes"].max()
)

metadata['Thal'] = metadata['Thal'].astype("category")
metadata['Thal'] = metadata['Thal'].cat.reorder_categories(['Thal 0', 'Thal 1', 'Thal 2', 'Thal 3', 'Thal 4', 'Thal 5'])
metadata['Thal_codes'] = metadata['Thal'].cat.codes 
metadata['Thal_codes'] = (
    metadata['Thal_codes'] / metadata['Thal_codes'].max()
)

braak_code_dict = {'Braak 0':0/6, 'Braak II': 2/6, 'Braak III':3/6, 'Braak IV':4/6, 'Braak V':5/6, 'Braak VI':6/6}
metadata['Braak_codes'] = metadata['Braak'].apply(braak_code_dict.get)

adnc_code_dict = {'Not AD':0/3, 'Low':1/3, 'Intermediate':2/3, 'High':3/3}
metadata['ADNC_codes'] = metadata['Overall AD neuropathological Change'].apply(adnc_code_dict.get)

adata.obs = metadata

adata.write_h5ad("/root/capsule/results/CaH_filtered_nuclei_preprocessed.2026-05-26.h5ad")