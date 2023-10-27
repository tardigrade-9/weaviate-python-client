import asyncio
import datetime
import uuid as uuid_package
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
    Generic,
    Type,
    Union,
    cast,
    get_type_hints,
    get_origin,
)

from httpx import ConnectError as HttpxConnectionError

from weaviate.collections.classes.batch import (
    _BatchObject,
    BatchObjectReturn,
    _BatchReference,
    BatchReferenceReturn,
    _BatchDeleteResult,
)
from weaviate.collections.classes.config import ConsistencyLevel
from weaviate.collections.classes.data import (
    DataObject,
    DataReference,
)
from weaviate.collections.classes.internal import (
    _Object,
    _metadata_from_dict,
    _Reference,
)
from weaviate.collections.classes.types import Properties, TProperties, _check_data_model
from weaviate.collections.classes.filters import _Filters
from weaviate.collections.batch.grpc import _BatchGRPCAsync, _validate_props
from weaviate.collections.batch.rest import _BatchRESTAsync
from weaviate.connect import ConnectionAsync
from weaviate.exceptions import (
    UnexpectedStatusCodeException,
    ObjectAlreadyExistsException,
    WeaviateConnectionException,
)
from weaviate.util import (
    _datetime_to_string,
    _decode_json_response_dict,
)
from weaviate.types import BEACON, UUID


class _DataAsync:
    def __init__(
        self,
        connection: ConnectionAsync,
        name: str,
        consistency_level: Optional[ConsistencyLevel],
        tenant: Optional[str],
    ) -> None:
        self._connection = connection
        self.name = name
        self._consistency_level = consistency_level
        self._tenant = tenant
        self._batch_grpc = _BatchGRPCAsync(connection, consistency_level)
        self._batch_rest = _BatchRESTAsync(connection, consistency_level)

    async def _insert(self, weaviate_obj: Dict[str, Any], clean_props: bool) -> uuid_package.UUID:
        path = "/objects"
        _validate_props(weaviate_obj["properties"], clean_props=clean_props)

        params, weaviate_obj = self.__apply_context_to_params_and_object({}, weaviate_obj)
        try:
            response = await self._connection.post(
                path=path, weaviate_object=weaviate_obj, params=params
            )
        except HttpxConnectionError as conn_err:
            raise WeaviateConnectionException("Object was not added to Weaviate.") from conn_err
        if response.status_code == 200:
            return uuid_package.UUID(weaviate_obj["id"])

        try:
            response_json = _decode_json_response_dict(response, "insert object")
            assert response_json is not None
            if "already exists" in response_json["error"][0]["message"]:
                raise ObjectAlreadyExistsException(weaviate_obj["id"])
        except KeyError:
            pass
        raise UnexpectedStatusCodeException("Creating object", response)

    async def delete_by_id(self, uuid: UUID) -> bool:
        """Delete an object from the collection based on its UUID.

        Arguments:
            `uuid`
                The UUID of the object to delete, REQUIRED.
        """
        path = f"/objects/{self.name}/{uuid}"

        try:
            response = await self._connection.delete(path=path, params=self.__apply_context({}))
        except HttpxConnectionError as conn_err:
            raise WeaviateConnectionException("Object could not be deleted.") from conn_err
        if response.status_code == 204:
            return True  # Successfully deleted
        elif response.status_code == 404:
            return False  # did not exist
        raise UnexpectedStatusCodeException("Delete object", response)

    async def delete_many(
        self, where: _Filters, verbose: bool = False, dry_run: bool = False
    ) -> _BatchDeleteResult:
        """Delete multiple objects from the collection based on a filter.

        Arguments:
            `where`
                The filter to apply. This filter is the same that is used when performing queries and has the same syntax, REQUIRED.
            `verbose`
                Whether to return the deleted objects in the response.
            `dry_run`
                Whether to perform a dry run. If set to `True`, the objects will not be deleted, but the response will contain the objects that would have been deleted.

        Raises:
            `requests.ConnectionError`:
                If the network connection to Weaviate fails.
            `weaviate.UnexpectedStatusCodeException`:
                If Weaviate reports a non-OK status.
        """
        return await self._batch_rest.delete(self.name, where, verbose, dry_run, self._tenant)

    async def _replace(self, weaviate_obj: Dict[str, Any], uuid: UUID) -> None:
        path = f"/objects/{self.name}/{uuid}"
        params, weaviate_obj = self.__apply_context_to_params_and_object({}, weaviate_obj)

        weaviate_obj["id"] = str(uuid)  # must add ID to payload for PUT request

        try:
            response = await self._connection.put(
                path=path, weaviate_object=weaviate_obj, params=params
            )
        except HttpxConnectionError as conn_err:
            raise WeaviateConnectionException("Object was not replaced.") from conn_err
        if response.status_code == 200:
            return
        raise UnexpectedStatusCodeException("Replacing object", response)

    async def _update(self, weaviate_obj: Dict[str, Any], uuid: UUID) -> None:
        path = f"/objects/{self.name}/{uuid}"
        params, weaviate_obj = self.__apply_context_to_params_and_object({}, weaviate_obj)

        try:
            response = await self._connection.patch(
                path=path, weaviate_object=weaviate_obj, params=params
            )
        except HttpxConnectionError as conn_err:
            raise WeaviateConnectionException("Object was not updated.") from conn_err
        if response.status_code == 204:
            return
        raise UnexpectedStatusCodeException("Update object", response)

    async def _get_by_id(self, uuid: UUID, include_vector: bool) -> Optional[Dict[str, Any]]:
        path = f"/objects/{self.name}/{uuid}"
        params: Dict[str, Any] = {}
        if include_vector:
            params["include"] = "vector"
        return await self._get_from_weaviate(params=self.__apply_context(params), path=path)

    async def _get(self, limit: Optional[int], include_vector: bool) -> Optional[Dict[str, Any]]:
        path = "/objects"
        params: Dict[str, Any] = {"class": self.name}
        if limit is not None:
            params["limit"] = limit
        if include_vector:
            params["include"] = "vector"
        return await self._get_from_weaviate(params=self.__apply_context(params), path=path)

    async def _get_from_weaviate(
        self, params: Dict[str, Any], path: str
    ) -> Optional[Dict[str, Any]]:
        try:
            response = await self._connection.get(path=path, params=params)
        except HttpxConnectionError as conn_err:
            raise WeaviateConnectionException("Could not get object/s.") from conn_err
        if response.status_code == 200:
            response_json = _decode_json_response_dict(response, "get")
            assert response_json is not None
            return response_json
        if response.status_code == 404:
            return None
        raise UnexpectedStatusCodeException("Get object/s", response)

    async def _reference_add(self, from_uuid: UUID, from_property: str, ref: _Reference) -> None:
        params: Dict[str, str] = {}

        path = f"/objects/{self.name}/{from_uuid}/references/{from_property}"
        futures = [
            self._connection.post(
                path=path,
                weaviate_object=beacon,
                params=self.__apply_context(params),
            )
            for beacon in ref._to_beacons()
        ]
        try:
            responses = await asyncio.gather(*futures)
        except HttpxConnectionError as conn_err:
            raise WeaviateConnectionException("Reference was not added.") from conn_err
        for response in responses:
            if response.status_code != 200:
                raise UnexpectedStatusCodeException("Add property reference to object", response)

    async def _reference_add_many(self, refs: List[DataReference]) -> BatchReferenceReturn:
        return await self._batch_rest.references(
            [
                _BatchReference(
                    from_=f"{BEACON}{self.name}/{ref.from_uuid}/{ref.from_property}",
                    to=f"{BEACON}{ref.to_uuid}",
                    tenant=self._tenant,
                )
                for ref in refs
            ]
        )

    async def _reference_delete(self, from_uuid: UUID, from_property: str, ref: _Reference) -> None:
        params: Dict[str, str] = {}

        path = f"/objects/{self.name}/{from_uuid}/references/{from_property}"
        futures = [
            self._connection.delete(
                path=path,
                weaviate_object=beacon,
                params=self.__apply_context(params),
            )
            for beacon in ref._to_beacons()
        ]
        try:
            responses = await asyncio.gather(*futures)
        except HttpxConnectionError as conn_err:
            raise WeaviateConnectionException("Reference was not added.") from conn_err
        for response in responses:
            if response.status_code != 204:
                raise UnexpectedStatusCodeException("Add property reference to object", response)

    async def _reference_replace(
        self, from_uuid: UUID, from_property: str, ref: _Reference
    ) -> None:
        params: Dict[str, str] = {}

        path = f"/objects/{self.name}/{from_uuid}/references/{from_property}"
        try:
            response = await self._connection.put(
                path=path,
                weaviate_object=ref._to_beacons(),
                params=self.__apply_context(params),
            )
        except HttpxConnectionError as conn_err:
            raise WeaviateConnectionException("Reference was not added.") from conn_err
        if response.status_code != 200:
            raise UnexpectedStatusCodeException("Add property reference to object", response)

    def __apply_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if self._tenant is not None:
            params["tenant"] = self._tenant
        if self._consistency_level is not None:
            params["consistency_level"] = self._consistency_level
        return params

    def __apply_context_to_params_and_object(
        self, params: Dict[str, Any], obj: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if self._tenant is not None:
            obj["tenant"] = self._tenant
        if self._consistency_level is not None:
            params["consistency_level"] = self._consistency_level
        return params, obj

    def _serialize_properties(self, data: Properties) -> Dict[str, Any]:
        return {
            key: val._to_beacons()
            if isinstance(val, _Reference)
            else self.__serialize_primitive(val)
            for key, val in data.items()
        }

    def __serialize_primitive(self, value: Any) -> Any:
        if isinstance(value, uuid_package.UUID):
            return str(value)
        if isinstance(value, datetime.datetime):
            return _datetime_to_string(value)
        if isinstance(value, list):
            return [self.__serialize_primitive(val) for val in value]
        return value

    def _deserialize_primitive(self, value: Any, type_value: Optional[Any]) -> Any:
        if type_value is None:
            return value
        if type_value == uuid_package.UUID:
            return uuid_package.UUID(value)
        if type_value == datetime.datetime:
            return datetime.datetime.fromisoformat(value)
        if isinstance(type_value, list):
            return [
                self._deserialize_primitive(val, type_value[idx]) for idx, val in enumerate(value)
            ]
        return value


class _DataCollectionAsync(Generic[Properties], _DataAsync):
    def __init__(
        self,
        connection: ConnectionAsync,
        name: str,
        consistency_level: Optional[ConsistencyLevel],
        tenant: Optional[str],
        type_: Optional[Type[Properties]] = None,
    ):
        super().__init__(connection, name, consistency_level, tenant)
        self.__type = type_

    def with_data_model(self, data_model: Type[TProperties]) -> "_DataCollectionAsync[TProperties]":
        _check_data_model(data_model)
        return _DataCollectionAsync[TProperties](
            self._connection, self.name, self._consistency_level, self._tenant, data_model
        )

    def __deserialize_properties(self, data: Dict[str, Any]) -> Properties:
        hints = (
            get_type_hints(self.__type)
            if self.__type and not get_origin(self.__type) == dict
            else {}
        )
        return cast(
            Properties,
            {key: self._deserialize_primitive(val, hints.get(key)) for key, val in data.items()},
        )

    def _json_to_object(self, obj: Dict[str, Any]) -> _Object[Properties]:
        props = self.__deserialize_properties(obj["properties"])
        return _Object(
            properties=cast(Properties, props),
            metadata=_metadata_from_dict(obj),
        )

    async def insert(
        self,
        properties: Properties,
        uuid: Optional[UUID] = None,
        vector: Optional[List[float]] = None,
    ) -> uuid_package.UUID:
        """Insert a single object into the collection.

        Arguments:
            `properties`
                The properties of the object, REQUIRED.
            `uuid`
                The UUID of the object. If not provided, a random UUID will be generated.
            `vector`
                The vector of the object.
        """
        weaviate_obj: Dict[str, Any] = {
            "class": self.name,
            "properties": self._serialize_properties(properties),
            "id": str(uuid if uuid is not None else uuid_package.uuid4()),
        }

        if vector is not None:
            weaviate_obj["vector"] = vector

        return await self._insert(weaviate_obj, False)

    async def insert_many(
        self,
        objects: List[Union[Properties, DataObject[Properties]]],
    ) -> BatchObjectReturn:
        """Insert multiple objects into the collection.

        Arguments:
            `objects`
                The objects to insert. This can be either a list of `Properties` or `DataObject[Properties]`
                    If you didn't set `data_model` then `Properties` will be `Data[str, Any]` in which case you can insert simple dictionaries here.
                        If you want to insert vectors and UUIDs alongside your properties, you will have to use `DataObject` instead.

        Raises:
            `weaviate.exceptions.WeaviateQueryException`:
                If the network connection to Weaviate fails.
            `weaviate.exceptions.WeaviateInsertInvalidPropertyError`:
                If a property is invalid. I.e., has name `id` or `vector`, which are reserved.
        """
        return await self._batch_grpc.objects(
            [
                _BatchObject(
                    class_name=self.name,
                    vector=obj.vector,
                    uuid=obj.uuid,
                    properties=obj.properties,
                    tenant=self._tenant,
                )
                if isinstance(obj, DataObject) and isinstance(obj.properties, dict)
                else _BatchObject(
                    class_name=self.name,
                    vector=None,
                    uuid=None,
                    properties=cast(dict, obj),
                    tenant=None,
                )
                for obj in objects
            ]
        )

    async def replace(
        self, properties: Properties, uuid: UUID, vector: Optional[List[float]] = None
    ) -> None:
        """Replace an object in the collection.

        This is equivalent to a PUT operation.

        Arguments:
            `properties`
                The properties of the object, REQUIRED.
            `uuid`
                The UUID of the object, REQUIRED.
            `vector`
                The vector of the object.

        Raises:
            `requests.ConnectionError`:
                If the network connection to Weaviate fails.
            `weaviate.UnexpectedStatusCodeException`:
                If Weaviate reports a non-OK status.
            `weaviate.exceptions.WeaviateInsertInvalidPropertyError`:
                If a property is invalid. I.e., has name `id` or `vector`, which are reserved.
        """
        weaviate_obj: Dict[str, Any] = {
            "class": self.name,
            "properties": self._serialize_properties(properties),
        }
        if vector is not None:
            weaviate_obj["vector"] = vector

        await self._replace(weaviate_obj, uuid=uuid)

    async def update(
        self, properties: Properties, uuid: UUID, vector: Optional[List[float]] = None
    ) -> None:
        """Update an object in the collection.

        This is equivalent to a PATCH operation.

        Arguments:
            `properties`
                The properties of the object, REQUIRED.
            `uuid`
                The UUID of the object, REQUIRED.
            `vector`
                The vector of the object.
        """
        weaviate_obj: Dict[str, Any] = {
            "class": self.name,
            "properties": self._serialize_properties(properties),
        }
        if vector is not None:
            weaviate_obj["vector"] = vector

        await self._update(weaviate_obj, uuid=uuid)

    async def reference_add(self, from_uuid: UUID, from_property: str, ref: _Reference) -> None:
        """Create a reference between an object in this collection and any other object in Weaviate.

        Arguments:
            `from_uuid`
                The UUID of the object in this collection, REQUIRED.
            `from_property`
                The name of the property in the object in this collection, REQUIRED.
            `ref`
                The reference to add, REQUIRED. Use `Reference.to` to generate the correct type.

        Raises:
            `requests.ConnectionError`:
                If the network connection to Weaviate fails.
            `weaviate.UnexpectedStatusCodeException`:
                If Weaviate reports a non-OK status.
        """
        await self._reference_add(
            from_uuid=from_uuid,
            from_property=from_property,
            ref=ref,
        )

    async def reference_add_many(self, refs: List[DataReference]) -> BatchReferenceReturn:
        """Create multiple references on a property in batch between objects in this collection and any other object in Weaviate.

        Arguments:
            `refs`
                The references to add including the prop name, from UUID, and to UUID.

        Returns:
            `BatchReferenceReturn`
                A `BatchReferenceReturn` object containing the results of the batch operation.

        Raises:
            `requests.ConnectionError`:
                If the network connection to Weaviate fails.
            `weaviate.UnexpectedStatusCodeException
                If Weaviate reports a non-OK status.
        """
        return await self._reference_add_many(refs)

    async def reference_delete(self, from_uuid: UUID, from_property: str, ref: _Reference) -> None:
        """Delete a reference from an object within the collection.

        Arguments:
            `from_uuid`
                The UUID of the object in this collection, REQUIRED.
            `from_property`
                The name of the property in the object in this collection from which the reference should be deleted, REQUIRED.
            `ref`
                The reference to delete, REQUIRED. Use `Reference.to` to generate the correct type.
        """
        await self._reference_delete(from_uuid=from_uuid, from_property=from_property, ref=ref)

    async def reference_replace(self, from_uuid: UUID, from_property: str, ref: _Reference) -> None:
        """Replace a reference of an object within the collection.

        Arguments:
            `from_uuid`
                The UUID of the object in this collection, REQUIRED.
            `from_property`
                The name of the property in the object in this collection from which the reference should be replaced, REQUIRED.
            `ref`
                The reference to replace, REQUIRED. Use `Reference.to` to generate the correct type.
        """
        await self._reference_replace(from_uuid=from_uuid, from_property=from_property, ref=ref)
