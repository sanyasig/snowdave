#!/usr/bin/python

import sys
import argparse
import re
import urllib, urllib2
import time
from collections import namedtuple

class GoogleTTS:

    def split_text(self, input_text, max_length=100):
        def split_text_rec(input_text, regexps, max_length=max_length):
            if(len(input_text) <= max_length): return [input_text]
            if isinstance(regexps, basestring): regexps = [regexps]
            regexp = regexps.pop(0) if regexps else '(.{%d})' % max_length

            text_list = re.split(regexp, input_text)
            combined_text = []
            combined_text.extend(split_text_rec(text_list.pop(0), regexps, max_length))
            for val in text_list:
                current = combined_text.pop()
                concat = current + val
                if(len(concat) <= max_length):
                    combined_text.append(concat)
                else:
                    combined_text.append(current)
                    #val could be >max_length
                    combined_text.extend(split_text_rec(val, regexps, max_length))
            return combined_text

        return split_text_rec(input_text.replace('\n', ''),
                              ['([\,|\.|;]+)', '( )'])

    audio_args = namedtuple('audio_args',['language','output'])

    def audio_extract(self, input_text=''):
        args = self.audio_args(language='en', output=open('output.mp3', 'w'))
        combined_text = self.split_text(input_text)
        for idx, val in enumerate(combined_text):
            mp3url = "https://translate.google.com/translate_tts?ie=UTF-8&q=%s&tl=en&client=tw-ob" % (
                urllib.quote(val))
            headers = {"Host": "translate.google.com",
                       "Referer": "http://www.gstatic.com/translate/sound_player2.swf",
                       "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) "
                                     "AppleWebKit/535.19 (KHTML, like Gecko) "
                                     "Chrome/18.0.1025.163 Safari/535.19"
            }
            req = urllib2.Request(mp3url, None, headers)
            sys.stdout.write('.')
            sys.stdout.flush()
            if len(val) > 0:
                try:
                    response = urllib2.urlopen(req)
                    args.output.write(response.read())
                    time.sleep(.5)
                except urllib2.URLError as e:
                    print ('%s' % e)
        args.output.close()
        print('Saved MP3 to %s' % args.output.name)

    def text_to_speech_mp3_argparse(self):
        description = 'Google TTS Downloader.'
        parser = argparse.ArgumentParser(description=description,
                                         epilog='tunnel snakes rule')
        parser.add_argument('-o', '--output',
                            action='store', nargs='?',
                            help='Filename to output audio to',
                            type=argparse.FileType('wb'), default='out.mp3')
        parser.add_argument('-l', '--language',
                            action='store',
                            nargs='?',
                            help='Language to output text to.', default='en')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-f', '--file',
                           type=argparse.FileType('r'),
                           help='File to read text from.')
        group.add_argument('-s', '--string',
                           action='store',
                           nargs='+',
                           help='A string of text to convert to speech.')
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)
        return parser.parse_args()
