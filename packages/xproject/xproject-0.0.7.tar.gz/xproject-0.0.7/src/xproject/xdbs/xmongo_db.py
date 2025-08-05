from typing import Any, Self
from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.synchronous.database import Database

from xproject.xdbs.xdb import DB


class MongoDB(DB):
    def __init__(
            self,
            *args: Any,
            host: str = "localhost",
            port: int = 27017,
            username: str | None = None,
            password: str | None = None,
            uri: str | None = None,
            dbname: str,
            **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.uri = uri
        self.dbname = dbname

        self._client: MongoClient | None = None
        self._db: Database | None = None

    def _open(self) -> None:
        if self.uri is not None:
            uri = self.uri
        else:
            if self.username is not None and self.password is not None:
                uri = "mongodb://%s:%s@%s:%s" % (
                    quote_plus(self.username), quote_plus(self.password), self.host, self.port
                )
            else:
                uri = "mongodb://%s:%s" % (self.host, self.port)

        self._client = MongoClient(uri)
        self._db = self._client[self.dbname]

    def _close(self) -> None:
        self._db = None

        self._client.close()
        self._client = None

    @classmethod
    def from_uri(cls, uri: str, dbname: str) -> Self:
        ins = super().from_uri(**dict(uri=uri, dbname=dbname))
        return ins
