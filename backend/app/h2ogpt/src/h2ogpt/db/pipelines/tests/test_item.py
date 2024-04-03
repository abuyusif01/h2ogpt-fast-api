from app.h2ogpt.src.h2ogpt.db.pipelines.item import ItemPipeline


class Test_ItemPipeline:

    item = {
        "restaurants": [
            {
                "_id": 1,
                "name": "The Hungry Panda",
                "cuisine": "Chinese",
                "address": {
                    "street": "123 Main Street",
                    "city": "New York",
                    "state": "NY",
                    "zipcode": "10001",
                },
                "ratings": [4.5, 4.8, 4.2, 4.6],
            },
            {
                "_id": 2,
                "name": "Taco Haven",
                "cuisine": "Mexican",
                "address": {
                    "street": "456 Elm Street",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zipcode": "90001",
                },
                "ratings": [4.2, 4.4, 4.0, 4.3],
            },
            {
                "_id": 3,
                "name": "Pizza Palace",
                "cuisine": "Italian",
                "address": {
                    "street": "789 Oak Street",
                    "city": "Chicago",
                    "state": "IL",
                    "zipcode": "60601",
                },
                "ratings": [4.7, 4.9, 4.6, 4.8],
            },
        ],
        "books": [
            {
                "_id": 1,
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "genre": "Classic",
                "year": 1925,
            },
            {
                "_id": 2,
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "genre": "Fiction",
                "year": 1960,
            },
            {
                "_id": 3,
                "title": "1984",
                "author": "George Orwell",
                "genre": "Dystopian",
                "year": 1949,
            },
        ],
        "movies": [
            {
                "_id": 1,
                "title": "The Shawshank Redemption",
                "director": "Frank Darabont",
                "genre": "Drama",
                "year": 1994,
                "rating": 9.3,
            },
            {
                "_id": 2,
                "title": "The Godfather",
                "director": "Francis Ford Coppola",
                "genre": "Crime",
                "year": 1972,
                "rating": 9.2,
            },
            {
                "_id": 3,
                "title": "The Dark Knight",
                "director": "Christopher Nolan",
                "genre": "Action",
                "year": 2008,
                "rating": 9.0,
            },
        ],
    }

    def test_insert_item_pipeline(self):
        res = ItemPipeline().insert_one(self.item)
        assert res == self.item


    def test_items(self):
        res = ItemPipeline().items()
        assert isinstance(res, list)
        assert len(res) >= 1
        assert "restaurants" in res[0]
        assert "books" in res[0]
        assert "movies" in res[0]
        assert len(res[0]["restaurants"]) == 3

    
    def test_run(self):
        res = ItemPipeline().run
        assert res is not None


    
