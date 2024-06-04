import json
from dataclasses import asdict
from typing import Generic, List, Literal, Optional, Type, Union, overload

from weaviate.collections.aggregate import _AggregateCollectionAsync
from weaviate.collections.backups import _CollectionBackupAsync
from weaviate.collections.classes.cluster import Shard
from weaviate.collections.classes.config import ConsistencyLevel
from weaviate.collections.classes.grpc import METADATA, PROPERTIES, REFERENCES
from weaviate.collections.classes.internal import (
    CrossReferences,
    References,
    ReturnProperties,
    ReturnReferences,
    TReferences,
)
from weaviate.collections.classes.tenants import Tenant
from weaviate.collections.classes.types import Properties, TProperties
from weaviate.collections.cluster import _ClusterAsync
from weaviate.collections.config import _ConfigCollectionAsync
from weaviate.collections.data import _DataCollectionAsync
from weaviate.collections.generate import _GenerateCollectionAsync
from weaviate.collections.iterator import _IteratorInputs, _ObjectAIterator
from weaviate.collections.query import _QueryCollectionAsync
from weaviate.collections.tenants import _TenantsAsync
from weaviate.connect import ConnectionV4
from weaviate.types import UUID
from weaviate.util import _capitalize_first_letter
from weaviate.validator import _validate_input, _ValidateArgument


class CollectionAsync(Generic[Properties, References]):
    """The collection class is the main entry point for interacting with a collection in Weaviate.

    This class is returned by the `client.collections.create` and `client.collections.get` methods. It provides
    access to all the methods available to you when interacting with a collection in Weaviate.

    You should not need to instantiate this class yourself but it may be useful to import this as a type when
    performing type hinting of functions that depend on a collection object.

    Attributes:
        `aggregate`
            This namespace includes all the querying methods available to you when using Weaviate's standard aggregation capabilities.
        `aggregate_group_by`
            This namespace includes all the aggregate methods available to you when using Weaviate's aggregation group-by capabilities.
        `config`
            This namespace includes all the CRUD methods available to you when modifying the configuration of the collection in Weaviate.
        `data`
            This namespace includes all the CUD methods available to you when modifying the data of the collection in Weaviate.
        `generate`
            This namespace includes all the querying methods available to you when using Weaviate's generative capabilities.
        `query_group_by`
            This namespace includes all the querying methods available to you when using Weaviate's querying group-by capabilities.
        `query`
            This namespace includes all the querying methods available to you when using Weaviate's standard query capabilities.
        `tenants`
            This namespace includes all the CRUD methods available to you when modifying the tenants of a multi-tenancy-enabled collection in Weaviate.
    """

    def __init__(
        self,
        connection: ConnectionV4,
        name: str,
        validate_arguments: bool,
        consistency_level: Optional[ConsistencyLevel] = None,
        tenant: Optional[str] = None,
        properties: Optional[Type[Properties]] = None,
        references: Optional[Type[References]] = None,
    ) -> None:
        self._connection = connection
        self.name = _capitalize_first_letter(name)
        self.__cluster = _ClusterAsync(connection)
        self._validate_arguments = validate_arguments

        self.__tenant = tenant
        self.__consistency_level = consistency_level
        self.__properties = properties
        self.__references = references

        self.aggregate = _AggregateCollectionAsync(
            self._connection, self.name, consistency_level, tenant
        )
        """This namespace includes all the querying methods available to you when using Weaviate's standard aggregation capabilities."""
        self.backup = _CollectionBackupAsync(connection, self.name)
        """This namespace includes all the backup methods available to you when backing up a collection in Weaviate."""
        self.config = _ConfigCollectionAsync(self._connection, self.name, tenant)
        """This namespace includes all the CRUD methods available to you when modifying the configuration of the collection in Weaviate."""
        self.data = _DataCollectionAsync[Properties](
            connection, self.name, consistency_level, tenant, validate_arguments, properties
        )
        """This namespace includes all the CUD methods available to you when modifying the data of the collection in Weaviate."""
        self.generate = _GenerateCollectionAsync[Properties, References](
            connection,
            self.name,
            consistency_level,
            tenant,
            properties,
            references,
            validate_arguments,
        )
        """This namespace includes all the querying methods available to you when using Weaviate's generative capabilities."""
        self.query = _QueryCollectionAsync[Properties, References](
            connection,
            self.name,
            consistency_level,
            tenant,
            properties,
            references,
            validate_arguments,
        )
        """This namespace includes all the querying methods available to you when using Weaviate's standard query capabilities."""
        self.tenants = _TenantsAsync(connection, self.name)
        """This namespace includes all the CRUD methods available to you when modifying the tenants of a multi-tenancy-enabled collection in Weaviate."""

    @property
    def tenant(self) -> Optional[str]:
        """The tenant of this collection object."""
        return self.__tenant

    @property
    def consistency_level(self) -> Optional[ConsistencyLevel]:
        """The consistency level of this collection object."""
        return self.__consistency_level

    def with_tenant(
        self, tenant: Optional[Union[str, Tenant]] = None
    ) -> "CollectionAsync[Properties, References]":
        """Use this method to return a collection object specific to a single tenant.

        If multi-tenancy is not configured for this collection then Weaviate will throw an error.

        This method does not send a request to Weaviate. It only returns a new collection object that is specific
        to the tenant you specify.

        Arguments:
            `tenant`
                The tenant to use. Can be `str` or `wvc.tenants.Tenant`.
        """
        _validate_input(
            [_ValidateArgument(expected=[str, Tenant, None], name="tenant", value=tenant)]
        )
        return CollectionAsync[Properties, References](
            self._connection,
            self.name,
            self._validate_arguments,
            self.__consistency_level,
            tenant.name if isinstance(tenant, Tenant) else tenant,
            self.__properties,
            self.__references,
        )

    def with_consistency_level(
        self, consistency_level: Optional[ConsistencyLevel] = None
    ) -> "CollectionAsync[Properties, References]":
        """Use this method to return a collection object specific to a single consistency level.

        If replication is not configured for this collection then Weaviate will throw an error.

        This method does not send a request to Weaviate. It only returns a new collection object that is specific
        to the consistency level you specify.

        Arguments:
            `consistency_level`
                The consistency level to use.
        """
        if self._validate_arguments:
            _validate_input(
                [
                    _ValidateArgument(
                        expected=[ConsistencyLevel, None],
                        name="consistency_level",
                        value=consistency_level,
                    )
                ]
            )
        return CollectionAsync[Properties, References](
            self._connection,
            self.name,
            self._validate_arguments,
            consistency_level,
            self.__tenant,
            self.__properties,
            self.__references,
        )

    async def length(self) -> int:
        """Get the total number of objects in the collection."""
        total = (await self.aggregate.over_all(total_count=True)).total_count
        assert total is not None
        return total

    async def to_string(self) -> str:
        """Return a string representation of the collection object."""
        config = await self.config.get()
        json_ = json.dumps(asdict(config), indent=2)
        return f"<weaviate.Collection config={json_}>"

    @overload
    def iterator(
        self,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        *,
        return_properties: Optional[PROPERTIES] = None,
        return_references: Literal[None] = None,
        after: Optional[UUID] = None,
    ) -> _ObjectAIterator[Properties, References]:
        ...

    @overload
    def iterator(
        self,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        *,
        return_properties: Optional[PROPERTIES] = None,
        return_references: REFERENCES,
        after: Optional[UUID] = None,
    ) -> _ObjectAIterator[Properties, CrossReferences]:
        ...

    @overload
    def iterator(
        self,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        *,
        return_properties: Optional[PROPERTIES] = None,
        return_references: Type[TReferences],
        after: Optional[UUID] = None,
    ) -> _ObjectAIterator[Properties, TReferences]:
        ...

    @overload
    def iterator(
        self,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        *,
        return_properties: Type[TProperties],
        return_references: Literal[None] = None,
        after: Optional[UUID] = None,
    ) -> _ObjectAIterator[TProperties, References]:
        ...

    @overload
    def iterator(
        self,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        *,
        return_properties: Type[TProperties],
        return_references: REFERENCES,
        after: Optional[UUID] = None,
    ) -> _ObjectAIterator[TProperties, CrossReferences]:
        ...

    @overload
    def iterator(
        self,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        *,
        return_properties: Type[TProperties],
        return_references: Type[TReferences],
        after: Optional[UUID] = None,
    ) -> _ObjectAIterator[TProperties, TReferences]:
        ...

    def iterator(  # type: ignore
        self,
        include_vector: bool = False,
        return_metadata: Optional[METADATA] = None,
        *,
        return_properties: Optional[ReturnProperties[TProperties]] = None,
        return_references: Optional[ReturnReferences[TReferences]] = None,
        after: Optional[UUID] = None,
    ) -> Union[
        _ObjectAIterator[Properties, References],
        _ObjectAIterator[Properties, CrossReferences],
        _ObjectAIterator[Properties, TReferences],
        _ObjectAIterator[TProperties, References],
        _ObjectAIterator[TProperties, CrossReferences],
        _ObjectAIterator[TProperties, TReferences],
    ]:
        """Use this method to return an iterator over the objects in the collection.

        This iterator keeps a record of the last object that it returned to be used in each subsequent call to
        Weaviate. Once the collection is exhausted, the iterator exits.

        If `return_properties` is not provided, all the properties of each object will be
        requested from Weaviate except for its vector as this is an expensive operation. Specify `include_vector`
        to request the vector back as well. In addition, if `return_references=None` then none of the references
        are returned. Use `wvc.QueryReference` to specify which references to return.

        Arguments:
            `include_vector`
                Whether to include the vector in the metadata of the returned objects.
            `return_metadata`
                The metadata to return with each object.
            `return_properties`
                The properties to return with each object.
            `return_references`
                The references to return with each object.
            `after`
                The cursor to use to mark the initial starting point of the iterator in the collection.

        Raises:
            `weaviate.exceptions.WeaviateGRPCQueryError`:
                If the request to the Weaviate server fails.
        """
        return _ObjectAIterator(
            self.query,
            _IteratorInputs(
                include_vector=include_vector,
                return_metadata=return_metadata,
                return_properties=return_properties,
                return_references=return_references,
                after=after,
            ),
        )

    async def exists(self) -> bool:
        """Check if the collection exists in Weaviate."""
        try:
            await self.config.get(simple=True)
            return True
        except Exception:
            return False

    async def shards(self) -> List[Shard]:
        """
        Get the statuses of all the shards of this collection.

        Returns:
            The list of shards belonging to this collection.

        Raises
            `weaviate.WeaviateConnectionError`
                If the network connection to weaviate fails.
            `weaviate.UnexpectedStatusCodeError`
                If weaviate reports a none OK status.
            `weaviate.EmptyResponseError`
                If the response is empty.
        """
        return [
            shard
            for node in await self.__cluster.nodes(self.name, output="verbose")
            for shard in node.shards
        ]