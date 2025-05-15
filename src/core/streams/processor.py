from typing import Dict

import pandas as pd


def process_streams(response: Dict, id_activity: int) -> pd.DataFrame:
    """Process stream data into a DataFrame."""
    max_length = (
        max(
            len(stream_data.get("data", []))
            for stream_data in response.values()
            if isinstance(stream_data, dict)
        )
        if response
        else 0
    )

    data = {}
    for stream_type, stream_data in response.items():
        if isinstance(stream_data, dict) and "data" in stream_data:
            data[stream_type] = stream_data["data"]

            if len(data[stream_type]) < max_length:
                data[stream_type].extend([None] * (max_length - len(data[stream_type])))
        else:
            data[stream_type] = [None] * max_length

    df = pd.DataFrame(data)
    df["id"] = id_activity
    return df
