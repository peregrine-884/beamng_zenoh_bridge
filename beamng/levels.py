from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging

beamng = BeamNGpy('localhost', 64256)
bng = beamng.open(launch=False)

print(bng.get_levels())