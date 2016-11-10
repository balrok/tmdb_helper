# -*- coding: utf-8 -*-
from tmdb3 import List
from imdb_helper import getImdbObject
from imdb_helper import Person as iPerson


class Person(object):
    def __init__(self, per):
        self.id = per.id
        self.birthplace = per.birthplace
        self.imdb_id = per.imdb_id
        self.name = per.name
        self.gender = per.gender
        self.dayofbirth = per.dayofbirth
        #self.deathday = per.deathday
        self.profile = per.profile
        self.aliases = per.aliases
        try:
            self.job = per.job
        except:
            self.job = ""
        try:
            self.character = per.character
        except:
            self.character = ""
        self.crew = []
        if hasattr(per, "crew"):
            self.crew = per.crew
        self.cast = []
        if hasattr(per, "cast"):
            self.cast = per.cast
        self.roles = []
        if hasattr(per, "roles"):
            self.roles = per.roles
        self.per = per

    def countMovies(self):
        # TODO only writer,director,cinematography and sound is interesting
        c = len(self.crew)
        c += len(self.roles)
        c += len(self.cast)
        return c

    def info(self):
        text = self.name
        text += " (%d!)" % self.countMovies()
        text += " %s" % self.imdb_id
        if self.job:
            text += " as %s" % self.job
        if self.character:
            text += " as %s" % self.character
        text += " http://themoviedb.org/person/%d" % self.id
        return text

class Movie(object):
    def __init__(self, mov):
        self.id = mov.id
        self.languages = mov.languages
        self.posters = mov.posters
        self.backdrops = mov.backdrops
        self.crew = mov.crew
        self.cast = mov.cast
        self.genres = mov.genres
        self.runtime = mov.runtime
        self.title = mov.title
        self.releasedate = mov.releasedate
        self.original_title = mov.originaltitle
        self.imdb = mov.imdb
        c = []
        for i in self.cast:
            c.append(Person(i))
        self.cast = c
        c = []
        for i in self.crew:
            c.append(Person(i))
        self.crew= c

    def getImdbObject(self):
        return getImdbObject(self.imdb)

    def compareActorsImdb(self, min_other_movies=1):
        errors = []
        t_imdb = set()
        i_imdb = set()
        t_imdb2Person = {}
        i_imdb2Person = {}
        imov = self.getImdbObject()
        if not imov or "cast" not in imov.data:
            return []
        for i in self.cast:
            if i.imdb_id:
                t_imdb.add(i.imdb_id)
                t_imdb2Person[i.imdb_id] = i
        for i in imov.data["cast"]:
            i_imdb.add("nm%s"%i.personID)
            i_imdb2Person["nm%s"%i.personID] = i
        # now show actors which are in tmdb but not imdb
        t_more = t_imdb.difference(i_imdb)
        for i in t_more:
            errors.append("tmdb has this extra actor %s" % t_imdb2Person[i].info())
        i_more = i_imdb.difference(t_imdb)
        e = []
        c = []
        for i in i_more:
            p = iPerson(getImdbObject(i))
            if p.countMovies() > min_other_movies:
                e.append("imdb has this extra actor %s" % p.info(i_imdb2Person[i]))
                c.append(p.countMovies())
        if e:
            errors.extend(zip(*sorted(zip(c,e), reverse=True))[1])
        return errors

    def get_link(self, type=None):
        if type is None:
            return "http://themoviedb.org/movie/%s" % (str(self.id))
        else:
            return "http://themoviedb.org/movie/%s/%s" % (str(self.id), type)


def countMoviesFromList(id):
    tmdblist = List(id)
    return len(tmdblist.members)

def getMoviesFromList(id):
    tmdblist = List(id)
    for mov in tmdblist.members:
        yield Movie(mov)
