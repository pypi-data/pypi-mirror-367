from __future__ import annotations
import json

from typing import TYPE_CHECKING, Generic, TypeVar

from pysimplesat.utils.helpers import parse_link_headers, parse_response_body

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pydantic import BaseModel
    from requests import Response

    from pysimplesat.types import RequestParams


TModel = TypeVar("TModel", bound="BaseModel")

if TYPE_CHECKING:
    from pysimplesat.interfaces import IPaginateable


class PaginatedResponse(Generic[TModel]):
    """
    PaginatedResponse is a wrapper class for handling paginated responses from the
    SimpleSat API. It provides methods for navigating through the pages of the response
    and accessing the data contained within each page.

    The class is designed to work with SimpleSatEndpoint and its derived classes to
    parse the API response into model instances. It also supports iteration, allowing
    the user to loop through the items within the paginated response.

    PaginatedResponse uses a generic type variable TModel, which represents the
    expected model type for the response data. This allows for type-safe handling
    of model instances throughout the class.
    """

    def __init__(
        self,
        response: Response,
        response_model: type[TModel],
        endpointmodel: IPaginateable,
        endpoint: str,
        page: int,
        limit: int,
        params: RequestParams | None = None,
    ) -> None:
        """
        PaginatedResponse is a wrapper class for handling paginated responses from the
        SimpleSat API. It provides methods for navigating through the pages of the response
        and accessing the data contained within each page.

        The class is designed to work with SimpleSatEndpoint and its derived classes to
        parse the API response into model instances. It also supports iteration, allowing
        the user to loop through the items within the paginated response.

        PaginatedResponse uses a generic type variable TModel, which represents the
        expected model type for the response data. This allows for type-safe handling
        of model instances throughout the class.
        """
        self._initialize(response, response_model, endpointmodel, endpoint, page, limit, params)

    def _initialize(
        self,
        response: Response,
        response_model: type[TModel],
        endpointmodel: IPaginateable,
        endpoint: str,
        page: int,
        limit: int,
        params: RequestParams | None = None,
    ):
        """
        Initialize the instance variables using the provided response, endpointmodel, and page size.

        Args:
            response: The raw response object from the API.
            endpointmodel (SimpleSatEndpoint[TModel]): The endpointmodel associated with the response.
            endpoint: The endpoint url to extract the data
            limit (int): The number of items per page.
        """
        self.response = response
        self.response_model = response_model
        self.endpointmodel = endpointmodel
        self.endpoint = endpoint
        self.limit = limit
        # Get page data from the response body
        try:
            self.parsed_pagination_response = parse_response_body(json.loads(response.content.decode('utf-8')))
            if self.parsed_pagination_response is not None:
                # SimpleSat API gives us a handy response to parse for Pagination
                self.has_next_page: bool = self.parsed_pagination_response.get("has_next_page", False)
                self.has_prev_page: bool = self.parsed_pagination_response.get("has_prev_page", False)
                self.prev_page: int = self.parsed_pagination_response.get("prev_page", None)
                self.next_page: int = self.parsed_pagination_response.get("next_page", None)
            else:
                # Haven't worked on this yet
                self.has_next_page: bool = True
                self.has_prev_page: bool = page > 1
                self.prev_page = page - 1 if page > 1 else 1
                self.next_page = page + 1
        except:
            pass
        self.params = params
        self.data: list[TModel] = [response_model.model_validate(d) for d in response.json().get(endpoint, {})]
        self.has_data = self.data and len(self.data) > 0
        self.index = 0

    def get_next_page(self) -> PaginatedResponse[TModel]:
        """
        Fetch the next page of the paginated response.

        Returns:
            PaginatedResponse[TModel]: The updated PaginatedResponse instance
            with the data from the next page or None if there is no next page.
        """
        if not self.has_next_page or not self.next_page:
            self.has_data = False
            return self

        next_response = self.endpointmodel.paginated(self.next_page, self.limit, self.params)
        self._initialize(
            next_response.response,
            next_response.response_model,
            next_response.endpointmodel,
            next_response.endpoint,
            self.next_page,
            next_response.limit,
            self.params,
        )
        return self

    def get_previous_page(self) -> PaginatedResponse[TModel]:
        """
        Fetch the next page of the paginated response.

        Returns:
            PaginatedResponse[TModel]: The updated PaginatedResponse instance
            with the data from the next page or None if there is no next page.
        """
        if not self.has_prev_page or not self.prev_page:
            self.has_data = False
            return self

        prev_response = self.endpointmodel.paginated(self.prev_page, self.limit, self.params)
        self._initialize(
            prev_response.response,
            prev_response.response_model,
            prev_response.endpointmodel,
            self.prev_page,
            prev_response.limit,
            self.params,
        )
        return self

    def all(self) -> Iterable[TModel]:
        """
        Iterate through all items in the paginated response, across all pages.

        Yields:
            TModel: An instance of the model class for each item in the paginated response.
        """
        while self.has_data:
            yield from self.data
            self.get_next_page()

    def __iter__(self):
        """
        Implement the iterator protocol for the PaginatedResponse class.

        Returns:
            PaginatedResponse[TModel]: The current instance of the PaginatedResponse.
        """
        return self

    def __dict__(self):
        """
        Implement the iterator protocol for the PaginatedResponse class.

        Returns:
            PaginatedResponse[TModel]: The current instance of the PaginatedResponse.
        """
        return self.data

    def __next__(self):
        """
        Implement the iterator protocol by getting the next item in the data.

        Returns:
            TModel: The next item in the data.

        Raises:
            StopIteration: If there are no more items in the data.
        """
        if self.index < len(self.data):
            result = self.data[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration
