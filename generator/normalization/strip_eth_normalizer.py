class StripEthNormalizer:
    def __init__(self, config):
        pass

    def normalize(self, name: str) -> str:
        return name[:-4] if name.endswith('.eth') else name