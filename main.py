from panda3d.core import GeoMipTerrain, DirectionalLight, PointLight, AmbientLight, Spotlight, Vec2, Vec3, Vec4, Point2, \
    Point3, Point4, ShaderTerrainMesh, HeightfieldTesselator, QueuedConnectionManager, QueuedConnectionReader, \
    QueuedConnectionListener, ConnectionWriter, NetDatagram, NetAddress
from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task, TaskManager
import traceback
from math import cos, sin
from direct.gui.DirectGui import DirectButton, DirectCheckButton, DirectRadioButton, DirectDialog, DirectEntry, \
    DirectFrame, \
    DirectLabel, DirectOptionMenu, DirectScrolledList, DirectWaitBar, DirectSlider, DirectScrollBar, DirectScrolledFrame
from panda3d.bullet import BulletWorld, BulletBoxShape, BulletCapsuleShape, BulletPlaneShape, BulletConeShape, \
    BulletRigidBodyNode, \
    BulletDebugNode, BulletSphereShape, BulletCylinderShape, BulletConvexHullShape, BulletTriangleMesh, \
    BulletHeightfieldShape, \
    BulletGhostNode, BulletHingeConstraint, BulletSliderConstraint, BulletSphericalConstraint, \
    BulletConeTwistConstraint, BulletGenericConstraint, BulletVehicle, BulletVehicleTuning, BulletSoftBodyNode, \
    BulletSoftBodyMaterial, \
    BulletSoftBodyConfig
from direct.particles.ParticleEffect import ParticleEffect
import json
from direct.interval.LerpInterval import LerpPosInterval
from direct.actor.Actor import Actor
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator


def main():
    game = ShowBase()

    _game_task_list = []
    _game_task_list.extend(game.taskMgr.getTasks())

    class Network:
        def __init__(self, events, port_address = 8067):
            self.events = events
            self.port_address = port_address
            self.connection_manger = QueuedConnectionManager()
            self.connection_listener = QueuedConnectionListener(self.connection_manger, 0)
            self.connection_reader = QueuedConnectionReader(self.connection_manger, 0)
            self.connection_writer = ConnectionWriter(self.connection_manger, 0)
            self.connection = None

            game.add_task(self.reader_polling)

        def reader_polling(self, task):
            if self.connection_reader.data_available():
                datagram = NetDatagram()

                if self.connection_reader.get_data(datagram):
                    datagram = PyDatagramIterator(datagram)
                    self.process_data(datagram)

            return Task.cont

        def process_data(self, datagram):
            self.events[datagram.get_string()](json.loads(datagram.get_string()))

        def send_data(self, event, data: dict):
            datagram = PyDatagram()
            datagram.add_string(event)
            datagram.add_string(json.dumps(data))
            self.connection_writer.send(datagram, self.connection)

    class Server(Network):
        def __init__(self, events):
            super().__init__(events)
            self.active_connects = []
            self.backlog = 3000
            self.connection = self.connection_manger.open_TCP_server_rendezvous(self.port_address, self.backlog)

    class Client(Network):
        def __init__(self, events):
            super().__init__(events)

    class Scene:
        def __init__(self, scene_name):
            self.scene_name = scene_name
            self.load(scene_name + ".py")

        def reload(self):
            self.load(self.scene_name + ".py")

        @staticmethod
        def load(filename):
            try:
                with open(filename, "r") as file:
                    python_code = compile(file.read(), "<string>", "exec")
                    exec(python_code, {"game": game,
                                       "Task": Task,
                                       "Scene": Scene,
                                       "DirectionalLight": DirectionalLight,
                                       "PointLight": PointLight,
                                       "AmbientLight": AmbientLight,
                                       "Spotlight": Spotlight,
                                       "cos": cos,
                                       "sin": sin,
                                       "Button": DirectButton,
                                       "CheckBox": DirectCheckButton,
                                       "RadioButton": DirectRadioButton,
                                       "Dialog": DirectDialog,
                                       "Entry": DirectEntry,
                                       "Frame": DirectFrame,
                                       "Label": DirectLabel,
                                       "OptionMenu": DirectOptionMenu,
                                       "ScrolledList": DirectScrolledList,
                                       "WaitBar": DirectWaitBar,
                                       "Slider": DirectSlider,
                                       "ScrollBar": DirectScrollBar,
                                       "ScrolledFrame": DirectScrolledFrame,
                                       "Vec2": Vec2,
                                       "Vec3": Vec3,
                                       "Vec4": Vec4,
                                       "Point2": Point2,
                                       "Point3": Point3,
                                       "Point4": Point4,
                                       "BulletWorld": BulletWorld,
                                       "BoxShape": BulletBoxShape,
                                       "CapsuleShape": BulletCapsuleShape,
                                       "PlaneShape": BulletPlaneShape,
                                       "ConeShape": BulletConeShape,
                                       "RigidBodyNode": BulletRigidBodyNode,
                                       "BulletDebugNode": BulletDebugNode,
                                       "SphereShape": BulletSphereShape,
                                       "CylinderShape": BulletCylinderShape,
                                       "ConvexHullShape": BulletConvexHullShape,
                                       "TriangleMeshShape": BulletTriangleMesh,
                                       "HeightfieldShape": BulletHeightfieldShape,
                                       "GhostNode": BulletGhostNode,
                                       "HingeConstraint": BulletHingeConstraint,
                                       "SliderConstraint": BulletSliderConstraint,
                                       "SphericalConstraint": BulletSphericalConstraint,
                                       "ConeTwistConstraint": BulletConeTwistConstraint,
                                       "GenericConstraint": BulletGenericConstraint,
                                       "BulletVehicle": BulletVehicle,
                                       "BulletVehicleTuning": BulletVehicleTuning,
                                       "SoftBodyNode": BulletSoftBodyNode,
                                       "SoftBodyMaterial": BulletSoftBodyMaterial,
                                       "BulletSoftBodyConfig": BulletSoftBodyConfig,
                                       "ParticleEffect": ParticleEffect,
                                       "json": json,
                                       "ShaderTerrainMesh": ShaderTerrainMesh,
                                       "GeoMipTerrain": GeoMipTerrain,
                                       "HeightfieldTesselator": HeightfieldTesselator,
                                       "clock": globalClock,
                                       "Server": Server,
                                       "Client": Client,
                                       "Actor": Actor})

            except Exception as exception:
                traceback.print_exc()

    main_scene = Scene("game")

    def reload():
        game.render.set_light_off()
        game.render2d.set_light_off()

        for child in game.render.get_children():
            child.remove_node()

        for child in game.aspect2d.get_children():
            child.remove_node()

        for task in game.taskMgr.getTasks():
            if task not in _game_task_list:
                task.remove()

        main_scene.reload()

    def debug():
        game.render.ls()
        game.render2d.ls()
        print(game.taskMgr.getAllTasks())

    game.accept("`", reload)
    game.accept("shift-`", debug)

    game.run()


if __name__ == "__main__":
    main()
