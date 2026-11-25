# Fly-In : cartes de simulation de drones

Cette collection contient des cartes conçues avec soin pour tester différents aspects des algorithmes de recherche de chemin pour drones, de la navigation élémentaire aux problèmes complexes d'optimisation.

## Catégories de cartes

### 🟢 Cartes faciles
**Public cible** : débutants, tests algorithmiques de base
- `01_linear_path.txt` - Progression linéaire simple (2 drones)
- `02_simple_fork.txt` - Séparation de chemin élémentaire (4 drones)
- `03_basic_capacity.txt` - Introduction aux contraintes de capacité (4 drones)

### 🟡 Cartes intermédiaires
**Public cible** : défis intermédiaires, optimisation des algorithmes
- `01_dead_end_trap.txt` - Impasses pouvant piéger les algorithmes naïfs (5 drones)
- `02_circular_loop.txt` - Chemins circulaires avec zones restreintes (6 drones)
- `03_priority_puzzle.txt` - Sélection du chemin optimal avec zones prioritaires (5 drones)

### 🔴 Cartes difficiles
**Public cible** : algorithmes avancés, tests de résistance
- `01_maze_nightmare.txt` - Labyrinthe complexe avec plusieurs pièges et boucles (8 drones)
- `02_capacity_hell.txt` - Contraintes de capacité extrêmes nécessitant un minutage précis (12 drones)
- `03_ultimate_challenge.txt` - **LE TEST ULTIME** - Tous les défis réunis (15 drones)

### ⚫ Cartes challenger
**Public cible** : recherche et exploration des limites algorithmiques
- `01_the_impossible_dream.txt` - **LE RÊVE IMPOSSIBLE** - Défi quasi insoluble (25 drones)

> ⚠️ **AVERTISSEMENT** : Les cartes challenger sont conçues pour repousser les limites algorithmiques et peuvent être insolubles pour la plupart des implémentations. Elles sont destinées à la recherche, aux tests de résistance et à l'exploration algorithmique plutôt qu'à la validation. L'objectif est de repousser les limites du possible, et non de satisfaire les critères d'évaluation.

> 🏆 **RECORD DU DÉFI** : L'implémentation de référence résout « The Impossible Dream » en **45 tours**. Pouvez-vous battre ce record ? Il sert de référence pour l'optimisation algorithmique et fournit un objectif concret aux implémentations avancées.

## Types de défis couverts

### 🎯 **Pièges en impasse**
Les cartes contiennent des chemins qui ne mènent nulle part, afin de vérifier si les algorithmes savent revenir en arrière ou éviter de rester bloqués.

### 🔄 **Boucles circulaires**
Les cycles dans le graphe peuvent provoquer des boucles infinies dans les algorithmes mal conçus.

### ⚡ **Contraintes de capacité**
- Limites de capacité des zones (`max_drones`)
- Limites de capacité des connexions (`max_link_capacity`)
- Goulots d'étranglement liés au temps

### 🚀 **Optimisation selon le type de zone**
- `normal` : déplacement standard en 1 tour
- `restricted` : déplacement en 2 tours (lent, mais parfois nécessaire)
- `priority` : déplacement en 1 tour, mais ce type de zone doit être privilégié
- `blocked` : complètement inaccessible

### 🧩 **Topologie complexe**
- Plusieurs chemins valides avec des coûts différents
- Points de convergence nécessitant une coordination
- Défis à plusieurs niveaux

## Stratégie de test

1. **Commencer par les cartes faciles** : s'assurer que les fonctionnalités de base fonctionnent
2. **Passer aux cartes intermédiaires** : tester la robustesse de l'algorithme
3. **Relever les défis difficiles** : tester la résistance de l'optimisation et les cas limites
4. **Test ultime** : `03_ultimate_challenge.txt` combine toutes les difficultés

## Comportement attendu

Toutes les cartes sont conçues pour être résolues avec un algorithme correctement implémenté. Cependant :

- **Cartes faciles** : devraient être résolues rapidement avec toute approche raisonnable
- **Cartes intermédiaires** : peuvent nécessiter du retour en arrière, une optimisation des chemins ou une gestion des capacités
- **Cartes difficiles** : exigent des algorithmes sophistiqués avec une résolution correcte des conflits et une optimisation appropriée

## Références de performance

- **Facile** : généralement moins de 10 tours de simulation
- **Intermédiaire** : 10 à 30 tours de simulation selon le niveau d'optimisation
- **Difficile** : plus de 30 tours de simulation, avec pour objectif de trouver des solutions valides
- **Challenger** : **record à battre : 45 tours** pour « The Impossible Dream » - conçu pour la recherche algorithmique
