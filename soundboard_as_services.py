#!/usr/bin/python

from os import listdir
from os.path import isfile, join, exists
from emoji import emojize
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

import random
import subprocess
import dataset


class soundboardService ():
    def __init__ ( self ):
        self.__db = dataset.connect("sqlite:///db/links.db")
        self.__table = self.__db['links']

    def __links ( self ):
        alist = []
        for row in self.__table:
            alist.append(row['url'])
        return alist

    def __inc_play ( self, link ):
        numOfPlays = self.__table.find_one(url=link)
        numOfPlays['number_of_plays'] = numOfPlays['number_of_plays'] + 1
        self.__table.update( dict ( url=link, number_of_plays=numOfPlays['number_of_plays'] ), ['url'] )
        self.__db.commit()

    def randFile ( self ):
        print(self.__links())
        link = random.choice(self.__links())
        self.__inc_play ( link )
        return link

    def play ( self ):
        link = self.randFile()
        subprocess.run(['mpv', '--no-video', link])

    def insert ( self, link ):
        self.__table.insert ( dict ( url=link, number_of_plays=0 ) )
        self.__db.commit()



class playResource ( Resource ):
    def get ( self ):
        soundboard = soundboardService()
        soundboard.play()
        return dict (success = emojize("You succesfully played a audio file :thumbs_up: :godmode:"))

class randomFileResource ( Resource ):
    def get ( self ):
        soundboard = soundboardService()
        link = soundboard.randFile()
        return dict (success = emojize("You're random file :thumbs_up: :godmode:"), link_url=link)


class newLinkResource ( Resource ):
    def post ( self, fileType ):
        parser = reqparse.RequestParser()
        parser.add_argument('link')
        parser.add_argument('filename')
        parser.add_argument('file')
        args = parser.parse_args()
        soundboard = soundboardService()

        if fileType == 'link':
            soundboard.insert(args['link'])
            return dict (success = emojize("You're link was added :thumbs_up: :godmode:", use_aliases=True), link_url=args['link'])
        elif fileType == 'file':
            if args['filename'] is None:
                return dict (failure = emojize("You need to add a filename to this request :thumbsdown: :rage4:",
                                               use_aliases=True), arguments=args)
            elif request.files['file'] is None:
                return dict (failure = emojize("You need to add a file to this request :thumbsdown: :rage4:",
                                               use_aliases=True), arguments=args)
            else: 
                if exists(join('sounds/', args['filename'])):
                    return dict (failure = emojize("This filename already exits choose another:thumbsdown: :rage4:",
                                               use_aliases=True),
                                 link_url=args['link'], arguments=args)

                testFile = request.files['file']
                testFile.save(join('sounds/', args['filename']))
                soundboard.insert(join('sounds/', args['filename']))
                return dict (success = emojize("You're file was added :thumbs_up: :godmode:", use_aliases=True))
        else:
            return dict (failure = emojize("You're link was not added becuase it's not supported :thumbsdown: :rage4:", use_aliases=True),
                         link_url=args['link'], type=fileType)


app = Flask(__name__, static_folder="client")
@app.route('/')
def root ():
    return """<!DOCTYPE html>
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Soundboard as a Service</title>
                    </head>

                    <body>
                        <form action="new/file" method="POST" enctype="multipart/form-data">
                            <label for="file">Pick a file to upload</label>
                            <input type="file" name="file" id="file" />
                            <label for="filename">Filename</label>
                            <input type="text" name="filename" id="filename" />
                            <input type="submit" value="submit" />
                        </form>
                        <form action="new/link" method="POST">
                            <label for="link">URL</label>
                            <input type="text" name="link" id="link" />
                            <input type="submit" value="submit" />
                        </form>
                    </body>

                </html>"""
api = Api(app)

api.add_resource(playResource, '/play')
api.add_resource(randomFileResource, '/random')
api.add_resource(newLinkResource, '/new/<fileType>')

if __name__ == '__main__':
    app.run(port=6969)


