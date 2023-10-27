from typing import Generic, List, Optional, Union, Type, overload

from weaviate.collections.classes.filters import (
    _Filters,
)
from weaviate.collections.classes.grpc import (
    MetadataQuery,
    PROPERTIES,
    Sort,
)
from weaviate.collections.classes.internal import (
    _QueryReturn,
    QueryReturn,
    ReturnProperties,
)
from weaviate.collections.classes.types import Properties, TProperties
from weaviate.collections.queries.base import _Query
from weaviate.types import UUID


class _FetchObjectsQuery(Generic[Properties], _Query[Properties]):
    @overload
    def fetch_objects(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _QueryReturn[Properties]:
        ...

    @overload
    def fetch_objects(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Type[TProperties],
    ) -> _QueryReturn[TProperties]:
        ...

    def fetch_objects(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> QueryReturn[Properties, TProperties]:
        """Retrieve the objects in this collection without any search.

        Arguments:
            `limit`
                The maximum number of results to return. If not specified, the default limit specified by the server is returned.
            `offset`
                The offset to start from. If not specified, the retrieval begins from the first object in the server.
            `after`
                The UUID of the object to start from. If not specified, the retrieval begins from the first object in the server.
            `filters`
                The filters to apply to the retrieval.
            `sort`
                The sorting to apply to the retrieval.
            `return_metadata`
                The metadata to return for each object.
            `return_properties`
                The properties to return for each object.

        NOTE:
            If neither `return_metadata` nor `return_properties` are provided then all properties and metadata are returned except for `metadata.vector`.

        Returns:
            A `_QueryReturn` object that includes the searched objects.

        Raises:
            `weaviate.exceptions.WeaviateQueryException`:
                If the network connection to Weaviate fails.
        """
        ret_properties, ret_metadata = self._parse_return_properties(return_properties)
        res = (
            self._query()
            .get(
                limit=limit,
                offset=offset,
                after=after,
                filters=filters,
                sort=sort,
                return_metadata=return_metadata or ret_metadata,
                return_properties=ret_properties,
            )
            .sync()
        )
        return self._result_to_query_return(res, return_properties)


class _FetchObjectsQueryAsync(Generic[Properties], _Query[Properties]):
    @overload
    async def fetch_objects(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _QueryReturn[Properties]:
        ...

    @overload
    async def fetch_objects(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Type[TProperties],
    ) -> _QueryReturn[TProperties]:
        ...

    async def fetch_objects(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> QueryReturn[Properties, TProperties]:
        """Retrieve the objects in this collection without any search.

        Arguments:
            `limit`
                The maximum number of results to return. If not specified, the default limit specified by the server is returned.
            `offset`
                The offset to start from. If not specified, the retrieval begins from the first object in the server.
            `after`
                The UUID of the object to start from. If not specified, the retrieval begins from the first object in the server.
            `filters`
                The filters to apply to the retrieval.
            `sort`
                The sorting to apply to the retrieval.
            `return_metadata`
                The metadata to return for each object.
            `return_properties`
                The properties to return for each object.

        NOTE:
            If neither `return_metadata` nor `return_properties` are provided then all properties and metadata are returned except for `metadata.vector`.

        Returns:
            A `_QueryReturn` object that includes the searched objects.

        Raises:
            `weaviate.exceptions.WeaviateQueryException`:
                If the network connection to Weaviate fails.
        """
        ret_properties, ret_metadata = self._parse_return_properties(return_properties)
        res = (
            await self._query()
            .get(
                limit=limit,
                offset=offset,
                after=after,
                filters=filters,
                sort=sort,
                return_metadata=return_metadata or ret_metadata,
                return_properties=ret_properties,
            )
            .async_()
        )
        return self._result_to_query_return(res, return_properties)
