import re
import math
from datetime import datetime
from typing import Any

from requests.structures import CaseInsensitiveDict


def cw_format_datetime(dt: datetime) -> str:
    """Format a datetime object as a string in ISO 8601 format. This is the format that Ironscales uses.

    Args:
        dt (datetime): The datetime object to be formatted.

    Returns:
        str: The formatted datetime string in the format "YYYY-MM-DDTHH:MM:SSZ".

    Example:
        from datetime import datetime

        dt = datetime(2022, 1, 1, 12, 0, 0)
        formatted_dt = cw_format_datetime(dt)
        print(formatted_dt)  # Output: "2022-01-01T12:00:00Z"
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_response_body(
    body: CaseInsensitiveDict,
) -> dict[str, Any] | None:
    """
    Parses response body to extract pagination information.

    Arguments:
    - body: content.json().get('pagination', {}) A dictionary containing the headers of an HTTP response.

    Returns:
    - A dictionary containing the extracted pagination information. The keys in the dictionary include:
      - "first_page": An optional integer representing the number of the first page.
      - "prev_page": An optional integer representing the number of the previous page.
      - "next_page": An optional integer representing the number of the next page.
      - "last_page": An optional integer representing the number of the last page.
      - "has_next_page": A boolean indicating whether there is a next page.
      - "has_prev_page": A boolean indicating whether there is a previous page.

    If the "Link" header is not present in the headers dictionary, None is returned.

    Example Usage:
        headers = {
            "Link": '<https://example.com/api?page=1>; rel="first", <https://example.com/api?page=2>; rel="next"'
        }
        pagination_info = parse_link_headers(headers)
        print(pagination_info)
        # Output: {'first_page': 1, 'next_page': 2, 'has_next_page': True}
    """
    if body.get("page") is None:
        return None
    has_next_page: bool = False
    has_prev_page: bool = False
    first_page: int | None = None
    prev_page: int | None = None
    page: int | None = None
    current_page_count: int | None = None
    limit: int | None = None
    total_count: int | None = None
    next_page: int | None = None
    next_page_url: str | None = None
    next_page_token: str | None = None
    total_pages: int | None = None

    result = {}

    if body.get("first_page") is not None:
        result["first_page"] = body.get("first_page")

    if body.get("prev_page") is not None:
        result["prev_page"] = body.get("prev_page")
    elif body.get("page") is not None:
        if body.get("page") > 1:
            result["prev_page"] = body.get("page") - 1

    if body.get("next_page") is not None:
        result["next_page"] = body.get("next_page")
    elif body.get("currentPage") is not None and body.get("currentPage") < body.get("lastPage"):
        result["next_page"] = body.get("currentPage") + 1

    if body.get("total_pages") is not None:
        result["last_page"] = body.get("total_pages")

    if body.get("page") is not None and body.get("page") == body.get("total_pages"):
        result["has_next_page"] = False
    elif body.get("page") is not None and body.get("page") < body.get("total_pages"):
        result["has_next_page"] = True
    
    if body.get("page") is not None:
        if body.get("page") > 1:
            result["has_prev_page"] = True

    return result
    
def parse_link_headers(
    headers: CaseInsensitiveDict,
) -> dict[str, Any] | None:
    """
    Parses link headers to extract pagination information.

    Arguments:
    - headers: A dictionary containing the headers of an HTTP response. The value associated with the "Link" key should be a string representing the link headers.

    Returns:
    - A dictionary containing the extracted pagination information. The keys in the dictionary include:
      - "first_page": An optional integer representing the number of the first page.
      - "prev_page": An optional integer representing the number of the previous page.
      - "next_page": An optional integer representing the number of the next page.
      - "last_page": An optional integer representing the number of the last page.
      - "has_next_page": A boolean indicating whether there is a next page.
      - "has_prev_page": A boolean indicating whether there is a previous page.

    If the "Link" header is not present in the headers dictionary, None is returned.

    Example Usage:
        headers = {
            "Link": '<https://example.com/api?page=1>; rel="first", <https://example.com/api?page=2>; rel="next"'
        }
        pagination_info = parse_link_headers(headers)
        print(pagination_info)
        # Output: {'first_page': 1, 'next_page': 2, 'has_next_page': True}
    """
    if headers.get("Link") is None:
        return None
    links = headers["Link"].split(",")
    has_next_page: bool = False
    has_prev_page: bool = False
    first_page: int | None = None
    prev_page: int | None = None
    next_page: int | None = None
    last_page: int | None = None

    for link in links:
        match = re.search(r'page=(\d+)>; rel="(.*?)"', link)
        if match:
            page_number = int(match.group(1))
            rel_value = match.group(2)
            if rel_value == "first":
                first_page = page_number
            elif rel_value == "prev":
                prev_page = page_number
                has_prev_page = True
            elif rel_value == "next":
                next_page = page_number
                has_next_page = True
            elif rel_value == "last":
                last_page = page_number

    result = {}

    if first_page is not None:
        result["first_page"] = first_page

    if prev_page is not None:
        result["prev_page"] = prev_page

    if next_page is not None:
        result["next_page"] = next_page

    if last_page is not None:
        result["last_page"] = last_page

    if has_next_page:
        result["has_next_page"] = has_next_page

    if has_prev_page:
        result["has_prev_page"] = has_prev_page

    return result
