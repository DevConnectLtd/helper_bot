import datetime

import attrs


@attrs.define(kw_only=True)
class TagData:
    name: str
    id: int
    content: str
    owner_id: str
    created_at: datetime.datetime
