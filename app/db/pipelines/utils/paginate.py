class Pagination:
    def __init__(self) -> None: ...

    def paginate(self, query: list, skip: int = 0, limit: int = 10):
        """paginate cursor

        Args:
            query (list): query to be paginated
            skip (int): skip how many pages
            limit (int): limit 

        Returns:
            list: paginated cursor
        """
        self.query = query
        self.skip = skip
        self.limit = limit

        def build_query():
            return self.query + [
                {"$skip": self.skip},
                {"$limit": self.limit},
            ]

        return build_query()
