def ez_options(timeout, begin, foreign_keys, journal):
    from sqlalchemy_boltons import sqlite as _sq

    return _sq.Options.new(
        timeout=timeout,
        begin=begin,
        foreign_keys=foreign_keys,
        recursive_triggers=True,
        trusted_schema=True,
        schemas={"main": _sq.SchemaOptions.new(journal=journal, synchronous="FULL")},
    )
