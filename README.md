# tmdb_helper
A simple tool to help editing movies on tmdb - lists those with empty fields and compares to imdb

You will create a list of movies on TMDB and this script looks for missing stuff. It has read-only access to TMDB - so you will not break
anything.

## Installation

You need python 2
`pip install --user -r requirements.txt`
Copy config.example.py to config.py
Request an API-key from tmdb.
Enter your list-id into the config


## Example Output
```
Movie has a problem:
    Love: Yeu  -  Yêu (2015)    http://themoviedb.org/movie/390381
    * language does not contain vietnamese
    * no backdrop - http://themoviedb.org/movie/390381/images/backdrops
    *    https://www.google.de/search?q=Y%C3%AAu+2015&safe=off&biw=1920&bih=1080&tbm=isch
    * no runtime
    * tmdb has this extra actor Lâm Thanh Mỹ (7!) nm6652333 as Little Nhi http://themoviedb.org/person/1450858
Movie has a problem:
    Beauty in Each Centimeter  -  Đẹp Từng Centimet (2009)    http://themoviedb.org/movie/44024
    * no imdb
Movie has a problem:
    Truy Sát (2016)    http://themoviedb.org/movie/408165
    * no runtime
    *   -> [u'90']
    * imdb has this extra actor Maria Tran as Phuong Lua (28!) http://imdb.com/name/nm3489824
    * imdb has this extra actor Truong Ngoc Anh as An (10!) http://imdb.com/name/nm1846416
    * imdb has this extra actor Lamou Vissay as Loc Soi (10!) http://imdb.com/name/nm2663086
Movie has a problem:
    Bảo Mẫu Siêu Quậy (2015)    http://themoviedb.org/movie/380377
    * no director
    * no genre
    * no imdb
```

## Why is tmdb3 bundled?

The code is not developed anymore and small things did not work - see in the commit 971b3f844a7b20636e75ba44db0d05f4d92cf775

## Contributing

Please write an email if you want to work on this code and I'll add you to the developers.
