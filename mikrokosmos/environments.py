import pendulum
from simpy import Environment, RealtimeEnvironment


class Cosm():

    def __init__(self, scenario):

        if scenario.get('realtime'):
            self.env = RealtimeEnvironment()

        else:
            self.start_time = pendulum.parse(scenario.get('start_time'))
            self.end_time = pendulum.parse(scenario.get('end_time'))

            self.ticks = scenario.get('ticks')

            self.env = Environment()

    def add_actor(self, spec):
        """Add an actor"""

        process = self.env.process(actor)

    def run(self, until):
        """Run the enviroment"""

        until = until or self.ticks
        self.env.run(until=until)
