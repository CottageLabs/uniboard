from random import randint, random
from portality import models
import numpy

owners = ["richard@cottagelabs.com"]

titlewords = ["Adult", "Aeroplane", "Air", "Aircraft Carrier", "Airforce", "Airport", "Album", "Alphabet", "Apple", "Arm", "Army",
              "Baby", "Baby", "Backpack", "Balloon", "Banana", "Bank", "Barbecue", "Bathroom", "Bathtub", "Bed", "Bed", "Bee",
              "Bible", "Bible", "Bird", "Bomb", "Book", "Boss", "Bottle", "Bowl", "Box", "Boy", "Brain", "Bridge", "Butterfly",
              "Button", "Cappuccino", "Car", "Car-race", "Carpet", "Carrot", "Cave", "Chair", "Chess Board", "Chief", "Child",
              "Chisel", "Chocolates", "Church", "Church", "Circle", "Circus", "Circus", "Clock", "Clown", "Coffee", "Coffee-shop",
              "Comet", "Compact Disc", "Compass", "Computer", "Crystal", "Cup", "Cycle", "Data Base", "Desk", "Diamond", "Dress",
              "Drill", "Drink", "Drum", "Dung", "Ears", "Earth", "Egg", "Electricity", "Elephant", "Eraser", "Explosive", "Eyes",
              "Family", "Fan", "Feather", "Festival", "Film", "Finger", "Fire", "Floodlight", "Flower", "Foot", "Fork", "Freeway",
              "Fruit", "Fungus", "Game", "Garden", "Gas", "Gate", "Gemstone", "Girl", "Gloves", "God", "Grapes", "Guitar",
              "Hammer", "Hat", "Hieroglyph", "Highway", "Horoscope", "Horse", "Hose", "Ice", "Ice-cream", "Insect", "Jet fighter",
              "Junk", "Kaleidoscope", "Kitchen", "Knife", "Leather jacket", "Leg", "Library", "Liquid", "Magnet", "Man",
              "Map", "Maze", "Meat", "Meteor", "Microscope", "Milk", "Milkshake", "Mist", "Money $$$$", "Monster", "Mosquito",
              "Mouth", "Nail", "Navy", "Necklace", "Needle", "Onion", "PaintBrush", "Pants", "Parachute", "Passport", "Pebble",
              "Pendulum", "Pepper", "Perfume", "Pillow", "Plane", "Planet", "Pocket", "Post-office", "Potato", "Printer",
              "Prison", "Pyramid", "Radar", "Rainbow", "Record", "Restaurant", "Rifle", "Ring", "Robot", "Rock", "Rocket",
              "Roof", "Room", "Rope", "Saddle", "Salt", "Sandpaper", "Sandwich", "Satellite", "School", "Sex", "Ship", "Shoes",
              "Shop", "Shower", "Signature", "Skeleton", "Slave", "Snail", "Software", "Solid", "Space Shuttle", "Spectrum",
              "Sphere", "Spice", "Spiral", "Spoon", "Sports-car", "Spot Light", "Square", "Staircase", "Star", "Stomach",
              "Sun", "Sunglasses", "Surveyor", "Swimming Pool", "Sword", "Table", "Tapestry", "Teeth", "Telescope", "Television",
              "Tennis racquet", "Thermometer", "Tiger", "Toilet", "Tongue", "Torch", "Torpedo", "Train", "Treadmill", "Triangle",
              "Tunnel", "Typewriter", "Umbrella", "Vacuum", "Vampire", "Videotape", "Vulture", "Water", "Weapon", "Web",
              "Wheelchair", "Window", "Woman", "Worm", "X-ray"]

names = ["Rosina Boose", "Linwood Gilkison", "Lizette Lobel", "Gino Bracken", "Galen Eddington", "Yukiko Plant", "Janita Cleland",
         "Allen Mansour", "Illa Bulter", "Maxine Jaimes", "Clemencia Song", "Sherron Shiflet", "Vincenza Grondin", "Kandi Naber",
         "Sarita Defilippo", "Adele Luebke", "Shenita Bartow", "Ngan Mcnealy", "Kenia Spadoni", "Zane Degner", "Hosea Maberry",
         "Maryjane Alarcon", "Harlan Borowski", "Cortney Archuleta", "Lazaro Herzog", "Willian Mcnab", "Mitsuko Kearney",
         "Hae Marston", "Dale Condrey", "Aletha Viveros", "Nery Houchens", "Melodee Grell", "Chad Woosley", "Bao Spanbauer",
         "Rosendo Galati", "Elinor Merrow", "Ebonie Auerbach", "Marcus Vigil", "Shizue Waldorf", "Domenica Rickles", "Lajuana Barrios",
         "Jacquelyn Astle", "Malika Holte", "Isobel Goldberg", "Yan Huson", "Jefferey Lo", "Tory Cassinelli", "Hedwig Bjerke",
         "Mariam Leisinger", "Emery Beegle"]

numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

num_suffix = ["st", "nd", "rd", "th"]

publishers = ["Abilene Christian University Press", "Ace Books \u2013 an imprint of Penguin Group",
              "Addison\u2013Wesley \u2013 an imprint of Pearson Education", "Akashic Books \u2013 independent small press; known for its noir series",
              "Allen & Unwin", "Andr\u00e9 Deutsch \u2013 an imprint of the Carlton Publishing Group", "Anova Books",
              "Applewood Books", "Arbor House", "Arcade Publishing", "Airiti Press \u2013 an imprint of Airiti Inc",
              "Armida Publications", "A. S. Barnes \u2013 founded by Alfred Smith Barnes",
              "Atheneum Books \u2013 a children's fiction imprint of Simon & Schuster", "Atlantic Books",
              "ATOM Books \u2013 a UK-based imprint of Little, Brown", "Aunt Lute Books \u2013 feminist publisher (US)", "B & W Publishing",
              "Baker Book House", "Barrie & Jenkins", "Ballantine Books", "Bantam Spectra \u2013 specialist Sci-Fi imprint of Bantam Books",
              "Belknap Press", "Bellevue Literary Press", "Berkley Books \u2013 an imprint of Penguin Group (USA)", "Bison Books",
              "Black Dog Publishing", "Black Sparrow Books", "Blackwell Publishing", "Bloodaxe Books",
              "Blue Ribbon Books, Garden City, New York \u2013 American publisher", "Book League of America",
              "Borgo Press \u2013 an imprint of Wildside Press", "Bowes & Bowes", "Boydell & Brewer", "Breslov Research Institute",
              "Brimstone Press \u2013 Australian dark-fiction publisher", "Butterworth-Heinemann \u2013 UK-based imprint of Elsevier",
              "Cambridge University Press UK", "Canongate Books", "Carlton Books UK", "Carnegie Mellon University Press", "Cassell",
              "Central European University Press", "Chambers Harrap", "Chatto and Windus", "Chronicle Books", "City Lights Publishers.",
              "Cloverdale Corporation", "Collector's Guide Publishing", "Columbia University Press",
              "Constable & Co Ltd \u2013 now part of Constable & Robinson", "Copper Canyon Press", "Cornell University Press",
              "Craftsman Book Company", "Crocker & Brewster", "Da Capo Press \u2013 imprint of Perseus Books Group",
              "Dalkey Archive Press \u2013 a small fiction publisher based in Urbana, Illinois", "Dar Lila (Kayan Corp) \u2013, Egypt",
              "DAW Books \u2013 science-fiction and fantasy imprint founded by Donald A. Wollheim (D.A.W.)",
              "Del Rey Books \u2013 a fantasy genre imprint o", "J. M. Dent", "Directmedia Publishing", "Dodd, Mead and Company",
              "Dorling", "Douglas & ", "Dover Publications", "E. P. Dutton \u2013 split into two imprints; now part of Penguin Group",
              "Earthscan pub", "Ee", "Ellora's Cave", "Emerald Group Publishing", "Ewha Womans Univer", "FabJob", "Farrar, Str",
              "Felon", "Flux \u2013 an imprint of Llewellyn Worldwid", "Folio Society", "Four Courts ", "Free Press", "Frede",
              "Funk & Wagnalls", "Gaspereau Press", "George Newnes", "George Routledge & Sons \u2013 on", "Good News Publishers",
              "Goose Lane Editions", "Grafton", "Greenery Press", "Greenwood Publishing Group", "Grosset & Dunlap \u2013 an imprint of Penguin Group",
              "Hachette Book Group USA", "Happy House \u2013 a part of Darakwon Press", "Harcour", "Harlequin ",
              "Harper & Row \u2013 also now part of HarperCollins", "HarperPrism \u2013 ", "Harry N. Abrams,", "Harvest House",
              "Hawthorne Books", "Haynes Manuals (UK)", "Herbert J", "Hodder & St", "Hogarth", "Holt McDougal", "Houghton Mifflin",
              "The House of", "Humana Pres", "Hyperion"]

lcc = ["General Works", "Philosophy. Psychology. Religion", "Auxiliary Sciences Of History",
       "World History And History Of Europe, Asia, Africa, Australia, New Zealand, Etc.", "History Of The Americas",
       "History Of The Americas", "Geography. Anthropology. Recreation", "Social Sciences", "Political Science", "Law",
       "Education", "Music And Books On Music", "Fine Arts", "Language And Literature", "Science", "Medicine", "Agriculture",
       "Technology", "Military Science", "Naval Science", "Bibliography. Library Science. Information Resources (General)"]

conditions = ["As New", "Very Good", "Good", "Fair", "Poor"]

tags = ["superserviceableness", "michigan", "atabalipa", "prespeculating", "goateed", "unsagacious", "saman", "subtetanic",
        "famacide", "lithosere", "sidestick", "tychistic", "subattenuate", "unsensed", "overmilitaristic", "utu", "daman",
        "wisenheimer", "became", "burglariously", "tarlatan", "angelic", "enolizing", "relevant", "deconcentrate", "telchines",
        "speedful", "sapid", "contaminating", "keyman", "ululant", "alkahestical", "mtwara", "preinhere", "choppiest",
        "custodial", "relaunder", "unleaf", "anacusia", "precipice", "belligerent", "racemization", "pergamum", "cumberland",
        "reincorporating", "negationist", "nonresistance", "nonaddicting", "overinvestment", "puerilism"]

coords = {
    "lat" : 51.533182,
    "lon" : -0.475996,
    "scale" : 0.035
}

def _random(length, from_list, separator="", aslist=False):
    result = []
    for i in range(length):
        pick = randint(0, len(from_list) - 1)
        result.append(from_list[pick])
    if not aslist:
        return separator.join(result)
    else:
        return result

def owner():
    return _random(1, owners)

def isbn(length=10):
    return _random(length, numbers)

def title():
    length = randint(2, 5)
    return _random(length, titlewords, " ")

def edition():
    ed = randint(1, 15)
    ns = _random(1, num_suffix)
    return str(ed) + ns

def authors():
    length = randint(1, 4)
    return _random(length, names, ", ")

def year():
    return randint(1970, 2014)

def publisher():
    return _random(1, publishers)

def subjects():
    length = randint(1, 3)
    return _random(length, lcc, aslist=True)

def condition():
    return _random(1, conditions)

def lat_lon():
    offset = numpy.random.normal(scale=coords["scale"])
    lat = coords["lat"] + offset
    lon = coords["lon"] + offset
    return lat, lon

def keywords():
    length = randint(1, 6)
    return _random(length, tags, aslist=True)

def price():
    major = randint(1, 70)
    minor = _random(2, numbers)
    return str(major) + "." + minor

def generate_record():
    """
    {
        "id" : "<opaque identifier for the advert>",
        "owner" : "<user who created the ad>",
        "isbn" : ["<isbn-10>", "<isbn-13>"],
        "title" : "<book title>",
        "edition" : "<edition of book>",
        "authors" : "<authors>",
        "year" : <year of publication>,
        "publisher" : "<publisher of book>",
        "image_id" : "<id of book image in image library>",
        "subject" : ["<subject classification>"],
        "condition" : "<condition of the book>",
        "loc" : {
            "lat" : <latitude>,
            "lon" : <longitude>
        },
        "keywords" : ["<keyword>"],
        "price" : <price in GBP>,
        "admin" : {
            "deleted" : True/False,
            "reactivate_token" : "<reactivate token>",
            "reactivate_expires" : "<ractivate token expiration timestamp>",
            "expires" : "<date the advert expires>",
            "abuse" : <number of times abuse reported>
        },
        "created_date" : "<date advert was created>",
        "last_updated" : "<date advert was last modified>",
    }
    """
    ad = models.Advert()
    ad.set_owner(owner())
    ad.add_isbn(isbn(10))
    ad.add_isbn(isbn(13))
    ad.set_title(title())
    ad.set_edition(edition())
    ad.set_authors(authors())
    ad.set_year(year())
    ad.set_publisher(publisher())
    ad.set_subjects(subjects())
    ad.set_condition(condition())
    ad.set_location(*lat_lon())
    ad.set_keywords(keywords())
    ad.set_price(price())
    ad.save()

if __name__ == "__main__":
    for i in range(100):
        generate_record()