import requests


def isbn_lookup(isbn):
    isbn = str(isbn)
    isbn = ''.join(c for c in isbn if c.isdigit())
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn
    book_google = requests.get(url)
    book_google = book_google.json()
    if book_google['totalItems'] != 1:
        book = {}
        return book

    book = {}
    book_google_info = book_google["items"][0]["volumeInfo"]

    book["title"] = book_google_info["title"] if "title" in book_google_info else None
    book["authors"] = book_google_info["authors"] if "authors" in book_google_info else None
    book["publisher"] = book_google_info["publisher"] if "publisher" in book_google_info else None
    book["subjects"] = book_google_info["categories"] if "categories" in book_google_info else None
    book["isbn"] = book_google_info["industryIdentifiers"] if "industryIdentifiers" in book_google_info else None
    book["image"] = book_google_info["imageLinks"]["thumbnail"] if "imageLinks" in book_google_info and "thumbnail" in book_google_info["imageLinks"] else None

    if "publishedDate" in book_google_info:
        year = book_google["items"][0]["volumeInfo"]["publishedDate"]
        year = year[0:4]
        try:
            year = int(year)
        except ValueError as e:
            year = None
        book["year"] = year
    else:
        book["year"] = None

    return book



