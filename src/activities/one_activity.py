from src.interfaces.activities import InterfaceActivitiesStrava


class GetOneActivity(InterfaceActivitiesStrava):
    def fetch_activity_data(self) -> dict:
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")
        return self.api.make_request(f"/activities/{self.id_activity}")
