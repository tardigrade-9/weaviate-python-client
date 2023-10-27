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
    _GenerativeReturn,
    _Generative,
    GenerativeReturn,
    ReturnProperties,
)
from weaviate.collections.classes.types import Properties, TProperties
from weaviate.collections.queries.base import _Query
from weaviate.types import UUID


class _FetchObjectsGenerate(Generic[Properties], _Query[Properties]):
    @overload
    def fetch_objects(
        self,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _GenerativeReturn[Properties]:
        ...

    @overload
    def fetch_objects(
        self,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Type[TProperties],
    ) -> _GenerativeReturn[TProperties]:
        ...

    def fetch_objects(
        self,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> GenerativeReturn[Properties, TProperties]:
        """Perform retrieval-augmented generation (RaG) on the results of a simple get query of objects in this collection.

        Arguments:
            `single_prompt`
                The prompt to use for RaG on each object individually.
            `grouped_task`
                The prompt to use for RaG on the entire result set.
            `grouped_properties`
                The properties to use in the RaG on the entire result set.
            `limit`
                The maximum number of results to return. If not specified, the default limit specified by Weaviate is returned.
            `offset`
                The offset to start from. If not specified, the retrieval begins from the first object in Weaviate.
            `after`
                The UUID of the object to start from. If not specified, the retrieval begins from the first object in Weaviate.
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
            A `_GenerativeReturn` object that includes the searched objects with per-object generated results and group generated results.

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
                generative=_Generative(
                    single=single_prompt,
                    grouped=grouped_task,
                    grouped_properties=grouped_properties,
                ),
            )
            .sync()
        )
        return self._result_to_generative_return(res, return_properties)


class _FetchObjectsGenerateAsync(Generic[Properties], _Query[Properties]):
    @overload
    async def fetch_objects(
        self,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> _GenerativeReturn[Properties]:
        ...

    @overload
    async def fetch_objects(
        self,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        *,
        return_properties: Type[TProperties],
    ) -> _GenerativeReturn[TProperties]:
        ...

    async def fetch_objects(
        self,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[Union[Sort, List[Sort]]] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
    ) -> GenerativeReturn[Properties, TProperties]:
        """Perform retrieval-augmented generation (RaG) on the results of a simple get query of objects in this collection.

        Arguments:
            `single_prompt`
                The prompt to use for RaG on each object individually.
            `grouped_task`
                The prompt to use for RaG on the entire result set.
            `grouped_properties`
                The properties to use in the RaG on the entire result set.
            `limit`
                The maximum number of results to return. If not specified, the default limit specified by Weaviate is returned.
            `offset`
                The offset to start from. If not specified, the retrieval begins from the first object in Weaviate.
            `after`
                The UUID of the object to start from. If not specified, the retrieval begins from the first object in Weaviate.
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
            A `_GenerativeReturn` object that includes the searched objects with per-object generated results and group generated results.

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
                generative=_Generative(
                    single=single_prompt,
                    grouped=grouped_task,
                    grouped_properties=grouped_properties,
                ),
            )
            .async_()
        )
        return self._result_to_generative_return(res, return_properties)
