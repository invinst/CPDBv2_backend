# pragma: no cover

import argparse
import sys
import urllib
import json

from django.core.management import BaseCommand
from django.conf import settings

from twisted.internet import reactor
from twisted.internet.defer import gatherResults, DeferredList
from twisted.internet.task import cooperate
from twisted.web.client import (
    ContentDecoderAgent, Agent, readBody, PartialDownloadError, GzipDecoder
)
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Mass geocode using Google Geocode API'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.agent = ContentDecoderAgent(Agent(reactor), [(b'gzip', GzipDecoder)])
        self.deferred_results = []

    def add_arguments(self, parser):
        parser.add_argument(
            'infile',
            nargs='?',
            type=argparse.FileType('r'),
            help='Input JSON file, should be a list of objects with "address" property',
            default=sys.stdin
        )
        parser.add_argument(
            'outfile',
            nargs='?',
            type=argparse.FileType('w'),
            help=(
                'Output JSON file, the properties from input file will be preserved. '
                'Two fields will be added to each object: "lat" and "lng"'
            ),
            default=sys.stdout
        )
        parser.add_argument(
            '--coordinators-poolsize',
            type=int,
            default=20,
            help='Coordinators pool size, defaults to 20, larger mean faster download'
        )

    def geocode_api_url(self, address):
        return (
            (
                'https://maps.googleapis.com/maps/api/geocode/json?address=%s'
                '&components=country:US&key=%s'
            ) % (urllib.quote_plus(address), settings.GOOGLE_GEOCODE_APIKEY)
        ).encode('ascii', 'ignore')

    def handle_readbody_err(self, failure):
        failure.trap(PartialDownloadError)
        return failure.value.response

    def response_received(self, response):
        return readBody(response)

    def updateLatLng(self, result, index, pbar):
        obj = self.store[index]
        try:
            obj['geocode_result'] = json.loads(result)['results'][0]['geometry']['location']
        except (IndexError, KeyError):
            pass
        pbar.update(1)

    def outputResult(self, result, outfile, pbar):
        pbar.close()
        outfile.write(json.dumps(self.store))

    def printError(self, error):
        self.stderr.write(error)

    def generate_requests(self, pbar):
        for ind, obj in enumerate(self.store):
            result = self.agent.request('GET', self.geocode_api_url(obj['address']))\
                .addCallback(self.response_received)\
                .addErrback(self.handle_readbody_err)\
                .addCallback(self.updateLatLng, ind, pbar)\
                .addErrback(self.printError)
            self.deferred_results.append(result)
            yield result

    def kickstart(self, infile, outfile, coordinators_poolsize):
        self.store = json.loads(infile.read())
        pbar = tqdm(total=len(self.store))
        generator = self.generate_requests(pbar)
        DeferredList([
                cooperate(generator).whenDone()
                for _ in range(coordinators_poolsize)
            ])\
            .addCallback(lambda _: gatherResults(self.deferred_results))\
            .addCallback(self.outputResult, outfile, pbar)\
            .addErrback(self.printError)\
            .addBoth(lambda ign: reactor.callWhenRunning(reactor.stop))

    def handle(self, infile, outfile, coordinators_poolsize, *args, **options):
        reactor.callLater(0.1, self.kickstart, infile, outfile, coordinators_poolsize)
        reactor.run()
