from __future__ import annotations

import abc
import dataclasses as dc
import enum
from immutabledict import immutabledict
from pathlib import Path
import typing as ty
from urllib import parse as _up

import sqlalchemy as sa
from sqlalchemy import pool as sap

__all__ = [
    "create_engine_sqlite",
    "SQLAlchemySqliteTransactionFix",
    "sqlite_file_uri",
    "MissingExecutionOptionError",
    "Options",
    "SchemaOptions",
    "Journal",
    "Begin",
    "SecureDelete",
    "ForeignKeys",
    "Synchronous",
]


class MissingExecutionOptionError(ValueError):
    pass


class Journal(enum.Enum):
    """
    https://www.sqlite.org/pragma.html#pragma_journal_mode
    """

    DELETE = enum.auto()
    TRUNCATE = enum.auto()
    PERSIST = enum.auto()
    MEMORY = enum.auto()
    WAL = enum.auto()
    WAL2 = enum.auto()  # only available on a particular branch
    OFF = enum.auto()


class Begin(enum.Enum):
    """
    https://www.sqlite.org/lang_transaction.html
    """

    DEFERRED = enum.auto()
    IMMEDIATE = enum.auto()
    EXCLUSIVE = enum.auto()
    CONCURRENT = enum.auto()  # only available on a particular branch


class SecureDelete(enum.Enum):
    """
    https://www.sqlite.org/pragma.html#pragma_secure_delete
    """

    OFF = enum.auto()
    FAST = enum.auto()
    ON = enum.auto()


class ForeignKeys(enum.Enum):
    """
    https://www.sqlite.org/pragma.html#pragma_foreign_keys
    """

    OFF = enum.auto()
    DEFERRED = enum.auto()
    IMMEDIATE = enum.auto()


class Synchronous(enum.Enum):
    """
    https://www.sqlite.org/pragma.html#pragma_synchronous
    """

    OFF = enum.auto()
    NORMAL = enum.auto()
    FULL = enum.auto()
    EXTRA = enum.auto()


class _OptionsMixin(abc.ABC):
    @abc.abstractmethod
    def convert_kwargs(self, kw: dict):
        ...

    @classmethod
    def new(cls, **kw):
        """Alternative constructor which automatically converts strings into enum values."""
        cls.convert_kwargs(kw)
        return cls(**kw)

    def evolve(self, **kw):
        """
        Make a copy of the current options block but with keyword arguments `**changes` applied to replace some of
        the attributes.
        """
        self.convert_kwargs(kw)
        return dc.replace(self, **kw)


def _convert_enum(d, k, enum_class):
    if isinstance(v := d.get(k), str):
        d[k] = enum_class[v]


@dc.dataclass(frozen=True, kw_only=True)
class Options(_OptionsMixin):
    """
    Represents the options that are applied to a SQLite database connection at the start of every transaction. These
    options are mostly in the form of "PRAGMA" statements.

    Use :meth:`new` as a convenient constructor that automatically resolves strings to enum values.

    Parameters
    ----------
    timeout:
        Number of seconds to wait when a table is locked. Set this to ``None`` if you are using your own custom
        busy handler via ``sqlite3_busy_handler``. See https://www.sqlite.org/c3ref/busy_timeout.html for more.
    begin:
        Controls the type of transaction. Use `DEFERRED` for read-only transactions and `IMMEDIATE` for read-write
        transactions.
    foreign_keys:
        Controls the enforcement of foreign keys.
    trusted_schema:
        Can we trust the database schema? Set this to False if the database file comes from an untrusted source. See
        https://www.sqlite.org/src/doc/latest/doc/trusted-schema.md for more information.
    recursive_triggers:
        Can the execution of a database trigger also cause the execution of another database trigger, and so on? This
        feature was added in SQLite in 2009, but it is turned off by default as it is a breaking change.
    schemas:
        Contains per-schema configuration options. See :class:`SchemaOptions`. You should have at least one entry for
        the `"main"` database.
    encoding:
        Encoding used for the text. Only a few values are supported https://www.sqlite.org/pragma.html#pragma_encoding
        and it can only be set on a brand new database.
    ignore_check_constraints:
        This option can be used to temporarily disable `CHECK` constraints.
    """

    timeout: float | int | None
    begin: Begin
    foreign_keys: ForeignKeys
    recursive_triggers: bool
    trusted_schema: bool
    schemas: immutabledict[str, SchemaOptions]
    encoding: str = "UTF-8"
    ignore_check_constraints: bool = False
    _cached_begin_commands = None

    @classmethod
    def get(cls, configurable) -> Options:
        """
        Return the options configured on engine or connection given in *configurable*. Raises KeyError if none is set.
        """
        return configurable.get_execution_options()["x_sqlite"]

    def apply(self, configurable):
        """Configure the engine or connection *configurable* to use this options object."""
        return configurable.execution_options(x_sqlite=self)

    def evolve_schema(self, schema_name: str, **changes):
        """
        Make a copy of the current options block but with keyword arguments `**changes` applied to
        :attr:`schemas[schema_name]` using :meth:`SchemaOptions.evolve`.
        """
        d = self.schemas
        return self.evolve(schemas=d | {schema_name: d[schema_name].evolve(**changes)})

    @classmethod
    def apply_lambda(cls, configurable, function: ty.Callable[[Options], Options]):
        """
        Get the current options for *configurable*, pass them to *function* to produce a new options object, then
        :meth:`apply` those options to *configurable*.
        """
        return function(cls.get(configurable)).apply(configurable)

    @staticmethod
    def convert_kwargs(kw):
        _convert_enum(kw, "begin", Begin)
        _convert_enum(kw, "foreign_keys", ForeignKeys)

        if (v := kw.get(k := "schemas")) is not None and not isinstance(v, immutabledict):
            kw[k] = immutabledict(v)

    def _cached_generate_begin_commands(self):
        if (r := self._cached_begin_commands) is None:
            object.__setattr__(self, "_cached_begin_commands", r := self._generate_begin_commands())
        return r

    def _generate_begin_commands(self):
        def sbool(x):
            return "1" if x else "0"

        if "'" in (encoding := self.encoding):
            raise ValueError("invalid character in encoding")

        r = [f"PRAGMA encoding='{encoding}'"]

        if (t := self.timeout) is not None:
            if t <= 0:
                t = -1
            elif (t := round(t * 1000)) < 1:
                t = 1
            r.append(f"PRAGMA busy_timeout={t:d}")

        for name, sch_opts in self.schemas.items():
            pre = f"PRAGMA {name}."
            if (x := sch_opts.journal) is not None:
                r.append(pre + "journal_mode=" + x.name)
            if (x := sch_opts.journal_size_limit) is not None:
                r.append(pre + "journal_size_limit=" + int(x))
            r += (
                pre + "synchronous=" + sch_opts.synchronous.name,
                pre + "secure_delete=" + sch_opts.secure_delete.name,
            )

        r += (
            "PRAGMA trusted_schema=" + sbool(self.trusted_schema),
            "PRAGMA recursive_triggers=" + sbool(self.recursive_triggers),
            "PRAGMA foreign_keys=" + sbool(self.foreign_keys != ForeignKeys.OFF),
            "PRAGMA ignore_check_constraints=" + sbool(self.ignore_check_constraints),
            "BEGIN " + self.begin.name,
        )

        if self.foreign_keys == ForeignKeys.DEFERRED:
            r.append("PRAGMA defer_foreign_keys=1")

        return tuple(r)


@dc.dataclass(frozen=True, kw_only=True)
class SchemaOptions(_OptionsMixin):
    """
    Options specific to one schema (one ATTACHed database file).

    Use :meth:`new` as a convenient constructor that automatically resolves strings to enum values.

    Parameters
    ----------
    synchronous:
        Higher levels are slower but provide more resilience to corruption in case of a sudden power failure or crash.
        Conversely, lower levels can be faster by orders of magnitude, at the cost of likely corruption in case of an
        unexpected power failure.
    journal:
        Journal mode. `WAL` is usually a good choice.
    journal_size_limit:
        The journal file may be left in place after a transaction ends, depending on your settings. To avoid it from
        taking up too much space, this option tells SQLite to trim down the journal file size down to
        `journal_size_limit` after the end of a transaction. Use `0` to trim it down to its minimum size. Use `-1` to
        allow it to grow unbounded.
    secure_delete:
        Controls the "overwrite with zeros" anti-forensic mechanism. Note that there are still some caveats, which you
        should read about at https://www.sqlite.org/pragma.html#pragma_secure_delete
    """

    synchronous: Synchronous
    journal: Journal | None = None
    journal_size_limit: int | None = None
    secure_delete: SecureDelete = SecureDelete.OFF

    @staticmethod
    def convert_kwargs(kw):
        _convert_enum(kw, "journal", Journal)
        _convert_enum(kw, "synchronous", Synchronous)
        _convert_enum(kw, "secure_delete", SecureDelete)


class SQLAlchemySqliteTransactionFix:
    """
    This class exists because sqlalchemy doesn't automatically fix pysqlite's stupid default behaviour. Additionally,
    we implement support for foreign keys.

    Use :class:`Options` to construct the options.

    https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
    """

    def register(self, engine):
        sa.event.listen(engine, "connect", self.event_connect)
        sa.event.listen(engine, "begin", self.event_begin)

    def event_connect(self, dbapi_connection, connection_record):
        # disable pysqlite's emitting of the BEGIN statement entirely.
        # also stops it from emitting COMMIT before any DDL.
        dbapi_connection.isolation_level = None

    def event_begin(self, conn):
        try:
            opts = Options.get(conn)
        except KeyError as exc:
            raise MissingExecutionOptionError(
                "You must configure your engine (or connection) execution options. "
                "For example:\n\n"
                "    engine = create_engine_sqlite(...)\n"
                "    engine_ro = Options.new(\n"
                "        timeout=0.5,\n"
                '        begin="DEFERRED",\n'
                '        foreign_keys="DEFERRED",\n'
                "        recursive_triggers=True,\n"
                "        trusted_schema=True,\n"
                '        schemas={"main": SchemaOptions.new(journal="WAL", synchronous="NORMAL")},\n'
                "    ).apply(engine)\n"
                '    engine_rw = Options.apply_lambda(engine_ro, lambda opt: opt.evolve(begin="IMMEDIATE"))'
            ) from exc

        # TODO: should we use the executescript method instead?
        for statement in opts._cached_generate_begin_commands():  # noqa
            conn.exec_driver_sql(statement).close()


@dc.dataclass
class Memory:
    """
    We keep a reference to an open connection because SQLite will free up the database otherwise.

    Note that you still can't get concurrent readers and writers because you cannot currently set WAL mode on an
    in-memory database. See https://sqlite.org/forum/info/6700ab1f9f6e8a00
    """

    uri: str = dc.field(init=False)
    connection_reference = None

    def __post_init__(self):
        self.uri = f"file:/sqlalchemy_boltons_memdb_{id(self)}"

    def as_uri(self):
        return self.uri


def sqlite_file_uri(path: Path | str | Memory, parameters: ty.Sequence[tuple[str | bytes, str | bytes]] = ()) -> str:
    if isinstance(path, str):
        path = Path(path)
    if isinstance(path, Path) and not path.is_absolute():
        path = path.absolute()

    qs = _up.urlencode(parameters, quote_via=_up.quote)
    qm = "?" if qs else ""
    return f"{path.as_uri()}{qm}{qs}"


def create_engine_sqlite(
    path: Path | str | Memory,
    *,
    parameters: ty.Iterable[tuple[str | bytes, str | bytes]] = (),
    check_same_thread: bool | None = False,
    create_engine_args: dict | None = None,
    create_engine: ty.Callable | None = None,
    transaction_fix: SQLAlchemySqliteTransactionFix | bool = True,
) -> sa.Engine:
    """
    Create a sqlite engine.

    Parameters
    ----------
    path: Path | str | Memory
        Path to the db file, or a :class:`Memory` object. The same memory object can be shared across multiple engines.
    parameters: ty.Sequence, optional
        SQLite URI query parameters as described in https://www.sqlite.org/uri.html
    check_same_thread: bool, optional
        Defaults to False. See https://docs.python.org/3/library/sqlite3.html#sqlite3.connect
    create_engine_args: dict, optional
        Keyword arguments to be passed to :func:`sa.create_engine`.
    create_engine: callable, optional
        If provided, this will be used instead of :func:`sa.create_engine`. You can use this to further customize
        the engine creation.
    transaction_fix: SQLAlchemySqliteTransactionFix | bool, optional
        See :class:`SQLAlchemySqliteTransactionFix`. If True, then instantiate one. If False, then do not apply the fix.
        (default: True)
    """

    parameters = list(parameters)
    if isinstance(path, Memory):
        parameters += (("vfs", "memdb"),)
    parameters.append(("uri", "true"))

    uri = sqlite_file_uri(path, parameters)

    if create_engine_args is None:
        create_engine_args = {}  # pragma: no cover

    # always default to QueuePool
    if (k := "poolclass") not in create_engine_args:
        create_engine_args[k] = sap.QueuePool
        if (k := "max_overflow") not in create_engine_args:
            # for SQLite it doesn't make sense to restrict the number of concurrent (read-only) connections
            create_engine_args["max_overflow"] = -1

    if (v := create_engine_args.get(k := "connect_args")) is None:
        create_engine_args[k] = v = {}
    if check_same_thread is not None:
        v["check_same_thread"] = check_same_thread

    # do not pass through poolclass=None
    if create_engine_args.get((k := "poolclass"), True) is None:
        create_engine_args.pop(k, None)  # pragma: no cover

    if create_engine is None:
        create_engine = sa.create_engine

    engine = create_engine("sqlite:///" + uri, **create_engine_args)

    if transaction_fix is True:
        transaction_fix = SQLAlchemySqliteTransactionFix()

    if transaction_fix:
        transaction_fix.register(engine)

    if isinstance(path, Memory):
        (conn := engine.raw_connection()).detach()

        # force the connection to actually happen
        conn.execute("SELECT 0 WHERE 0").close()

        path.connection_reference = conn

    return engine
