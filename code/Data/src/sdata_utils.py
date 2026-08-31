import spatialdata as sd
import geopandas as gpd
from pathlib import Path

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