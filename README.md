# Messy

Hello.

You can retrieve the code for this project (and see this README nicely formatted) from [GitHub](https://github.com/LorenDavie/sturdy-octo-succotash).

The problem, as I read it, dealt with a large dataset, being manipulated by a modest server. So I decided to build the application structure in a fairly scalable way, so that the processing and memory load on the server could stay relatively flat. If there is a lot of traffic on it, it could be scaled horizontally by adding servers in a cluster.

One of the main techniques I used was to keep database reads and writes out of the request/response cycle. You can always add app servers, but database activity remains a hotspot, so I tried to ensure that only async tasks (that can be throttled) would access the database.

So this should scale. I'm not sure if it's overkill for what you were looking for, but this is an approach I might use to building a high-throughput app.

Thanks,

Loren

## Running Locally

> Note: An app like this could really benefit from Docker and Docker-Compose, but in the interests of time I've left you with a slightly more complicated set up.

Setup instructions are for OS X. I make the assumption that you have Homebrew, Virtualenv and Pip on your machine.

### Pre-Requisites

1. Install PostgreSQL. `brew install postgresql`. (SQLite will not work, because I'm using queries with DISTICT clauses).
2. Install Redis `brew install redis`. This is the back end for Celery.
3. Install Memcached `brew install memcached`. We're using memcached to pass some info around, and the local memory cache won't work.

You will also need working AWS credentials.

### Installation

1. Create virtual env: `cd <project-dir>; virtualenv --no-site-packages env`.
2. Pick up the environment: `source env/bin/activate`
3. Install packages: `pip install -r requirements.txt`
4. Environment file: `cp local.sh.template local.sh`
5. Set the following values in `local.sh`:
    * MESSY_BUCKET: The name of the AWS S3 bucket to use. Defaults to `messystats`.
    * MESSY_KEY: The key for the stats JSON blob, stored in the bucket. Defaults to `messystats_key`.
    * AWS_ACCESS_KEY_ID: The access key for your AWS account.
    * AWS_SECRET_ACCESS_KEY: The secret key for your AWS account.
    * REDIS_URL: The URL to your Redis server. Will default to localhost.
6. Run migrations: `./runmigrations.sh`.

### Running the App

You will need FOUR terminal windows, unless you want to modify the startup scripts to use daemon mode. In the interest of time...

1. Terminal window 1: `memcached`.
2. Terminal window 2: `./runworker.sh`.
3. Terminal window 3: `./runbeat.sh`
4. Terminal window 4: `./runserver.sh`

### Writing Messages

Access [http://localhost:8000/message/write/?username=Fred&city=New+York&state=NY&message=Yo+what+up!](http://localhost:8000/message/write/?username=Fred&city=New+York&state=NY&message=Yo+what+up!). Try playing with the arguments to create some different data.  It will accept both a POST and a GET. (I know the GET isn't RESTful in this case, but it's easier to demo. I'd probably just want to accept a POST in production.)

Note that your request does not directly cause a db write. Instead it stuffs your message into memcached, and then launches an async job to do the write.

Possible improvement: You can still flood the message queue with enough traffic, so I might switch the celery task to a periodic task that pulls all of the messages sunk into memcached, instead of launching a task per http request.

### Getting Stats

As specified, access [http://localhost:8000/stat/get/](http://localhost:8000/stat/get/).

This will send you on a redirect to an S3 bucket, that holds the JSON blob. The data in the bucket is regenerated once per minute, meaning if you just entered a bunch of messages, you'll need to wait up to a minute to see them reflected in the stats. This is the price we pay for scalability, but it's probably acceptable in these kinds of dashboard applications.

Make sure to give the app a minute to run the periodic task at least once before hitting this URL, or you'll find your bucket will be empty.

### Notes

* Renaming `Messages` model to `Message`. Typical Django convention is to have models named in the singular, unless they actually represent an aggregation of something on a per-record basis.
* Removing capitalization of field verbose names.  As per [documentation](https://docs.djangoproject.com/en/1.9/topics/db/models/#verbose-field-names): "The convention is not to capitalize the first letter of the verbose_name. Django will automatically capitalize the first letter where it needs to."
* Not using class-based views on purpose. They over-complicate something easily done with a function view. (Frankly, not totally sold on class based views in general.)
