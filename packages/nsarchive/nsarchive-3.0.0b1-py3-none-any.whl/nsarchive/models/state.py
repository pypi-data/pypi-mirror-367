from __future__ import annotations

import requests

from .base import NSID
from .republic import Vote

class Party:
    def __init__(self, org_id: NSID):
        self._url: str = ''
        self._headers: dict = {}

        self.org_id = org_id

        self.color: int = 0x000000
        self.motto: str = None
        self.scale: dict = {}
        self.last_election: int = None

    def _load(self, _data: dict, url: str = None, headers: dict = None):
        self._url = url
        self._headers = headers

        self.org_id = _data['org_id']

        self.color = _data['color']
        self.motto = _data['motto']
        self.scale = _data['politiscales']
        self.last_election = _data['last_election']

    def cancel_candidacy(self, election: Election):
        election.cancel_candidacy()

class Election:
    def __init__(self, id: NSID):
        self._url: str = ''
        self._headers: dict = {}

        self.id = id
        self.type: str = 'full' # Partial = législatives, full = totales
        self.vote: Vote = None

    def _load(self, _data: dict, url: str = None, headers: str = None):
        self._url = url
        self._headers = headers

        self.id = _data['id']
        self.type = _data['type']

        self.vote = Vote(_data['vote']['id'])
        self.vote._load(_data['vote'], url, headers)

    def close(self):
        if self.vote:
            self.vote.close()
        else:
            return

    def add_vote(self, id: str):
        if self.vote:
            self.vote.add_vote(id)
        else:
            return

    def submit_candidacy(self):
        res = requests.put(f"{self._url}/submit")

        if res.status_code != 200:
            res.raise_for_status()

    def cancel_candidacy(self):
        res = requests.put(f"{self._url}/cancel_candidacy")

        if res.status_code != 200:
            res.raise_for_status()