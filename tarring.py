import tarfile

def compress(tarFile: str, members: list[str]) -> None:
    with tarfile.open(tarFile, mode="w:gz") as tar:
        for member in members:
            tar.add(member)

def decompress(tarFile: str, path: str) -> None:
    with tarfile.open(tarFile, mode="r:gz") as tar:
        members = tar.getmembers()
        for member in members:
            tar.extract(member, path=path)