from portality.models import Advert
from portality.scripts.adexpire import expire_email
from time import sleep
from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

'''
Expected output:

advert 200  # you may not get this if you've already run the app, it's just the type being created in ES
advert_expired@cottagelabs.com
expires_soon@cottagelabs.com
still_okay@cottagelabs.com
expires_soon@cottagelabs.com
advert_expired@cottagelabs.com delete

'''

def create_deactivated():
    advert = Advert()
    advert.set_owner('advert_deactivated@cottagelabs.com')
    advert.set_title('Hippy')
    advert.set_authors('Pony')
    advert.set_price(50)
    advert.set_expires((datetime.now() - timedelta(days=365)).strftime(DATE_FORMAT))
    advert.mark_deactivated()
    advert.save()
    print advert.owner
    return advert

def create_expired():
    advert = Advert()
    advert.set_owner('advert_expired@cottagelabs.com')
    advert.set_title('Hippy')
    advert.set_authors('Pony')
    advert.set_price(50)
    advert.set_expires((datetime.now() - timedelta(days=365)).strftime(DATE_FORMAT))
    advert.save()
    print advert.owner
    return advert

def create_soon_expiring():
    advert = Advert()
    advert.set_owner('expires_soon@cottagelabs.com')
    advert.set_title('Glug')
    advert.set_authors('Mug')
    advert.set_price(50)
    advert.set_expires((datetime.now() + timedelta(hours=36)).strftime(DATE_FORMAT))
    advert.save()
    print advert.owner
    return advert

def create_still_okay():
    advert = Advert()
    advert.set_owner('still_okay@cottagelabs.com')
    advert.set_title('Foot')
    advert.set_authors('Feet')
    advert.set_price(50)
    advert.set_expires((datetime.now() + timedelta(days=365)).strftime(DATE_FORMAT))
    advert.save()
    print advert.owner
    return advert


expired = create_expired()
soon_expiring = create_soon_expiring()
still_okay = create_still_okay()
deleted = create_deactivated()
sleep(2)

expire_email(testing=True)

expired.delete()
soon_expiring.delete()
still_okay.delete()


