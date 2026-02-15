"""
Data contract for CityBikes API response (Pandera model).
Acts as a "bouncer" for ingestion—only data passing this schema is valid.
"""
import pandera.polars as pa

class CityBikeSchema(pa.DataFrameModel):
    """Schema for station data: name, free_bikes, latitude, longitude."""

    name: str
    free_bikes: int = pa.Field(ge=0)
    latitude: float = pa.Field(in_range={"min_value": -90, "max_value": 90})
    longitude: float = pa.Field(in_range={"min_value": -180, "max_value": 180})
