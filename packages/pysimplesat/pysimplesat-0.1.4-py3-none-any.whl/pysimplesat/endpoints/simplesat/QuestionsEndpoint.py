from pysimplesat.endpoints.base.base_endpoint import SimpleSatEndpoint
from pysimplesat.interfaces import (
    IGettable,
    IPaginateable,
)
from pysimplesat.models.simplesat import Question
from pysimplesat.responses.paginated_response import PaginatedResponse
from pysimplesat.types import (
    JSON,
    SimpleSatRequestParams,
)


class QuestionsEndpoint(
    SimpleSatEndpoint,
    IGettable[Question, SimpleSatRequestParams],
    IPaginateable[Question, SimpleSatRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        SimpleSatEndpoint.__init__(self, client, "questions", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, Question)
        IPaginateable.__init__(self, Question)

    def paginated(
        self,
        page: int,
        limit: int,
        params: SimpleSatRequestParams | None = None,
    ) -> PaginatedResponse[Question]:
        """
        Performs a GET request against the /questions endpoint and returns an initialized PaginatedResponse object.

        Parameters:
            page (int): The page number to request.
            limit (int): The number of results to return per page.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PaginatedResponse[Question]: The initialized PaginatedResponse object.
        """
        if params:
            params["page[number]"] = page
            params["page[size]"] = limit
        else:
            params = {"page[number]": page, "page[size]": limit}
        return PaginatedResponse(
            super()._make_request("GET", params=params),
            Question,
            self,
            "questions",
            page,
            limit,
            params,
        )

    def get(
        self,
        data: JSON | None = None,
        params: SimpleSatRequestParams | None = None,
    ) -> Question:
        """
        Performs a GET request against the /questions endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            Question: The parsed response data.
        """
        print("get")
        return self._parse_many(
            Question,
            super()._make_request("GET", data=data, params=params).json().get('questions', {}),
        )
