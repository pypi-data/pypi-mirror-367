import time

import helper
import profile_tool

start_time = time.time()
DoCoverageTest = False

if DoCoverageTest:
    import coverage

    cov = coverage.Coverage()
    cov.start()


helper.LoadMap("outputmap/basemap/basemap_wireframe.scx")
helper.EP_SetRValueStrictMode(True)

helper.InitialWireframe.wireframes("Terran Ghost", "Protoss Archon")
helper.InitialWireframe.wireframes(
    "Terran Siege Tank (Tank Mode)", "Terran Siege Tank (Tank Mode)"
)
helper.InitialWireframe.wireframes("Protoss Probe", "Terran Siege Tank (Tank Mode)")
helper.InitialWireframe.wireframes("Terran Goliath", "Terran Dropship")


@helper.EUDFunc
def foo():
    helper.InitialWireframe.wireframes("Devouring One", "Zerg Hive")
    helper.InitialWireframe.wireframes("Zerg Queen's Nest", "Protoss Photon Cannon")


@helper.TestInstance
def test_wireframe():
    foo()
    helper.InitialWireframe.wireframes("Protoss Scout", "Psi Emitter")
    helper.InitialWireframe.wireframes("Protoss Cybernetics Core", "Protoss Probe")
    helper.SetWireframes("Terran SCV", "Zerg Drone")


helper.CompressPayload(True)
helper.ShufflePayload(False)

# profile_tool.profile(f, "profile.json")
helper.SaveMap("outputmap/test_wireframe.scx", helper._testmain)
print("--- %s seconds ---" % (time.time() - start_time))

if DoCoverageTest:
    cov.stop()
    cov.html_report(include=["C:\\gitclones\\eudtrglib\\eudplib\\*"])
