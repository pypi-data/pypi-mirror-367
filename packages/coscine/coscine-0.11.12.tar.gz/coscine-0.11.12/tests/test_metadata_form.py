import logging
from os import getenv
import coscine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

def main(fp):
    token = getenv("COSCINE_API_TOKEN")
    if not token:
        raise ValueError(
            "No Coscine API Token specified! "
            "Create a new environment variable with "
            "the name COSCINE_API_TOKEN!"
        )
    client = coscine.ApiClient(token)
    application_profiles = client.application_profiles()
    count = len(application_profiles)
    valid = 0
    invalid = 0
    for index, ap in enumerate(application_profiles):
        print(f"AP {index}/{count} {ap.uri}", file=fp)
        try:
            form = coscine.MetadataForm(client.application_profile(ap.uri))
            form.test()
            print(form, file=fp)
            is_valid = form.validate()
            print(f"Valid: {is_valid}", file=fp)
            valid += 1
        except Exception as ex:
            print(f"Valid: {False}", file=fp)
            print(ex, file=fp)
            invalid += 1
    print(f"Valid: {valid}", file=fp)
    print(f"Invalid: {invalid}", file=fp)
    print(f"Total: {count}", file=fp)

with open("test-metadata-form-results.txt", "w", encoding="utf-8") as fp:
    main(fp)
