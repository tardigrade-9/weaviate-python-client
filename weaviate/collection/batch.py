from typing import Any, Dict, List, Optional

import grpc  # type: ignore

from proto.v1 import batch_pb2

from requests.exceptions import ConnectionError as RequestsConnectionError

from weaviate.collection.classes.batch import _BatchDeleteResult
from weaviate.collection.classes.config import ConsistencyLevel
from weaviate.collection.classes.filters import _Filters
from weaviate.collection.filters import _FilterToREST
from weaviate.collection.grpc import _BaseGRPC
from weaviate.connect import Connection
from weaviate.exceptions import WeaviateGRPCException
from weaviate.util import _decode_json_response_dict


class _BatchGRPC(_BaseGRPC):
    def batch(self, batch: List[batch_pb2.BatchObject]) -> Dict[int, str]:
        metadata = self._get_metadata()

        try:
            assert self._connection.grpc_stub is not None
            res, _ = self._connection.grpc_stub.BatchObjects.with_call(
                batch_pb2.BatchObjectsRequest(
                    objects=batch,
                    consistency_level=self._consistency_level,
                ),
                metadata=metadata,
            )

            objects: Dict[int, str] = {}
            for result in res.errors:
                objects[result.index] = result.error
            return objects
        except grpc.RpcError as e:
            raise WeaviateGRPCException(e.details())


class _BatchREST:
    def __init__(self, connection: Connection) -> None:
        self.__connection = connection

    def delete(
        self,
        class_name: str,
        where: _Filters,
        verbose: bool,
        dry_run: bool,
        consistency_level: Optional[ConsistencyLevel],
        tenant: Optional[str],
    ) -> _BatchDeleteResult:
        payload: Dict[str, Any] = {
            "match": {
                "class": class_name,
                "where": _FilterToREST.convert(where),
            }
        }
        if verbose:
            payload["output"] = "verbose"
        if dry_run:
            payload["dryRun"] = True

        params = {}
        if consistency_level is not None:
            params["consistency"] = consistency_level.value
        if tenant is not None:
            params["tenant"] = tenant

        try:
            response = self.__connection.delete(
                path="/batch/objects",
                weaviate_object=payload,
                params=params,
            )
        except RequestsConnectionError as conn_err:
            raise RequestsConnectionError("Batch delete was not successful.") from conn_err
        res = _decode_json_response_dict(response, "Delete in batch")
        assert res is not None
        return _BatchDeleteResult(
            failed=res["results"]["failed"],
            matches=res["results"]["matches"],
            objects=res["results"]["objects"],
            successful=res["results"]["successful"],
        )
