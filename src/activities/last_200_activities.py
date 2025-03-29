from src.interfaces.activities import InterfaceActivitiesStrava


class GetLast200Activities(InterfaceActivitiesStrava):
    def fetch_activity_data(self) -> dict:
        params = {"per_page": 200, "page": 1}
        return self.api.make_request(endpoint="/activities", params=params)
