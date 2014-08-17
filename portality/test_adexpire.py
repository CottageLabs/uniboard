from portality.models import Advert

def create_expired():
    advert = Advert()
    advert.set_owner('test@cottagelabs.com')
    advert.set_title('Hippy')
    advert.set_authors('Pony')
    advert.set_price(50)
    advert.set_expires('2008-07-07T00:00:00Z')
    advert.save()
    print advert.owner
    return advert

def create_soon_expiring():
    advert = Advert()
    advert.set_owner('test@cottagelabs.com')
    advert.set_title('Glug')
    advert.set_authors('Mug')
    advert.set_price(50)
    advert.set_expires('2014-08-18T00:00:00Z')
    advert.save()
    print advert.owner
    return advert

def create_still_okay():
    advert = Advert()
    advert.set_owner('test@cottagelabs.com')
    advert.set_title('Foot')
    advert.set_authors('Feet')
    advert.set_price(50)
    advert.expires_in(220)
    advert.save()
    print advert.owner
    return advert

create_expired()
create_soon_expiring()
create_still_okay()