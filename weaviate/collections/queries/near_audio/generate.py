from io import BufferedReader
from pathlib import Path
from typing import Generic, List, Optional, Type, Union, overload

from weaviate.collections.classes.filters import (
    _Filters,
)
from weaviate.collections.classes.grpc import (
    MetadataQuery,
    PROPERTIES,
)
from weaviate.collections.classes.internal import (
    _Generative,
    _GenerativeReturn,
    GenerativeReturn,
    ReturnProperties,
)
from weaviate.collections.classes.types import (
    Properties,
    TProperties,
)
from weaviate.collections.queries.base import _Query


class _NearAudioGenerate(Generic[Properties], _Query[Properties]):
    @overload
    def near_audio(
        self,
        near_audio: Union[str, Path, BufferedReader],
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _GenerativeReturn[Properties]:
        ...

    @overload
    def near_audio(
        self,
        near_audio: Union[str, Path, BufferedReader],
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Type[TProperties],
    ) -> _GenerativeReturn[TProperties]:
        ...

    def near_audio(
        self,
        near_audio: Union[str, Path, BufferedReader],
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> GenerativeReturn[Properties, TProperties]:
        """Perform retrieval-augmented generation (RaG) on the results of a by-audio object search in this collection using an audio-capable vectorisation module and vector-based similarity search.

        See the [docs](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/multi2vec-bind) for a more detailed explanation.

        NOTE:
            You must have an audio-capable vectorisation module installed in order to use this method, e.g. `multi2vec-bind`.

        Arguments:
            `near_audio`
                The audio file to search on, REQUIRED. This can be a base64 encoded string of the binary, a path to the file, or a file-like object.
            `certainty`
                The minimum similarity score to return. If not specified, the default certainty specified by the server is used.
            `distance`
                The maximum distance to search. If not specified, the default distance specified by the server is used.
            `limit`
                The maximum number of results to return. If not specified, the default limit specified by the server is returned.
            `auto_limit`
                The maximum number of [autocut](https://weaviate.io/developers/weaviate/api/graphql/additional-operators#autocut) results to return. If not specified, no limit is applied.
            `filters`
                The filters to apply to the search.
            `return_metadata`
                The metadata to return for each object.
            `return_properties`
                The properties to return for each object.


        Returns:
            A `_GenerativeReturn` object that includes the searched objects with per-object generated results and group generated results.

        Raises:
            `weaviate.exceptions.WeaviateGrpcError`:
                If the request to the Weaviate server fails.
        """
        ret_properties, ret_metadata = self._parse_return_properties(return_properties)
        res = (
            self._query()
            .near_audio(
                audio=self._parse_media(near_audio),
                certainty=certainty,
                distance=distance,
                filters=filters,
                generative=_Generative(
                    single=single_prompt,
                    grouped=grouped_task,
                    grouped_properties=grouped_properties,
                ),
                limit=limit,
                autocut=auto_limit,
                return_metadata=return_metadata or ret_metadata,
                return_properties=ret_properties,
            )
            .sync()
        )
        return self._result_to_generative_return(res, return_properties)


class _NearAudioGenerateAsync(Generic[Properties], _Query[Properties]):
    @overload
    async def near_audio(
        self,
        near_audio: Union[str, Path, BufferedReader],
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _GenerativeReturn[Properties]:
        ...

    @overload
    async def near_audio(
        self,
        near_audio: Union[str, Path, BufferedReader],
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Type[TProperties],
    ) -> _GenerativeReturn[TProperties]:
        ...

    async def near_audio(
        self,
        near_audio: Union[str, Path, BufferedReader],
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> GenerativeReturn[Properties, TProperties]:
        """Perform retrieval-augmented generation (RaG) on the results of a by-audio object search in this collection using an audio-capable vectorisation module and vector-based similarity search.

        See the [docs](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/multi2vec-bind) for a more detailed explanation.

        NOTE:
            You must have an audio-capable vectorisation module installed in order to use this method, e.g. `multi2vec-bind`.

        Arguments:
            `near_audio`
                The audio file to search on, REQUIRED. This can be a base64 encoded string of the binary, a path to the file, or a file-like object.
            `certainty`
                The minimum similarity score to return. If not specified, the default certainty specified by the server is used.
            `distance`
                The maximum distance to search. If not specified, the default distance specified by the server is used.
            `limit`
                The maximum number of results to return. If not specified, the default limit specified by the server is returned.
            `auto_limit`
                The maximum number of [autocut](https://weaviate.io/developers/weaviate/api/graphql/additional-operators#autocut) results to return. If not specified, no limit is applied.
            `filters`
                The filters to apply to the search.
            `return_metadata`
                The metadata to return for each object.
            `return_properties`
                The properties to return for each object.


        Returns:
            A `_GenerativeReturn` object that includes the searched objects with per-object generated results and group generated results.

        Raises:
            `weaviate.exceptions.WeaviateGrpcError`:
                If the request to the Weaviate server fails.
        """
        ret_properties, ret_metadata = self._parse_return_properties(return_properties)
        res = (
            await self._query()
            .near_audio(
                audio=self._parse_media(near_audio),
                certainty=certainty,
                distance=distance,
                filters=filters,
                generative=_Generative(
                    single=single_prompt,
                    grouped=grouped_task,
                    grouped_properties=grouped_properties,
                ),
                limit=limit,
                autocut=auto_limit,
                return_metadata=return_metadata or ret_metadata,
                return_properties=ret_properties,
            )
            .async_()
        )
        return self._result_to_generative_return(res, return_properties)
