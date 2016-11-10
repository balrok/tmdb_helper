#!/usr/bin/python2
# -*- coding: utf-8 -*-
#import tmdbsimple as tmdb
# todo look at this: https://github.com/AnthonyBloomer/tmdbv3api
from __future__ import print_function
import re
from imdb_helper import getImdbPerson, getImdbMovie
from tmdb_helper import getMoviesFromList, countMoviesFromList
import tqdm
from tmdb3 import set_key, set_cache
from urllib import quote_plus as quote
import config

# https://www.themoviedb.org/talk/56f2ad7dc3a3680764001b85


vn_letters = u"ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂ"
vn_letters += u"ưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợ"
vn_letters += u"ụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ"

# api key
set_key(config.api_key)

set_cache(filename='/tmp/tmdb3.cache')
# movie-list which to search
listId = config.list_id

# to print general imdb-mismatch the importance must be above this
PERSON_IMDB_MIN_IMPORTANT = 6
# to print more detailed mismatches:
PERSON_MIN_IMPORTANT = 8

# vietnamese actors with birthplace in vietnam should have vietnamese names
person_birthplace_exceptions = [81192, 61632, 91378]

# don't check these movies if their original title contains vietnamese characters
orig_title_vn_exceptions = [111058, 377935, 288609, 166898]

# don't check these movies that they are connected to imdb
imdb_id_exceptions = [278618, 324801, 377968, 378692]

# how many other movies a person on imdb must have stared in to suggest it for adding
IMDB_PERSON_MIN_MOVIES = 3

def check_orig_is_vietnamese(title):
    if not re.search(u"["+vn_letters+u"]", title):
        return False
    return True
def has_language(languages, code):
    for i in languages:
        if i.code == code:
            return True
    return False

def has_crew_job(crew, job):
    for i in crew:
        if i.job == job:
            return True
    return False


def check_movie(mov):
    errors = []
    if not check_orig_is_vietnamese(mov.original_title):
        if mov.id not in orig_title_vn_exceptions:
            errors.append("originaltitle not vietnamese?")

    if not has_language(mov.languages, "vi"):
        errors.append("language does not contain vietnamese")

    if isinstance(mov.releasedate, unicode):
        s = mov.original_title+" "+str(mov.releasedate)
    else:
        s = mov.original_title+" "+str(mov.releasedate.year)
    s = s.encode("utf-8")
    if mov.backdrops == []:
        errors.append("no backdrop - %s" % (mov.get_link("images/backdrops")))
        errors.append("   https://www.google.de/search?q=%s&safe=off&biw=1920&bih=1080&tbm=isch" % (quote(s)))
    if mov.posters == []:
        errors.append("no poster - %s" % (mov.get_link("images/posters")))
        errors.append("   https://www.google.de/search?q=%s&safe=off&biw=1000&bih=1500&tbm=isch" % (quote(s)))

    imov = getImdbMovie(mov.imdb)

    if not has_crew_job(mov.crew, "Director"):
        if imov.director:
            errors.append("no director -> "+", ".join(imov.director))
        else:
            errors.append("no director")
    if mov.cast == []:
        errors.append("no cast")
    if mov.genres == []:
        if imov.genres:
            errors.append("no genre -> "+imov.genres)
        else:
            errors.append("no genre")
    if not mov.runtime:
        errors.append("no runtime")
        if imov.runtimes:
            errors.append("  -> "+imov.runtimes)
    tmp_errors = mov.compareActorsImdb(min_other_movies=IMDB_PERSON_MIN_MOVIES)
    for i in tmp_errors:
        errors.append(i)

    if not mov.imdb:
        if mov.id not in imdb_id_exceptions:
            errors.append("no imdb")

    if errors != []:
        print("Movie has a problem:")
        if mov.title != mov.original_title:
            print("   ",mov.title, " - ", mov.original_title, end="")
        else:
            print("   ",mov.title, end="")
        try:
            print(" ("+str(mov.releasedate.year)+")", end="")
        except:
            pass
        print("    " + mov.get_link())
        print("    * "+"\n    * ".join(errors))


already_checked_persons = set()
def check_person(person):
    global already_checked_persons
    if person.id in already_checked_persons:
        return
    already_checked_persons.add(person.id)
    important = 0
    if hasattr(person, "crew"):
        important += len(person.crew)
    if hasattr(person, "roles"):
        important += len(person.roles)
    # TODO check imdb id
    # TODO check gender
    # not checked
        # aliases can't be checked
        # biography is mostly none
    # maybe checked
        # birthplace maybe unify different versions
    # checked
        # dayofbirth
        # profile if more than x movies, should have an image there
        # profiles
    errors = []
    if "Vietnam" in person.birthplace:
        important *= 2
    iper = getImdbPerson(person.imdb_id)
    important = max(important, iper.countMovies())
    if important > PERSON_IMDB_MIN_IMPORTANT:
        if not person.imdb_id:
            errors.append("No imdb id")
        if not person.gender:
            if iper.gender:
                errors.append("no gender - %s" % iper.gender)
            elif important > PERSON_MIN_IMPORTANT:
                errors.append("No gender")
        if not person.dayofbirth:
            if iper.birthday:
                errors.append("no dayofbirth - %s" % iper.birthday)
            elif important > PERSON_MIN_IMPORTANT:
                errors.append("no dayofbirth")
        if not person.profile:
            if important > PERSON_MIN_IMPORTANT:
                errors.append("no profile picture")
        if not person.birthplace:
            if iper.birthplace:
                errors.append("no birthplace - %s" % iper.birthplace)
            elif important > PERSON_MIN_IMPORTANT:
                errors.append("no birthplace")
        elif "Vietnam" in person.birthplace:
            if person.id not in person_birthplace_exceptions:
                names = person.aliases
                names.append(person.name)
                for n in names:
                    if check_orig_is_vietnamese(n):
                        break
                else:
                    errors.append("name is not vietnamese")

    if errors != []:
        print("Person has a problem:")
        print("   ",person.name," ",important)
        print("    http://themoviedb.org/person/"+str(person.id))
        print("    * "+"\n    * ".join(errors))



class Dummy():
    data = {}
    def __init__(self):
        pass

t = countMoviesFromList(listId)
for mov in tqdm.tqdm(getMoviesFromList(listId), total=t):
    if mov.id in (361996, 64937, 263214, 17075, 24221, 329851, 175466, 138969,
                  34899, 288609, 291008, 175447, 143653, 19552, 36266, 18328, 210626, 276465,
                  256890, 143653, 19552, 388748):
        continue
    check_movie(mov)
    continue
    for person in mov.cast:
        check_person(person)
    for person in mov.crew:
        check_person(person)

