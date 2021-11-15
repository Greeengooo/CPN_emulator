from random import choice
from argparse import ArgumentParser
import re


class Place:
    def __init__(self, dots):
        self.dots = dots
        self.contains = len(dots)


class Dot:
    def __init__(self, data):
        self.data = data


class ArcBase:
    def __init__(self, place, amount=1):
        self.place = place
        self.amount = amount


class Out(ArcBase):
    def trigger(self) -> not None:
        elem = self.place.dots.pop(0)
        self.place.contains -= self.amount
        return elem

    def non_blocking(self) -> bool:
        return self.place.contains >= self.amount


class In(ArcBase):
    def trigger(self, dot) -> None:
        for i in dot:
            self.place.dots.append(i)
        self.place.contains += self.amount


class Transition:
    def __init__(self, out_arcs, in_arcs):
        self.out_arcs = set(out_arcs)
        self.in_arcs = set(in_arcs)
        self.storage = []

    def fire(self) -> bool:
        not_blocked = all(arc.non_blocking() for arc in self.out_arcs)
        if not_blocked:
            for arc in self.out_arcs:
                elem = arc.trigger()
                self.storage.append(elem)
            for arc in self.in_arcs:
                if len(self.storage) == 1:
                    arc.trigger(self.storage)
                else:
                    arc.trigger([self.storage.pop(0)])
        return not_blocked


class PetriNet:
    def __init__(self, transitions):
        self.transitions = transitions

    def run(self, execution_plan, places) -> None:
        print('Execution plan: ' + ' => '.join(execution_plan))
        initial_state = [[dot.data for dot in place.dots] for place in places]
        print(f'Initial state:  {initial_state} \n')

        for name in execution_plan:
            t = self.transitions[name]
            if t.fire():
                print(f'{name} executed')
                current_state = [[dot.data for dot in place.dots] for place in places]
                print(f'    {current_state}')
            else:
                print(f'{name} forbidden')
        result_state = [[dot.data for dot in place.dots] for place in places]
        print(f'\nresult {result_state}')


def parse_arguments() -> tuple:
    parser = ArgumentParser()
    parser.add_argument('--sequence', type=str, nargs='+')
    parser.add_argument('--places', type=str, nargs='+')
    args = parser.parse_args()
    execution_sequence = args.sequence

    places_lst = []
    tmp_list = []
    for p in args.places:
        dots = re.sub('[()]', '', p).split(',')
        for d in dots:
            if d != '':
                tmp_list.append(Dot(d))
        places_lst.append(Place(tmp_list))
        tmp_list = []
    return execution_sequence, places_lst


if __name__ == "__main__":
    execution_sequence, places_lst = parse_arguments()
    places = places_lst
    sequence = execution_sequence

    transitions = dict(
        t1=Transition(
            [Out(places[0])],
            [In(places[1]), In(places[2])]
        ),
        t2=Transition(
            [Out(places[1]), Out(places[2])],
            [In(places[3]), In(places[0])]
        )
    )

    petri_net = PetriNet(transitions)
    petri_net.run(sequence, places)
