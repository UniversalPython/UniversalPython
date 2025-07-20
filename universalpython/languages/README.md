## Adding a new language

- Simply make a new folder here with the **two-letter** language code of your language.
For example, German is `de`, Korean is `ko`. You can find yours [here](https://www.iban.com/country-codes).

Make sure it's in lowercase!

- In that folder, add two files:
  - An empty `__init__.py` (this makes it packageable with the rest of the languages). You don't need to add anything inside!
  - A `default.yaml` file which contains the mappings of the language. You can take [this one](./de/default.yaml) as a base template. 

## Editing an existing language

Simply edit the `default.yaml` of your preferred language. We currently don't have versioning or automated-human-testing involved, so it's more of an honor system.