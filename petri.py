from random import choice
from argparse import ArgumentParser
import re


class Place:
    def __init__(self, dots):
        self.dots = dots
        self.contains = len(dots)

    def get_colors(self):
        return [d.data for d in self.dots]

class Dot:
    def __init__(self, data):
        self.data = data


class ArcBase:
    def __init__(self, place, color, amount=1):
        self.color = color
        self.place = place
        self.amount = amount

    def get_color(self):
        return self.color

class Out(ArcBase):
    def trigger(self) -> not None:
        dot = list(filter(lambda x: x.data == self.get_color(), self.place.dots))
        self.place.dots.remove(dot[0])
        self.place.contains -= self.amount
        return dot[0]

    def non_blocking(self) -> bool:
        return self.place.contains >= self.amount and self.color in self.place.get_colors()


class In(ArcBase):
    def trigger(self, dot) -> None:
        self.place.dots.append(dot)
        self.place.contains += self.amount


class Transition:
    def __init__(self, name, out_arcs, in_arcs):
        self.name = name
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
                    arc.trigger(self.storage[0])
                else:
                    dot = list(filter(lambda x: x.data == arc.get_color(), self.storage))
                    if len(dot) == 0:
                        continue
                    self.storage.remove(dot[0])
                    arc.trigger(dot[0])
        self.storage = []
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
                break
        result_state = [[dot.data for dot in place.dots] for place in places]
        print(f'\nresult {result_state}')


def parse_arguments() -> tuple:
    parser = ArgumentParser()
    parser.add_argument('--places', type=str, nargs='+')
    args = parser.parse_args()

    places_lst = []
    tmp_list = []
    for p in args.places:
        dots = re.sub('[()]', '', p).split(',')
        for d in dots:
            if d != '':
                tmp_list.append(Dot(d))
        places_lst.append(Place(tmp_list))
        tmp_list = []
    return places_lst


if __name__ == "__main__":
    places_lst = parse_arguments()
    places = places_lst

    transitions = dict(
        t1=Transition(1,
            [Out(places[0], "red"), Out(places[0], "blue")],
            [In(places[1], "red"), In(places[2], "blue")]
        ),
        t2=Transition(2,
            [Out(places[1], "red"), Out(places[2], "blue"), Out(places[2], "red")],
            [In(places[3], "red"), In(places[0], "blue")]
        )
    )

    sequence = [choice(list(transitions.keys())) for _ in range(5)]

    petri_net = PetriNet(transitions)
    petri_net.run(sequence, places)
