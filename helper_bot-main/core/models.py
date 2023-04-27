import datetime

import attrs


@attrs.define(kw_only=True)
class TagData:
    name: str
    id: int
    content: str
    owner_id: int
    created_at: datetime.datetime


@attrs.define(kw_only=True)
class WarnData:
    id: int
    mod_id: int
    user_id: int
    reason: str
    created_at: datetime.datetime
