from io import BufferedReader
from pathlib import Path
from typing import Generic, Optional, Type, Union, overload

from weaviate.collections.classes.filters import (
    _Filters,
)
from weaviate.collections.classes.grpc import (
    MetadataQuery,
    PROPERTIES,
)
from weaviate.collections.classes.internal import (
    _GroupBy,
    _GroupByReturn,
    GroupByReturn,
    ReturnProperties,
)
from weaviate.collections.classes.types import Properties, TProperties
from weaviate.collections.queries.base import _Query


class _NearVideoGroupBy(Generic[Properties], _Query[Properties]):
    @overload
    def near_video(
        self,
        near_video: Union[str, Path, BufferedReader],
        group_by_property: str,
        number_of_groups: int,
        objects_per_group: int,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _GroupByReturn[Properties]:
        ...

    @overload
    def near_video(
        self,
        near_video: Union[str, Path, BufferedReader],
        group_by_property: str,
        number_of_groups: int,
        objects_per_group: int,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Type[TProperties],
    ) -> _GroupByReturn[TProperties]:
        ...

    def near_video(
        self,
        near_video: Union[str, Path, BufferedReader],
        group_by_property: str,
        number_of_groups: int,
        objects_per_group: int,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> GroupByReturn[Properties, TProperties]:
        """Group the results of a by-video object search in this collection using the video-capable vectorisation module and vector-based similarity search.

        See the [docs](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/multi2vec-bind) for a more detailed explanation.

        Arguments:
            `near_video`
                The video file to search on, REQUIRED. This can be a base64 encoded string of the binary, a path to the file, or a file-like object.
            `group_by_property`
                The property to group on.
            `number_of_groups`
                The number of groups to return.
            `objects_per_group`
                The number of objects per group to return.
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
            A `_GroupByReturn` object that includes the searched objects grouped by the specified property.

        Raises:
            `weaviate.exceptions.WeaviateGrpcError`:
                If the request to the Weaviate server fails.
        """
        ret_properties, ret_metadata = self._parse_return_properties(return_properties)
        res = (
            self._query()
            .near_video(
                video=self._parse_media(near_video),
                certainty=certainty,
                distance=distance,
                filters=filters,
                group_by=_GroupBy(
                    prop=group_by_property,
                    number_of_groups=number_of_groups,
                    objects_per_group=objects_per_group,
                ),
                limit=limit,
                autocut=auto_limit,
                return_metadata=return_metadata or ret_metadata,
                return_properties=ret_properties,
            )
            .sync()
        )
        return self._result_to_groupby_return(res, return_properties)


class _NearVideoGroupByAsync(Generic[Properties], _Query[Properties]):
    @overload
    async def near_video(
        self,
        near_video: Union[str, Path, BufferedReader],
        group_by_property: str,
        number_of_groups: int,
        objects_per_group: int,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _GroupByReturn[Properties]:
        ...

    @overload
    async def near_video(
        self,
        near_video: Union[str, Path, BufferedReader],
        group_by_property: str,
        number_of_groups: int,
        objects_per_group: int,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Type[TProperties],
    ) -> _GroupByReturn[TProperties]:
        ...

    async def near_video(
        self,
        near_video: Union[str, Path, BufferedReader],
        group_by_property: str,
        number_of_groups: int,
        objects_per_group: int,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> GroupByReturn[Properties, TProperties]:
        """Group the results of a by-video object search in this collection using the video-capable vectorisation module and vector-based similarity search.

        See the [docs](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/multi2vec-bind) for a more detailed explanation.

        Arguments:
            `near_video`
                The video file to search on, REQUIRED. This can be a base64 encoded string of the binary, a path to the file, or a file-like object.
            `group_by_property`
                The property to group on.
            `number_of_groups`
                The number of groups to return.
            `objects_per_group`
                The number of objects per group to return.
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
            A `_GroupByReturn` object that includes the searched objects grouped by the specified property.

        Raises:
            `weaviate.exceptions.WeaviateGrpcError`:
                If the request to the Weaviate server fails.
        """
        ret_properties, ret_metadata = self._parse_return_properties(return_properties)
        res = (
            await self._query()
            .near_video(
                video=self._parse_media(near_video),
                certainty=certainty,
                distance=distance,
                filters=filters,
                group_by=_GroupBy(
                    prop=group_by_property,
                    number_of_groups=number_of_groups,
                    objects_per_group=objects_per_group,
                ),
                limit=limit,
                autocut=auto_limit,
                return_metadata=return_metadata or ret_metadata,
                return_properties=ret_properties,
            )
            .async_()
        )
        return self._result_to_groupby_return(res, return_properties)
