import requests


def isbn_lookup(isbn):
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + str(isbn)
    book = requests.get(url)
    book = book.json()
    if book['totalItems'] == 0 or book['totalItems'] > 1:
        book = {}
        return book
    else:
        return book


