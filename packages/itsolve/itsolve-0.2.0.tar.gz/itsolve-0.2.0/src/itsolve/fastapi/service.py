from .repository import Repository


class RepoTypeError(Exception):
    pass


class Service[IRepo]:
    repo: IRepo

    def __init__(self, repo: IRepo) -> None:
        if not isinstance(repo, Repository):
            raise RepoTypeError
        self.repo = repo
