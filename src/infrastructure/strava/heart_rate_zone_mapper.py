from collections.abc import Mapping, Sequence
from typing import cast

from src.domain.heart_rate_zones import HeartRateZone, HeartRateZones


def map_heart_rate_zones(activity_id: int, payload: object) -> HeartRateZones:
    """Translate an untrusted Strava zones response into the domain."""
    zone_payload = _heart_rate_zone_payload(payload)
    buckets = zone_payload.get("distribution_buckets")
    if buckets is None:
        raise ValueError("The activity does not have heartrate information.")
    if not isinstance(buckets, Sequence) or isinstance(buckets, (str, bytes)):
        raise TypeError("Strava zone buckets must be a sequence.")
    if len(buckets) != 5:
        raise ValueError("Strava must return exactly five heart-rate zones.")

    zones: list[HeartRateZone] = []
    for number, bucket in enumerate(cast(Sequence[object], buckets), start=1):
        if not isinstance(bucket, Mapping):
            raise TypeError("Each Strava zone bucket must be an object.")
        values = cast(Mapping[str, object], bucket)
        zones.append(
            HeartRateZone(
                number=number,
                minimum_bpm=_required_int(values, "min"),
                maximum_bpm=_required_int(values, "max"),
                time_seconds=_required_int(values, "time"),
            )
        )
    return HeartRateZones(activity_id=activity_id, zones=tuple(zones))


def _heart_rate_zone_payload(payload: object) -> Mapping[str, object]:
    if isinstance(payload, Mapping):
        return cast(Mapping[str, object], payload)
    if not isinstance(payload, Sequence) or isinstance(payload, (str, bytes)):
        raise TypeError("Strava zones response must be an object or a sequence.")

    candidates = [item for item in payload if isinstance(item, Mapping)]
    for candidate in candidates:
        if candidate.get("type") == "heartrate":
            return cast(Mapping[str, object], candidate)
    for candidate in candidates:
        if "distribution_buckets" in candidate:
            return cast(Mapping[str, object], candidate)
    raise ValueError("The activity does not have heartrate information.")


def _required_int(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"Heart-rate zone {key} must be an integer.")
    return value
