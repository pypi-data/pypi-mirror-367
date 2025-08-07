import time

from ..models.base import *
from ..models.republic import *
from ..models.state import *
from ..models.scale import *

class StateInterface(Interface):
    """
    Gère les interactions avec les votes et les officiers.

    ## Informations
    - Liste des partis enregistrés: `.Party`
    - Liste des élections: `.Election`
    - Liste des officiers et candidats: `.Officer | .Candidate`
    - Résultats des votes: `.Vote`
    """

    def __init__(self, url: str, token: str) -> None:
        super().__init__(url, token)

    """
    ---- VOTES ----
    """

    def get_vote(self, id: NSID) -> Vote:
        """
        Récupère un vote.

        ## Paramètres
        id: `NSID`\n
            ID du vote.

        ## Renvoie
        - `.Vote`
        """

        id = NSID(id)
        res = requests.get(f"{self.url}/votes/{id}", headers = self.default_headers)

        if not res:
            return None

        _data = res.json()

        vote = Vote(id)
        vote._load(_data, url = f"{self.url}/votes/{id}", headers = self.default_headers)

        return vote

    def open_vote(self, title: str = None, options: list[dict] = [], end: int = 0) -> Vote:
        """
        Déclenche un vote dans la base de données.

        ## Paramètres
        - title: `str`\n
            Titre du vote
        - options: list[dict]\n
            Liste des choix disponibles
        - end: `int`\n
            Fin du vote (timestamp)
        """

        payload = {
            "options": options,
            "end_date": end
        }

        if title:
            payload['title'] = title

        res = requests.put(f"{self.url}/open_vote", headers = self.default_headers, json = payload)

        if res.status_code == 200:
            _data = res.json()

            vote = Vote(_data['id'])
            vote._load(_data, url = f"{self.url}/votes/{_data['id']}", headers = self.default_headers)

            return vote
        else:
            res.raise_for_status()

    # Aucune possibilité de supprimer un vote

    def get_election(self, id: NSID) -> Election:
        """
        Récupère une élection.

        ## Paramètres
        id: `NSID`\n
            ID de l'élection.

        ## Renvoie
        - `.Election`
        """

        id = NSID(id)
        res = requests.get(f"{self.url}/elections/{id}", headers = self.default_headers)

        if res.status_code != 200:
            res.raise_for_status()

        _data = res.json()

        election = Election(id)
        election._load(_data, url = f"{self.url}/elections/{id}", headers = self.default_headers)

        return election

    def open_election(self, vote: Vote, start: int = None, full: bool = False) -> Election:
        """
        Déclenche une élection dans la base de données.

        ## Paramètres
        - vote: `.Vote`\n
            Vote associé
        - start: `int` (optionnel)\n
            Date de début du vote (timestamp, dure 4 jours)
        - full: `bool` (optionnel)\n
            Choix du type d'élections (True = présidentielles, False = législatives)
        """

        res = requests.put(f"{self.url}/open_election?vote={vote.id}&type={'full' if full else 'partial'}{('&date=' + str(start)) if start else ''}", headers = self.default_headers, json = {})

        if res.status_code == 200:
            _data = res.json()

            election = Election(_data['id'])
            election._load(_data, url = f"{self.url}/elections/{_data['id']}", headers = self.default_headers)

            return election
        else:
            res.raise_for_status()

    """
    PARTIS
    """

    def get_party(self, id: NSID) -> Party:
        """
        Récupère un parti politique.

        ## Paramètres
        id: `NSID`\n
            ID du parti.

        ## Renvoie
        - `.Party`
        """

        id = NSID(id)
        res = requests.get(f"{self.url}/parties/{id}", headers = self.default_headers)

        if res.status_code != 200:
            res.raise_for_status()

        _data = res.json()

        party = Party(id)
        party._load(_data, url = f"{self.url}/parties/{id}", headers = self.default_headers)

        return party

    def register_party(self, id: NSID, color: int, motto: str = None, scale: dict | Scale = {}) -> Party:
        """
        Enregistre un nouveau parti pour que ses députés puissent s'y présenter.

        ## Paramètres
        - id: `NSID`\n
            ID de l'entreprise à laquelle correspond le parti
        - color: `int`\n
            Couleur du parti
        - motto: `str, optional`\n
            Devise du parti
        - politiscales: `.Scale`\n
            Résultats du parti au test Politiscales
        """

        payload = {
            "color": color,
            "motto": motto,
            "scale": scale if isinstance(scale, dict) else scale._to_dict()
        }

        res = requests.put(f"{self.url}/register_party?candidate={id}", headers = self.default_headers, json = payload)

        if res.status_code == 200:
            _data = res.json()

            party = Party(_data['org_id'])
            party._load(_data, url = f"{self.url}/parties/{_data['org_id']}", headers = self.default_headers)

            return party
        else:
            res.raise_for_status()