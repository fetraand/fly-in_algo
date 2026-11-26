"""Version monofichier de la démonstration répartie dans les autres modules.

Ce fichier rassemble les modèles, le calcul d'itinéraire, l'ordonnancement
des drones et la construction du réseau d'exemple. Il peut être exécuté
directement avec ``python3 demo_source.py``.

Les rangs sont des couples contenant le coût restant en tours et la pénalité
secondaire qui favorise les itinéraires passant par des zones prioritaires.
"""

import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


Rank = Tuple[int, int]


@dataclass(frozen=True)
class Zone:
    """Représente une zone du réseau.

    ``kind`` décrit le type de zone : ``normal``, ``priority``, ``restricted``
    ou ``blocked``. Une capacité de ``None`` signifie que la zone n'est pas
    limitée en nombre de drones.
    """

    name: str
    kind: str = "normal"
    capacity: Optional[int] = 1

    @property
    def turn_cost(self) -> int:
        """Renvoie le nombre de tours nécessaires pour entrer dans la zone."""
        return 2 if self.kind == "restricted" else 1

    @property
    def preferred(self) -> bool:
        """Indique si la zone est prioritaire en cas d'égalité de coût."""
        return self.kind == "priority"

    @property
    def enterable(self) -> bool:
        """Indique si un drone a le droit d'entrer dans la zone."""
        return self.kind != "blocked"


@dataclass(frozen=True)
class Link:
    """Représente une connexion bidirectionnelle et sa capacité par tour."""

    left: str
    right: str
    capacity: int = 1

    def other_end(self, zone_name: str) -> str:
        """Renvoie l'autre extrémité de la connexion.

        Lève ``ValueError`` si ``zone_name`` ne correspond à aucune extrémité.
        """
        if zone_name == self.left:
            return self.right
        if zone_name == self.right:
            return self.left
        raise ValueError(f"{zone_name!r} is not an endpoint of this link")

    @property
    def key(self) -> frozenset[str]:
        """Renvoie une clé identique quel que soit l'ordre des extrémités."""
        return frozenset((self.left, self.right))


@dataclass
class Network:
    """Stocke les zones et la liste des connexions de chacune d'elles."""

    zones: Dict[str, Zone]
    adjacency: Dict[str, List[Link]] = field(init=False)

    def __post_init__(self) -> None:
        """Initialise une liste de connexions vide pour chaque zone."""
        self.adjacency = {name: [] for name in self.zones}

    def connect(self, left: str, right: str, capacity: int = 1) -> None:
        """Ajoute une connexion bidirectionnelle entre deux zones."""
        link = Link(left, right, capacity)
        self.adjacency[left].append(link)
        self.adjacency[right].append(link)


@dataclass
class Drone:
    """Représente un drone dans la simulation simplifiée."""

    identifier: int
    zone: str
    delivered: bool = False

    @property
    def label(self) -> str:
        """Renvoie l'étiquette du drone utilisée dans l'affichage."""
        return f"D{self.identifier}"


def reverse_dijkstra(network: Network, end: str) -> Dict[str, Rank]:
    """Calcule le meilleur rang de chaque zone atteignable jusqu'à ``end``.

    La recherche part de la destination et parcourt le graphe en sens inverse.
    Le premier élément du rang est le nombre de tours restants ; le second
    départage les itinéraires de même coût en favorisant les zones prioritaires.
    Ces deux critères sont comparés dans cet ordre : une meilleure priorité ne
    compense donc jamais un trajet plus long.

    Les zones bloquées sont exclues. Le coût d'une zone est ajouté lorsqu'on
    remonte depuis cette zone vers ses voisines, ce qui revient à compter le
    coût d'entrée dans chaque zone du trajet, mais pas celui de son origine.
    """
    best: Dict[str, Rank] = {end: (0, 0)}
    queue: List[Tuple[int, int, str]] = [(0, 0, end)]

    while queue:
        cost, non_priority, current = heapq.heappop(queue)
        if (cost, non_priority) != best.get(current):
            continue

        zone = network.zones[current]
        extra_penalty = 0 if zone.preferred else 1
        for link in network.adjacency[current]:
            previous = link.other_end(current)
            if not network.zones[previous].enterable:
                continue

            candidate = (
                cost + zone.turn_cost,
                non_priority + extra_penalty,
            )
            if candidate < best.get(previous, (float("inf"), float("inf"))):
                best[previous] = candidate
                heapq.heappush(
                    queue, (candidate[0], candidate[1], previous)
                )

    return best


def choose_next_zone(
    network: Network,
    drone: Drone,
    ranks: Dict[str, Rank],
    occupancy: Dict[str, int],
    link_usage: Dict[frozenset[str], int],
) -> Optional[Tuple[Link, Zone]]:
    """Choisit une prochaine zone légale qui rapproche le drone de l'arrivée.

    Une destination est admissible si elle n'est pas bloquée, si elle réduit
    le coût restant, si sa capacité n'est pas atteinte et si la connexion
    dispose encore d'une place pour ce tour. En cas d'égalité, la fonction
    préfère le meilleur rang, puis la zone la moins occupée.

    Renvoie la connexion et la zone choisies, ou ``None`` si aucun déplacement
    n'est possible pour le drone pendant ce tour.
    """
    current_rank = ranks[drone.zone]
    choices: List[Tuple[Rank, int, Link, Zone]] = []

    for link in network.adjacency[drone.zone]:
        target = network.zones[link.other_end(drone.zone)]
        if not target.enterable or target.name not in ranks:
            continue

        target_rank = ranks[target.name]
        if target_rank[0] >= current_rank[0]:
            continue
        if (
            target.capacity is not None
            and occupancy[target.name] >= target.capacity
        ):
            continue
        if link_usage.get(link.key, 0) >= link.capacity:
            continue

        choices.append(
            (target_rank, occupancy[target.name], link, target)
        )

    if not choices:
        return None
    choices.sort(key=lambda choice: (choice[0], choice[1]))
    return choices[0][2], choices[0][3]


def simulate(
    network: Network, start: str, end: str, count: int
) -> List[List[str]]:
    """Construit le planning glouton des déplacements d'une flotte de drones.

    Les drones sont traités une fois par tour, dans l'ordre de leur rang
    restant puis de leur identifiant. Chaque déplacement met immédiatement à
    jour l'occupation des zones et des connexions, afin que les drones suivants
    respectent les capacités disponibles. Le résultat contient, pour chaque
    tour, les déplacements au format ``D<numéro>-<zone>``.

    Lève ``ValueError`` si aucune route ne relie ``start`` à ``end`` et
    ``RuntimeError`` si aucun drone ne peut avancer alors qu'il en reste à
    livrer.
    """
    ranks = reverse_dijkstra(network, end)
    if start not in ranks:
        raise ValueError(f"no route from {start!r} to {end!r}")

    drones = [Drone(index, start) for index in range(1, count + 1)]
    occupancy = {name: 0 for name in network.zones}
    occupancy[start] = count
    turns: List[List[str]] = []
    delivered = 0

    while delivered < count:
        link_usage: Dict[frozenset[str], int] = {}
        moves: List[str] = []
        ready = [drone for drone in drones if not drone.delivered]
        ready.sort(key=lambda drone: (ranks[drone.zone], drone.identifier))

        for drone in ready:
            choice = choose_next_zone(
                network, drone, ranks, occupancy, link_usage
            )
            if choice is None:
                continue

            link, target = choice
            occupancy[drone.zone] -= 1
            occupancy[target.name] += 1
            link_usage[link.key] = link_usage.get(link.key, 0) + 1
            moves.append(f"{drone.label}-{target.name}")
            drone.zone = target.name
            if target.name == end:
                drone.delivered = True
                delivered += 1

        if not moves:
            raise RuntimeError("no drone can move; the schedule is stuck")
        turns.append(moves)

    return turns


def build_example() -> Network:
    """Crée deux chemins de même coût et une branche inaccessible."""
    zones = {
        "start": Zone("start", capacity=None),
        "priority_entry": Zone("priority_entry"),
        "priority_lane": Zone("priority_lane", kind="priority"),
        "normal_entry": Zone("normal_entry"),
        "normal_lane": Zone("normal_lane"),
        "blocked": Zone("blocked", kind="blocked"),
        "goal": Zone("goal", capacity=None),
    }
    network = Network(zones)
    network.connect("start", "priority_entry")
    network.connect("priority_entry", "priority_lane")
    network.connect("priority_lane", "goal")
    network.connect("start", "normal_entry")
    network.connect("normal_entry", "normal_lane")
    network.connect("normal_lane", "goal")
    network.connect("start", "blocked")
    network.connect("blocked", "goal")
    return network


def main() -> None:
    """Affiche les rangs des zones et le planning de déplacement des drones."""
    network = build_example()
    ranks = reverse_dijkstra(network, "goal")

    print("Coût restant depuis chaque zone (coût, pénalité):")
    for name in network.zones:
        if name in ranks:
            print(f"  {name:16} {ranks[name]}")
        else:
            print(f"  {name:16} inaccessible")

    print("\nDéplacements par tour:")
    for turn_number, moves in enumerate(
        simulate(network, "start", "goal", count=2), start=1
    ):
        print(f"  Tour {turn_number}: {' '.join(moves)}")


if __name__ == "__main__":
    main()
