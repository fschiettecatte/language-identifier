Language Identifier:
====================

Simple language identifier which allows you to create language ngrams from source
text in a variety of languages, and then identify the langiage of a piece of text.

I used the TextCat source texts for the ngram files, but you could just as easily
use the Universal Declaration of Human Rights as source text.

I wrote this in Perl about 4 years ago for another project, and decided to port it 
to Python and release it. I have kept the code very simple so it should port easily
to other languages (I have already ported it to Java.)


Directories:
------------

- ./textcat.texts - contains the source text
- ./textcat.ngrams - contains the ngram files


Commands:
---------

```

# Create ngrams from a text file for inspection
./languageIdentifier.py --create --text-file=textcat.texts/en.txt | more

# Create ngram files for all the text files in a directory
./languageIdentifier.py --create --text-directory=textcat.texts --ngram-directory=textcat.ngrams

# Identify the text language
./languageIdentifier.py --ngram-directory=textcat.ngrams --text="the quick brown fox jumped over the lazy dog"

```

There are more sample command lines in the file [languageIdentifier.py](./languageIdentifier.py)

Userful Links:
--------------

- [TextCat](http://odur.let.rug.nl/~vannoord/TextCat/)
- [Universal Declaration of Human Rights](http://www.ohchr.org/EN/UDHR/Pages/SearchByLang.aspx)





