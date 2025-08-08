# pyright: basic
# ruff: noqa

def test_example_1():
    from runtime.serialization.json import Serializer, serialize, deserialize
    from runtime.serialization import serializable
    from datetime import date

    @serializable(namespace="tests.examples")
    class Author:
        def __init__(self, name: str, birthday: date):
            self.__name = name
            self.__birthday = birthday

        @property
        def name(self) -> str:
            return self.__name

        @property
        def birthday(self) -> date:
            return self.__birthday

    @serializable(namespace="tests.examples")
    class Book:
        def __init__(self, title: str, author: Author):
            self.__title = title
            self.__author = author

        @property
        def title(self) -> str:
            return self.__title

        @property
        def author(self) -> Author:
            return self.__author

    author = Author("Stephen King", date(1947, 9, 21))
    book = Book("The Shining", author)
    serializer = Serializer[Book]()
    serialized = serializer.serialize(book) # -> {"author": {"birthday": "1947-09-21", "name": "Stephen King"}, "title": "The Shining"}
    deserialized = serializer.deserialize(serialized)
    assert deserialized.author.name == author.name
    assert deserialized.title == book.title

    # same result, different approach without the need for instantiating Serializer manually
    serialized = serialize(book, Book)

    # and without a base type, the type info is embedded
    serialized_untyped = serialize(book) # -> {"author": {"birthday": "1947-09-21", "name": "Stephen King"}, "title": "The Shining", "~type": "tests.examples.Book"}
    deserialized_untyped = deserialize(serialized_untyped)
    assert deserialized_untyped.author.name == deserialized.author.name
    assert deserialized_untyped.title == deserialized.title

