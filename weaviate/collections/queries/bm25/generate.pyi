from typing import Generic, List, Literal, Optional, Type, overload

from weaviate.collections.classes.filters import (
    _Filters,
)
from weaviate.collections.classes.grpc import Rerank, METADATA, PROPERTIES, REFERENCES
from weaviate.collections.classes.internal import (
    GenerativeReturn,
    References,
    TReferences,
    CrossReferences,
)
from weaviate.collections.classes.types import Properties, TProperties
from weaviate.collections.queries.base import _BaseQuery

class _BM25Generate(Generic[Properties, References], _BaseQuery[Properties, References]):
    @overload
    def bm25(
        self,
        query: str,
        *,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        query_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        rerank: Optional[Rerank] = None,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        return_properties: Optional[PROPERTIES] = None,
        return_references: Literal[None] = None,
    ) -> GenerativeReturn[Properties, References]: ...
    @overload
    def bm25(
        self,
        query: str,
        *,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        query_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        rerank: Optional[Rerank] = None,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        return_properties: Optional[PROPERTIES] = None,
        return_references: REFERENCES,
    ) -> GenerativeReturn[Properties, CrossReferences]: ...
    @overload
    def bm25(
        self,
        query: str,
        *,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        query_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        rerank: Optional[Rerank] = None,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        return_properties: Optional[PROPERTIES] = None,
        return_references: Type[TReferences],
    ) -> GenerativeReturn[Properties, TReferences]: ...
    @overload
    def bm25(
        self,
        query: str,
        *,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        query_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        rerank: Optional[Rerank] = None,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        return_properties: Type[TProperties],
        return_references: Literal[None] = None,
    ) -> GenerativeReturn[TProperties, References]: ...
    @overload
    def bm25(
        self,
        query: str,
        *,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        query_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        rerank: Optional[Rerank] = None,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        return_properties: Type[TProperties],
        return_references: REFERENCES,
    ) -> GenerativeReturn[TProperties, CrossReferences]: ...
    @overload
    def bm25(
        self,
        query: str,
        *,
        single_prompt: Optional[str] = None,
        grouped_task: Optional[str] = None,
        grouped_properties: Optional[List[str]] = None,
        query_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        rerank: Optional[Rerank] = None,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        return_properties: Type[TProperties],
        return_references: Type[TReferences],
    ) -> GenerativeReturn[TProperties, TReferences]: ...