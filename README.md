# animedb

A personal anime tracker with statically generated web displays.

Thought up during MAL's sudden and unusual hiatus in which they forced every user account to reset their password and denied access to their service for days. As of writing this no explanation was given other than a potential exploit in their API. This really isn't good enough.

I want a personalised way of displaying my anime history and progress without relying on a third party being online. 

[Live example](http://anime.danieljon.es)

# project goals

* single user, this is not a community tracker 
* static webpages generated with scripts
* no javascript, php or cgi (html and css web pages only)
* usable on mobile and browser
* display anime with information about it (name, year created, rating, genre, number of episodes etc))
* display user rating, episodes watched, personal notes etc)
* source information from MAL API (maybe others, I don't know of any) or allow the user to enter it manually
* sqlite database to hold the information
* provide easy to use cli tool to update/add anime, episodes, rating, notes etc
* no servers, all edits to the database will be local
* provide filters (highest/lowest score first, date created, watch status (watching, finished, on hold etc)
  * these will be generated html pages
* script to import anime from MAL profiles (maybe others, again I don't know any personally)
  * possibly using exported XML data instead of API
