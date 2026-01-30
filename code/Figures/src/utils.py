from h5py import File
from anndata.io import read_elem
from spatialdata import get_centroids

def crop_cell(sdata, element_key, element_cell_index, bounding_box_size = 250, coordinate_system = 'global'):
    centroids_df = get_centroids(sdata[element_key]).compute()
    centroid_x = int(centroids_df.loc[element_cell_index, 'x'])
    centroid_y = int(centroids_df.loc[element_cell_index, 'y'])
    min_coords = [centroid_x - bounding_box_size // 2, centroid_y - bounding_box_size // 2]
    max_coords = [centroid_x + bounding_box_size // 2, centroid_y + bounding_box_size // 2]
    sdata = sdata.query.bounding_box(min_coordinate=min_coords, max_coordinate=max_coords, axes=("x", "y"), target_coordinate_system="global")
    return sdata

def get_shape_transform(sdata, elem):
    shape_transform = get_transformation(sdata_sample[elem]).to_affine_matrix(input_axes = ("x", "y"), output_axes = ("x", "y"))
    return np.concat([shape_transform[:-1, :-1].flatten(), shape_transform[:-1, -1].flatten()])
    
def read_obs(path):
    with File(path) as f:
        return read_elem(f['obs'])


def latexify_xlabel(x):
    a = x.split("_")
    if len(a) > 1:
        a, b = a
        return f'${a}_{{{b}}}$'
    else:
        return f'${a[0]}$'