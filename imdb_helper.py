from filecache import filecache
import imdb
import re
imdb_access = imdb.IMDb()


class Movie(object):
    def __init__(self):
        self.director = ""
        self.cast = ""
        self.genres = ""
        self.runtimes = ""
        self.imov = None

    def setImdbMovie(self, imov):
        if "director" in imov.data:
            self.director = []
            for d in imov.data["director"]:
                self.director.append(Person(d).info())
        if "cast" in imov.data:
            c = []
            for i in imov.data["cast"]:
                p = Person(getImdbObject("nm%s"%i.personID))
                c.append(p.info(i))
            self.cast = "\n".join(c)
        if "genres" in imov.data:
            self.genres = ", ".join(imov.data["genres"])
        if "runtimes" in imov.data:
            self.runtimes = str(imov.data["runtimes"])
        self.imov = imov
    
class Person(object):
    def __init__(self, iper):
        if iper:
            self.__dict__ = iper.__dict__
        self.iper = None
        self.gender = ""
        self.birthday = ""
        self.birthplace = ""
        if iper:
            if "birth notes" in iper.data:
                self.birthplace = iper.data["birth notes"]
            if "birth date" in iper.data:
                self.birthday = iper.data["birth date"]
            if "mini biography" in iper.data:
                self.extractFromBiography(iper.data["mini biography"], iper.data["name"])
            self.iper = iper
            self.currentRole = iper.currentRole

    def getName(self):
        name = " ".join(reversed(self.iper.get("long imdb canonical name").split(", ")))
        return name.replace(" (I)", "").replace(" (II)", "").replace(" (III)", "").replace(" (IV)", "").replace(" (V)", "").replace(" (VI)", "")

    def info(self, char=0):
        text = self.getName()
        if char and "data" in dir(char.currentRole) and "name" in char.currentRole.data:
            text += " as %s" % char.currentRole.data["name"]
        text += " (%d!)" % self.countMovies()
        text += " http://imdb.com/name/nm%s" % self.personID
        return text
        
    def getMoviesActed(self):
        if self.iper:
            if "actor" in self.iper.data:
                return self.iper.data["actor"]
            elif "actress" in self.iper.data:
                return self.iper.data["actress"]
        return []

    def getMoviesCrew(self, important):
        m = {}
        if self.iper:
            for key in self.iper.data:
                if important:
                    if key in ("director", "cinematographer", "writer", "producer", "director movie", "cinematographer movie",
                               "writer movie", "producer movie"):
                        m[key] = self.iper.data[key]
                    #else:
                    #    print key
                else:
                    if key.endswith("movie") or key.endswith("movies") or key == "director":
                        m[key] = self.iper.data[key]
        return m

    def countMovies(self, important=True):
        c = len(self.getMoviesActed())
        crew = self.getMoviesCrew(important)
        for i in crew:
            c += len(crew[i])
        return c

    def extractFromBiography(self, bios, name):
        bio = False
        for f in bios:
            if f.endswith("::Anonymous"):
                bio = f
                break
        if not bio:
            return
        # Yee Tong was born on October 17, 1987 in Hong Kong, British Crown Colony as Yuen Ka-Yee. She
        patterns = [".+ (was born on (?P<birthday>.* [0-9]{1,2}), [0-9]{4})?.*\. (?P<gender>He|She).*",
            "(?P<birthday>).+ is an (?P<gender>actor|actress).*",
            "(?P<birthday>).+ is a.(?P<gender>[a-zA-Z ]+),.*",
            "(?P<birthday>).+ is known for (?P<gender>his|her).*",
            ]
        for pattern in patterns:
            m = re.match(pattern, bio)
            if m:
                break
        if m:
            if m.group("birthday"):
                self.birthday = m.group("birthday")
            if m.group("gender"):
                if m.group("gender") in ("He", "his", "actor"):
                    self.gender = "Male"
                elif m.group("gender") in ("She", "her", "actress"):
                    self.gender = "Female"
                else:
                    self.gender = m.group("gender")
        else:
            print("ERROR in imdb bio")
            for pattern in patterns:
                print("re.match(\""+pattern+"\", \"\"\""+bio+"\"\"\")")
            print(bio)

        # TODO website
        # TODO alias

def getImdbMovie(id):
    m = Movie()
    if len(id) != 0:
        m.setImdbMovie(getImdbObject(id))
    return m

@filecache(31 * 24 * 60 * 60)
def getImdbObject(id):
    if id[:2] == "tt":
        return imdb_access.get_movie(id[2:])
    if id[:2] == "nm":
        return imdb_access.get_person(id[2:])
    return None

def getImdbPerson(id):
    if len(id) != 0:
        return Person(getImdbObject(id))
    else:
        return Person(None)


