from types import SimpleNamespace


class HashableSimpleNamespace(SimpleNamespace):
    def __hash__(self) -> int:  # type: ignore[override]
        return hash(str(self.__dict__.values()))


def get_mocked_projects(num_of_projects: int) -> list[HashableSimpleNamespace]:
    return [
        HashableSimpleNamespace(id=i, name=f"test_project_{i}", web_url=f"https://test_project_{i}")
        for i in range(num_of_projects)
    ]
