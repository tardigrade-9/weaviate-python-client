from io import BufferedReader
from pathlib import Path
from typing import Generic, Optional, Type, Union, overload

from weaviate.collections.classes.filters import (
    _Filters,
)
from weaviate.collections.classes.grpc import MetadataQuery, PROPERTIES
from weaviate.collections.classes.internal import (
    _QueryReturn,
    QueryReturn,
    ReturnProperties,
)
from weaviate.collections.classes.types import (
    Properties,
    TProperties,
)
from weaviate.collections.queries.base import _Query


class _NearImageQuery(Generic[Properties], _Query[Properties]):
    @overload
    def near_image(
        self,
        near_image: Union[str, Path, BufferedReader],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _QueryReturn[Properties]:
        ...

    @overload
    def near_image(
        self,
        near_image: Union[str, Path, BufferedReader],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Type[TProperties],
    ) -> _QueryReturn[TProperties]:
        ...

    def near_image(
        self,
        near_image: Union[str, Path, BufferedReader],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> QueryReturn[Properties, TProperties]:
        """Search for objects in this collection by an image using an image-capable vectorisation module and vector-based similarity search.

        See the [docs](https://weaviate.io/developers/weaviate/search/image) for a more detailed explanation.

        NOTE:
            You must have an image-capable vectorisation module installed in order to use this method, e.g. `img2vec-neural`, `multi2vec-clip`, or `multi2vec-bind.

        Arguments:
            `near_image`
                The image file to search on, REQUIRED. This can be a base64 encoded string of the binary, a path to the file, or a file-like object.
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
            A `_QueryReturn` object that includes the searched objects.

        Raises:
            `weaviate.exceptions.WeaviateGrpcError`:
                If the request to the Weaviate server fails.
        """
        ret_properties, ret_metadata = self._parse_return_properties(return_properties)
        res = (
            self._query()
            .near_image(
                image=self._parse_media(near_image),
                certainty=certainty,
                distance=distance,
                filters=filters,
                limit=limit,
                autocut=auto_limit,
                return_metadata=return_metadata or ret_metadata,
                return_properties=ret_properties,
            )
            .sync()
        )
        return self._result_to_query_return(res, return_properties)


class _NearImageQueryAsync(Generic[Properties], _Query[Properties]):
    @overload
    async def near_image(
        self,
        near_image: Union[str, Path, BufferedReader],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _QueryReturn[Properties]:
        ...

    @overload
    async def near_image(
        self,
        near_image: Union[str, Path, BufferedReader],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Type[TProperties],
    ) -> _QueryReturn[TProperties]:
        ...

    async def near_image(
        self,
        near_image: Union[str, Path, BufferedReader],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> QueryReturn[Properties, TProperties]:
        """Search for objects in this collection by an image using an image-capable vectorisation module and vector-based similarity search.

        See the [docs](https://weaviate.io/developers/weaviate/search/image) for a more detailed explanation.

        NOTE:
            You must have an image-capable vectorisation module installed in order to use this method, e.g. `img2vec-neural`, `multi2vec-clip`, or `multi2vec-bind.

        Arguments:
            `near_image`
                The image file to search on, REQUIRED. This can be a base64 encoded string of the binary, a path to the file, or a file-like object.
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
            A `_QueryReturn` object that includes the searched objects.

        Raises:
            `weaviate.exceptions.WeaviateGrpcError`:
                If the request to the Weaviate server fails.
        """
        ret_properties, ret_metadata = self._parse_return_properties(return_properties)
        res = (
            await self._query()
            .near_image(
                image=self._parse_media(near_image),
                certainty=certainty,
                distance=distance,
                filters=filters,
                limit=limit,
                autocut=auto_limit,
                return_metadata=return_metadata or ret_metadata,
                return_properties=ret_properties,
            )
            .async_()
        )
        return self._result_to_query_return(res, return_properties)
