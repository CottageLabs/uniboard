from portality.models import Account

if __name__ == "__main__":
    import argparse, getpass
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email", help="email address of user to make admin")
    args = parser.parse_args()

    if not args.email:
        print "Please specify an email with the -e option"
        exit()

    email = args.email

    acc = Account.pull(email)
    if not acc:
        print "Account with email " + email + " does not exist"
    current_roles = acc.role
    if "admin" not in current_roles:
        acc.set_role(current_roles + ["admin"])
        acc.save()