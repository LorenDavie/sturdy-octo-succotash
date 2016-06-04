# sturdy-octo-succotash


### Notes

* Renaming `Messages` model to `Message`. Typical Django convention is to have models named in the singular, unless they actually represent an aggregation of something on a per-record basis.
* Removing capitalization of field verbose names.  As per [documentation](https://docs.djangoproject.com/en/1.9/topics/db/models/#verbose-field-names): "The convention is not to capitalize the first letter of the verbose_name. Django will automatically capitalize the first letter where it needs to."
* Not using class-based views on purpose. They over-complicate something easily done with a function view. (Frankly, not totally sold on class based views in general.)
* Must create setting MESSY_BUCKET to identify the S3 bucket that will be used.
* Must create settings MESSY_KEY to identify the S3 key where stats info is stored.