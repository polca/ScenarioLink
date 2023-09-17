from unfold import Unfold
import bw2data
bw2data.projects.set_current("ei39")

filepath="/Users/romain/Library/Caches/ActivityBrowser/8351309.zip"
dependencies={"ecoinvent": "ecoinvent 3.9.1 cutoff", "biosphere3": "biosphere3"}
scenarios=[0,]
superstructure=False

Unfold(filepath).unfold(
    dependencies=dependencies,
    scenarios=scenarios,
    superstructure=superstructure,
)