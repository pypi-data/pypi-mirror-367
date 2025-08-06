from typing import Any, Dict
from typing import List as ListType

from audiostack.helpers.api_item import APIResponseItem
from audiostack.helpers.api_list import APIResponseList
from audiostack.helpers.request_interface import RequestInterface
from audiostack.helpers.request_types import RequestTypes


class Voice:
    interface = RequestInterface(family="speech/voice")

    class Item(APIResponseItem):
        def __init__(self, response: dict) -> None:
            super().__init__(response)
            self.provider = self.data["provider"]
            self.alias = self.data["alias"]

    class List(APIResponseList):
        def __init__(self, response: dict, list_type: str) -> None:
            super().__init__(response, list_type)

        def resolve_item(self, list_type: str, item: Any) -> "Voice.Item":
            if list_type == "voices":
                return Voice.Item({"data": item})
            else:
                raise Exception()

    @staticmethod
    def query(
        filters: ListType[Dict] = [],
        minimumNumberOfResults: int = 3,
        forceApplyFilters: bool = True,
        page: int = 1,
        pageLimit: int = 1000,
    ) -> "Voice.List":
        body = {
            "filters": filters,
            "minimumNumberOfResults": minimumNumberOfResults,
            "forceApplyFilters": forceApplyFilters,
            "page": page,
            "pageLimit": pageLimit,
        }

        r = Voice.interface.send_request(
            rtype=RequestTypes.POST, route="query", json=body
        )
        return Voice.List(r, list_type="voices")

    @staticmethod
    def select_for_script(
        scriptId: str = "", scriptItem: Any = "", tone: str = "", targetLength: int = 20
    ) -> APIResponseItem:
        if scriptId and scriptItem:
            raise Exception("scriptId or scriptItem should be supplied not both")
        if not (scriptId or scriptItem):
            raise Exception("scriptId or scriptItem should be supplied")

        if scriptItem:
            scriptId = scriptItem.scriptId

        body = {"scriptId": scriptId, "tone": tone, "targetLength": targetLength}

        r = Voice.interface.send_request(
            rtype=RequestTypes.POST, route="select", json=body
        )
        return APIResponseItem(r)

    @staticmethod
    def select_for_content(content: str, tone: str = "") -> APIResponseItem:
        body = {"content": content}
        if tone:
            body["tone"] = tone

        r = Voice.interface.send_request(
            rtype=RequestTypes.POST, route="select", json=body
        )
        return APIResponseItem(r)

    @staticmethod
    def list() -> "Voice.List":
        r = Voice.interface.send_request(rtype=RequestTypes.GET, route="")
        return Voice.List(r, list_type="voices")

    class Parameter:
        @staticmethod
        def get() -> APIResponseItem:
            r = Voice.interface.send_request(rtype=RequestTypes.GET, route="parameter")
            return APIResponseItem(r)
