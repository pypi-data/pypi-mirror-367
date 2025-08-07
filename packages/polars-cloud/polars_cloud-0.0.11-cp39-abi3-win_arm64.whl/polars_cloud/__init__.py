"""Polars Cloud client.

Enables users to interact with workspaces, clusters, and queries on Polars Cloud.
"""

from polars_cloud import exceptions
from polars_cloud._version import __version__
from polars_cloud.auth import authenticate, login
from polars_cloud.context import (
    ClientContext,
    ClusterContext,
    ComputeContext,
    ComputeContextStatus,
    set_compute_context,
)
from polars_cloud.organization import (
    Organization,
)
from polars_cloud.polars_cloud import LogLevelSchema
from polars_cloud.query import (
    BatchQuery,
    Broadcast,
    CsvDst,
    ExecuteRemote,
    InteractiveQuery,
    IpcDst,
    LazyFrameRemote,
    ParquetDst,
    QueryInfo,
    QueryProgress,
    QueryResult,
    QueryStatus,
    StageStatistics,
    spawn,
    spawn_blocking,
    spawn_many,
    spawn_many_blocking,
)
from polars_cloud.workspace import (
    Workspace,
    WorkspaceDefaultComputeSpecs,
    WorkspaceStatus,
)

__all__ = [
    "BatchQuery",
    "Broadcast",
    "ClientContext",
    "ClusterContext",
    "ComputeContext",
    "ComputeContextStatus",
    "CsvDst",
    "ExecuteRemote",
    "InteractiveQuery",
    "IpcDst",
    "LazyFrameRemote",
    "LogLevelSchema",
    "Organization",
    "ParquetDst",
    "QueryInfo",
    "QueryProgress",
    "QueryResult",
    "QueryStatus",
    "StageStatistics",
    "Workspace",
    "WorkspaceDefaultComputeSpecs",
    "WorkspaceStatus",
    "__version__",
    "authenticate",
    "exceptions",
    "login",
    "set_compute_context",
    "spawn",
    "spawn_blocking",
    "spawn_many",
    "spawn_many_blocking",
]
