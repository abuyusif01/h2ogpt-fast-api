from db.pipelines.utils.paginate import Pagination
from db.pipelines.utils.cursor import Cursor


class Test_H2ogptUtils:

    def test_paginate(self):
        query = []
        skip = 0
        limit = 10
        expected_result = [{"$skip": 0}, {"$limit": 10}]

        assert isinstance(Pagination().paginate(query, skip, limit), list)
        assert Pagination().paginate(query, skip, limit) == expected_result
        assert Pagination().paginate(query, skip, limit) != None

    def test_cursor(self):
        import os

        assert isinstance(Cursor(), object)
        assert Cursor().port == os.getenv("MONGO_PORT")
        assert Cursor().host == os.getenv("MONGO_HOST")
        assert Cursor().user == os.getenv("MONGO_USER")
        assert Cursor().passwd == os.getenv("MONGO_PASS")
