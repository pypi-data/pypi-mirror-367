from pydantic import BaseModel


class Torrent(BaseModel):
    id: int
    filename: str
    category: str
    size: str
    seeders: int
    leechers: int
    downloads: int | None = None
    date: str
    magnet_link: str | None = None

    def __str__(self) -> str:
        return str(self.model_dump(exclude_unset=True, exclude_none=True))
