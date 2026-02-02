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


def generate_grid(max_x, max_y, bin_size, min_x=0, min_y=0, crs=None):
    """
    Generate a regular grid of rectangular boxes.

    Parameters
    ----------
    max_x, max_y : float
        Maximum X and Y extent of the grid.
    min_x, min_y : float, optional
        Minimum coordinates (default 0,0).
    bin_size : float
        Size of each grid cell in coordinate units.
    crs : any, optional
        Coordinate reference system to assign to the resulting GeoDataFrame.

    Returns
    -------
    grid_gdf : GeoDataFrame
        Grid of rectangular boxes (each cell is a polygon).
    """
    
    # Create the coordinate ranges
    xs = np.arange(min_x, max_x, bin_size)
    ys = np.arange(min_y, max_y, bin_size)

    # Build the boxes
    boxes = []
    for x0 in xs:
        for y0 in ys:
            x1 = x0 + bin_size
            y1 = y0 + bin_size
            boxes.append(box(x0, y0, x1, y1))

    # Wrap in GeoDataFrame
    grid = gpd.GeoDataFrame({"geometry": boxes}, crs=crs)
    
    return grid


def compute_polygon_overlap(polygons_gs, boxes_gdf):
    """
    Robustly compute the overlap area between grid boxes and polygons,
    automatically fixing invalid geometries to avoid TopologyException.
    """

    # Convert to GDF
    polygons = gpd.GeoDataFrame(geometry=polygons_gs, crs=boxes_gdf.crs).copy()
    boxes = boxes_gdf.copy()

    # 1. Fix invalid geometries (buffer(0) is the classic fix)
    polygons["geometry"] = polygons.geometry.buffer(0)
    boxes["geometry"]    = boxes.geometry.buffer(0)

    # 2. Use spatial index to find intersecting pairs
    sindex = polygons.sindex

    intersections = []
    box_idx_list = []

    for box_idx, box in boxes.geometry.items():
        # candidate polygons that might intersect the box
        cand_idx = list(sindex.query(box, predicate="intersects"))

        if not cand_idx:
            intersections.append(0.0)
            continue

        # intersect only valid candidates
        polys = polygons.geometry.iloc[cand_idx]
        inter = polys.intersection(box)

        # compute total intersection area for this box
        area = inter.area.sum()
        intersections.append(area)

    # 3. Add result column
    boxes["overlap_area"] = intersections
    return boxes


