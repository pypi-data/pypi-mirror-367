import json
from typing import Any, Iterable, List, Union
from obiguard.api_resources.apis.api_resource import APIResource, AsyncAPIResource
from obiguard.api_resources.client import AsyncObiguard, Obiguard
from ..._vendor.openai._types import NotGiven, NOT_GIVEN
from obiguard.api_resources.types.moderations_type import ModerationCreateResponse


class Moderations(APIResource):
    def __init__(self, client: Obiguard) -> None:
        super().__init__(client)
        self.openai_client = client.openai_client

    def create(
        self,
        *,
        input: Union[str, List[str], Iterable[Any]],
        model: Union[str, NotGiven] = NOT_GIVEN,
        **kwargs
    ) -> ModerationCreateResponse:
        response = self.openai_client.with_raw_response.moderations.create(
            input=input, model=model, extra_body=kwargs
        )
        data = ModerationCreateResponse(**json.loads(response.text))
        data._headers = response.headers

        return data


class AsyncModerations(AsyncAPIResource):
    def __init__(self, client: AsyncObiguard) -> None:
        super().__init__(client)
        self.openai_client = client.openai_client

    async def create(
        self,
        *,
        input: Union[str, List[str], Iterable[Any]],
        model: Union[str, NotGiven] = NOT_GIVEN,
        **kwargs
    ) -> ModerationCreateResponse:
        response = await self.openai_client.with_raw_response.moderations.create(
            input=input, model=model, extra_body=kwargs
        )
        data = ModerationCreateResponse(**json.loads(response.text))
        data._headers = response.headers

        return data
