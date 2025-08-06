from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPostable,
    IDeleteable
)
from pyironscales.models.ironscales import Company911Email
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyId911EmailEndpoint(
    IronscalesEndpoint,
    IGettable[Company911Email, IronscalesRequestParams],
    IPostable[Company911Email, IronscalesRequestParams],
    IDeleteable[IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "911-email/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, Company911Email)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> Company911Email:
        """
        Performs a GET request against the /company/{id}/911-email/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            Company911Email: The parsed response data.
        """
        return self._parse_one(
            Company911Email,
            super()._make_request("GET", data=data, params=params).json(),
        )

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> Company911Email:
        """
        Performs a POST request against the /company/{id}/911-email/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            Survey: The parsed Company data.
        """
        return self._parse_one(Company911Email, super()._make_request("POST", data=data, params=params).json())

    def delete(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> Company911Email:
        """
        Performs a DELETE request against the /company/{id}/911-email/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            Company911Email: The parsed response data.
        """
        return self._parse_one(Company911Email, super()._make_request("DELETE", data=data, params=params).json())
