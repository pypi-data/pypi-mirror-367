"""Convert shapefile data to SWIFT JSON catchment structure."""

import json
from typing import Any, Dict, List, Tuple  # noqa: UP035

import geopandas as gpd

_default_linkid_field = "LinkID"
_default_fromnodeid_field = "FromNodeID"
_default_tonodeid_field = "ToNodeID"
_default_spathlen_field = "SPathLen"
_default_darea2_field = "DArea2"
_default_geometry_field = "geometry"


class ShapefileToSwiftConverter:
    """Converts shapefile data to SWIFT JSON catchment structure."""

    def __init__(
        self,
        gdf: gpd.GeoDataFrame,
        include_coordinates: bool = False,  # noqa: FBT001, FBT002
        linkid_field: str = "LinkID",
        fromnodeid_field: str = "FromNodeID",
        tonodeid_field: str = "ToNodeID",
        spathlen_field: str = "SPathLen",
        darea2_field: str = "DArea2",
        geometry_field: str = "geometry",
    ):
        """Initialize converter with geopandas dataframe.

        Args:
            gdf: GeoDataFrame loaded from shapefile containing link data
            include_coordinates: Whether to include lat/lon in node definitions
        """
        self.gdf = gdf
        self.include_coordinates = include_coordinates
        self._linkid_field = linkid_field if linkid_field else _default_linkid_field
        self._fromnodeid_field = fromnodeid_field if fromnodeid_field else _default_fromnodeid_field
        self._tonodeid_field = tonodeid_field if tonodeid_field else _default_tonodeid_field
        self._spathlen_field = spathlen_field if spathlen_field else _default_spathlen_field
        self._darea2_field = darea2_field if darea2_field else _default_darea2_field
        self._geometry_field = geometry_field if geometry_field else _default_geometry_field
        self._check_geodf()

        self._runoff_model = {
            "PercFactor": 2.25,
            "R": 0.0,
            "RunoffModelType": "GR4J",
            "S": 0.0,
            "SurfaceRunoffRouting": {"SurfaceRunoffRoutingType": "NoRouting"},
            "UHExponent": 2.5,
            "x1": 350.0,
            "x2": 0.0,
            "x3": 40.0,
            "x4": 0.5,
        }
        self.routing_model = {"ChannelRoutingType": "NoRouting"}

    @property
    def gdf(self) -> gpd.GeoDataFrame:
        """The geodataframe from which we build the json file."""
        return self._gdf
    @gdf.setter
    def gdf(self, value: gpd.GeoDataFrame) -> None:
        self._gdf = value

    @property
    def include_coordinates(self) -> bool:
        """Should the Latitude/Longitude coordinates be derived from the geometry and written in the json file."""
        return self._include_coordinates
    @include_coordinates.setter
    def include_coordinates(self, value: bool) -> None:
        self._include_coordinates = value

    @property
    def runoff_model(self) -> dict:
        """Dictionary for the rainfall-runoff model sections of the json file."""
        return self._runoff_model
    @runoff_model.setter
    def runoff_model(self, value:dict) -> None:
        self._runoff_model = value

    @property
    def routing_model(self) -> dict:
        """Dictionary for the routing model sections of the json file."""
        return self._routing_model
    @routing_model.setter
    def routing_model(self, value:dict) -> None:
        self._routing_model = value

    def _check_geodf(self) -> None:
        """Check the GeoDataFrame for required columns and types."""
        required_columns_names = [
            self._linkid_field,
            self._fromnodeid_field,
            self._tonodeid_field,
            self._spathlen_field,
            self._darea2_field,
            self._geometry_field,
        ]

        if set(required_columns_names).intersection(set(self.gdf.columns)) != set(required_columns_names):
            raise ValueError(f"The GeoDataFrame does not contain all the required columns: {required_columns_names}")

        # IDs should be strings, even if legacy are ints.
        self.gdf[self._linkid_field] = self.gdf[self._linkid_field].astype(str)
        self.gdf[self._fromnodeid_field] = self.gdf[self._fromnodeid_field].astype(str)
        self.gdf[self._tonodeid_field] = self.gdf[self._tonodeid_field].astype(str)

        required_columns = {
            # self._linkid_field: "int64",
            # self._fromnodeid_field: "int64",
            # self._tonodeid_field: "int64",
            self._spathlen_field: "float64",
            self._darea2_field: "float64",
            # TODO test geometry column, but I could not figure out how.
            # self._geometry_field: gpd.array.GeometryDtype,
        }
        for column, expected_type in required_columns.items():
            if self.gdf[column].dtype != expected_type:
                raise TypeError(f"Column '{column}' must be of type {expected_type}.")

        # Check for duplicate LinkID values
        link_id_counts = self.gdf[self._linkid_field].value_counts()
        duplicates = link_id_counts[link_id_counts > 1]
        if not duplicates.empty:
            duplicate_indices = self.gdf[self.gdf[self._linkid_field].isin(duplicates.index)].index.tolist()
            raise ValueError(f"Column 'LinkID' contains duplicate values: {duplicates.index.tolist()} at indices {duplicate_indices}.")


    def convert(self) -> Dict[str, Any]:
        """Convert shapefile data to SWIFT JSON format.

        Returns:
            Dictionary containing Links, Nodes, and SubAreas sections
        """
        return {"Links": self._create_links(), "Nodes": self._create_nodes(), "SubAreas": self._create_subareas()}

    def save_to_file(self, filepath: str, indent: int = 2) -> None:
        """Save converted data to JSON file.

        Args:
            filepath: Path where to save the JSON file
            indent: Number of spaces for JSON indentation (default: 2)
        """
        with open(filepath, "w") as f:
            json.dump(self.convert(), f, indent=indent)

    def _create_links(self) -> List[Dict[str, Any]]:
        """Create links section of JSON from dataframe."""
        links = []
        for _, row in self.gdf.iterrows():
            link = {
                "ChannelRouting": self.routing_model,
                "DownstreamNodeID": str(row[self._tonodeid_field]),
                "ID": str(row[self._linkid_field]),
                "Length": float(row[self._spathlen_field]),
                "ManningsN": 1.0,
                "Name": str(row[self._linkid_field]),
                "Slope": 1.0,
                "UpstreamNodeID": str(row[self._fromnodeid_field]),
                "f": 1.0,
            }
            links.append(link)
        return links

    def _get_node_coordinates(self) -> Dict[int, Tuple[float, float]]:
        """Extract node coordinates from geometry data.

        Returns:
            Dictionary mapping node_id to (longitude, latitude) tuple
        """
        node_coords = {}
        for _, row in self.gdf.iterrows():
            geom = row[self._geometry_field]
            coords = list(geom.coords)

            # Start point for FromNodeID
            start_lon, start_lat = coords[0]
            node_coords[row[self._fromnodeid_field]] = (start_lon, start_lat)

            # End point for ToNodeID
            end_lon, end_lat = coords[-1]
            node_coords[row[self._tonodeid_field]] = (end_lon, end_lat)

        return node_coords

    def _create_nodes(self) -> List[Dict[str, Any]]:
        """Create nodes section of JSON from dataframe."""
        from_nodes = set(self.gdf[self._fromnodeid_field])
        to_nodes = set(self.gdf[self._tonodeid_field])
        unique_nodes = from_nodes.union(to_nodes)

        # Get coordinates if requested
        node_coords = self._get_node_coordinates() if self.include_coordinates else {}

        nodes = []
        for node_id in sorted(unique_nodes):
            node:Dict[str,Any] = {
                "ErrorCorrection": {"ErrorCorrectionType": "NoErrorCorrection"},
                "ID": str(node_id),
                "Name": f"Node_{node_id}",
                "Reservoir": {"ReservoirType": "NoReservoir"},
            }

            # Add coordinates if available
            if self.include_coordinates and node_id in node_coords:
                lon, lat = node_coords[node_id]
                node["Longitude"] = lon
                node["Latitude"] = lat

            nodes.append(node)
        return nodes

    def _create_subareas(self) -> List[Dict[str, Any]]:
        """Create subareas section of JSON from dataframe."""
        subareas = []
        for _, row in self.gdf.iterrows():
            if row[self._darea2_field] > 0:
                subarea = {
                    "AreaKm2": float(row[self._darea2_field]) / 1_000_000,
                    "ID": str(row[self._linkid_field]),
                    "LinkID": str(row[self._linkid_field]),
                    "Name": f"Subarea_{row['LinkID']}",
                    "RunoffModel": self.runoff_model,
                }
                subareas.append(subarea)
        return subareas
