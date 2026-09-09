from collections.abc import Mapping, Sequence

import pandas as pd


def process_streams(response: Mapping[str, object], id_activity: int) -> pd.DataFrame:
    """Process stream data into a DataFrame."""
    data = {
        stream_type: _extract_stream_values(stream_data)
        for stream_type, stream_data in response.items()
    }
    max_length = max((len(values) for values in data.values()), default=0)

    for values in data.values():
        values.extend([None] * (max_length - len(values)))

    df = pd.DataFrame(data)
    df["id"] = id_activity
    return df


def _extract_stream_values(stream_data: object) -> list[object]:
    if not isinstance(stream_data, Mapping):
        return []
    values = stream_data.get("data")
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return []
    return list(values)
