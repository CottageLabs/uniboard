from portality.models import Advert
from portality.core import app
from portality import util

def expire_email():
    for item in Advert.get_by_expiration():
        if item.is_expired:
            print item.owner + " delete"
            item.mark_deactivated(True)
        else:
            print item.owner
            activation_link = app.config['LOCALHOST_URL'] + "/advert/" + item.id + "/reactivate"
            to = [item.owner, app.config['ADMIN_EMAIL']]
            fro = app.config['ADMIN_EMAIL']
            subject = app.config.get("SERVICE_NAME", "") + item.title + " - expires soon"
            text = "Hello, " + item.owner + "!\n\n"
            text += "Your advert " + item.title + " expires soon."
            text += "Please visit " + activation_link + " if you want to keep it up for another week.\n\n"
            text += "Regards, The UniBoard Team"

            util.send_mail(to=to, fro=fro, subject=subject, text=text)

expire_email()