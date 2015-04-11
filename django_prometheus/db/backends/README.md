# Adding new database wrapper types

Unfortunately, I don't have the resources to create wrappers for all
database vendors. Doing so should be straightforward, but testing that
it works and maintaining it is a lot of busywork, or is impossible for
me for commercial databases.

This document should be enough for people who wish to implement a new
database wrapper.

## Structure

A database engine in Django requires 3 classes (it really requires 2,
but the 3rd one is required for our purposes):

* A DatabaseFeatures class, which describes what features the database
  supports. For our usage, we can simply extend the existing
  DatabaseFeatures class without any changes.
* A DatabaseWrapper class, which abstracts the interface to the
  database.
* A CursorWrapper class, which abstracts the interface to a cursor. A
  cursor is the object that can execute SQL statements via an open
  connection.

An easy example can be found in the sqlite3 module. Here are a few tips:

* The `self.alias` and `self.vendor` properties are present in all
  DatabaseWrappers.
* The CursorWrapper doesn't have access to the alias and vendor, so we
  generate the class in a function that accepts them as arguments.
* Most methods you overload should just increment a counter, forward
  all arguments to the original method and return the
  result. `execute` and `execute_many` should also wrap the call to
  the parent method in a `try...except` block to increment the
  `errors_total` counter as appropriate.
