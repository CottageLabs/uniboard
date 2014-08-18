from portality.models import Advert
from portality.scripts.adexpire import expire_email
from time import sleep

'''
Expected output:

advert 200
advert_expired@cottagelabs.com
expires_soon@cottagelabs.com
still_okay@cottagelabs.com
expires_soon@cottagelabs.com
advert_expired@cottagelabs.com delete

'''

def create_expired():
    advert = Advert()
    advert.set_owner('advert_expired@cottagelabs.com')
    advert.set_title('Hippy')
    advert.set_authors('Pony')
    advert.set_price(50)
    advert.set_expires('2008-07-07T00:00:00Z')
    advert.save()
    print advert.owner
    return advert

def create_soon_expiring():
    advert = Advert()
    advert.set_owner('expires_soon@cottagelabs.com')
    advert.set_title('Glug')
    advert.set_authors('Mug')
    advert.set_price(50)
    advert.set_expires('2014-08-18T00:00:00Z')
    advert.save()
    print advert.owner
    return advert

def create_still_okay():
    advert = Advert()
    advert.set_owner('still_okay@cottagelabs.com')
    advert.set_title('Foot')
    advert.set_authors('Feet')
    advert.set_price(50)
    advert.set_expires('2014-08-28T00:00:00Z')
    advert.save()
    print advert.owner
    return advert


expired = create_expired()
soon_expiring = create_soon_expiring()
still_okay = create_still_okay()
sleep(2)

expire_email(testing=True)

expired.delete()
soon_expiring.delete()
still_okay.delete()


