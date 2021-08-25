from typing import Optional

from domain.model import MeshColumn


class ConnectionUpdatePolicyReplace:
    """ConnectionUpdatePolicyReplace implements ConnectionUpdatePolicy"""

    def update(self, cached_conn: Optional[MeshColumn], update_conn: MeshColumn) -> MeshColumn:
        """Update cache if update is newer or just as fresh but has more timeseries data"""

        # 1. no such connection in cache yet - replace with whatever comes
        if not cached_conn:
            return update_conn

        # 2. connection in cache but has no timeseries data - replace
        cached_latest = cached_conn.latest_measurement
        if not cached_latest:
            return update_conn

        # 3. connection in cache, has timeseries, but update brings no timeseries data - keep cache
        update_latest = update_conn.latest_measurement
        if not update_latest:
            return cached_conn

        # 4. cached connection is older than update connection
        if cached_latest.timestamp < update_latest.timestamp:
            return update_conn

        # 5. cached and update are equally fresh but update brings more data
        same_timestamp = cached_latest.timestamp == update_latest.timestamp
        more_timeseries_data = len(update_conn.health) > len(cached_conn.health)
        if same_timestamp and more_timeseries_data:
            return update_conn

        return cached_conn
