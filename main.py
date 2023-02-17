from panda3d.core import GeoMipTerrain, DirectionalLight, PointLight, AmbientLight, Spotlight, Vec2, Vec3, Vec4, Point2, \
    Point3, Point4, ShaderTerrainMesh, HeightfieldTesselator, QueuedConnectionManager, QueuedConnectionReader, \
    QueuedConnectionListener, ConnectionWriter, NetDatagram, NetAddress, Camera, NodePath, MouseWatcher, Material, \
    Shader, ComputeNode, CompassEffect, BillboardEffect, GraphicsOutput, Texture, load_prc_file_data, \
    load_prc_file, unload_prc_file, look_at, password_hash, transpose, rotate_to, \
    old_to_new_hpr, invert, heads_up, parse_color_space_string, format_color_space, encrypt_string, encrypt_file, \
    encode_sRGB_float, encode_sRGB_uchar, decode_sRGB_float, decode_sRGB_uchar, decrypt_file, decrypt_string, \
    encrypt_stream, decrypt_stream, compress_stream, compress_file, compress_string, decompress_stream, \
    decompress_string, decompress_file, decompose_matrix, decompose_matrix_old_hpr, copy_stream, compose_matrix, \
    VirtualFileSystem, LODNode, FadeLODNode, Geom, GeomNode, GeomVertexData, GeomVertexFormat, \
    GeomPrimitive, GeomTriangles, GeomLines, GeomPoints, GeomPatches, GeomTrifans, GeomVertexColumn, \
    GeomLinestrips, GeomTristrips, GeomVertexRewriter, BoundingBox, BoundingLine, BoundingPlane, BoundingSphere, \
    BoundingVolume, BoundingHexahedron, FiniteBoundingVolume, OmniBoundingVolume, UnionBoundingVolume, \
    GeometricBoundingVolume, IntersectionBoundingVolume, ShowBoundsEffect, GeomVertexArrayData, MeshDrawer, \
    MeshDrawer2D, OrthographicLens, PerspectiveLens, PerlinNoise, PerlinNoise2, PerlinNoise3, StackedPerlinNoise2, \
    StackedPerlinNoise3, HTTPClient, HTTPChannel, HTTPCookie, TransformState, BitMask32, PandaSystem
from direct.showbase.ShowBase import ShowBase, DirectObject
from direct.task.Task import Task, TaskManager
import traceback
from math import cos, sin, sqrt, ceil, floor, pi, tau, tan, asin, acos, atan, exp, log, dist, e, degrees, radians
from direct.gui.DirectGui import DirectButton, DirectCheckButton, DirectRadioButton, DirectDialog, DirectEntry, \
    DirectFrame, DirectLabel, DirectOptionMenu, DirectScrolledList, DirectWaitBar, DirectSlider, DirectScrollBar, \
    DirectScrolledFrame
from panda3d.bullet import BulletWorld, BulletBoxShape, BulletCapsuleShape, BulletPlaneShape, BulletConeShape, \
    BulletRigidBodyNode, BulletDebugNode, BulletSphereShape, BulletCylinderShape, BulletConvexHullShape, \
    BulletTriangleMesh, BulletHeightfieldShape, BulletGhostNode, BulletHingeConstraint, BulletSliderConstraint, \
    BulletSphericalConstraint, BulletConeTwistConstraint, BulletGenericConstraint, BulletVehicle, \
    BulletVehicleTuning, BulletSoftBodyNode, BulletSoftBodyMaterial, BulletSoftBodyConfig
from direct.particles.ParticleEffect import ParticleEffect
import json
from direct.interval.SoundInterval import ShowInterval
from direct.interval.IntervalGlobal import Sequence, Parallel, SoundInterval, ActorInterval, FunctionInterval, \
    LerpFunc, LerpPosQuatScaleShearInterval, LerpPosHprScaleShearInterval, LerpPosQuatScaleInterval, \
    LerpPosHprScaleInterval, LerpQuatScaleInterval, LerpHprScaleInterval, LerpPosHprInterval, LerpPosInterval, \
    Interval, LerpColorInterval, Func, Wait, WaitInterval, WrtParentInterval, IgnoreInterval, IndirectInterval, \
    MetaInterval, HprInterval, PosInterval, PosHprInterval, HprScaleInterval, PosHprScaleInterval, AcceptInterval, \
    EventInterval, ParentInterval, ScaleInterval, LerpScaleInterval, LerpTexScaleInterval, LerpQuatInterval, \
    TestInterval, ParticleInterval, ProjectileInterval, MopathInterval, LerpShearInterval, LerpHprInterval, \
    LerpNodePathInterval, LerpPosQuatInterval, LerpAnimInterval, LerpFunctionInterval, LerpTexOffsetInterval, \
    LerpTexRotateInterval, LerpColorScaleInterval, LerpFunctionNoStateInterval, ivalMgr
from direct.filter.FilterManager import FilterManager, FrameBufferProperties
from direct.actor.Actor import Actor
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from panda3d.egg import EggPolygon, EggVertexPool, EggData, EggVertex, EggCoordinateSystem, load_egg_data

game = ShowBase()


class Network:
    def __init__(self, events, port_address=8067):
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


built_ins = {"game": game,
             "Task": Task,
             "Texture": Texture,
             "Material": Material,
             "Shader": Shader,
             "ComputeNode": ComputeNode,
             "CompassEffect": CompassEffect,
             "BillboardEffect": BillboardEffect,
             "Camera": Camera,
             "MouseWatcher": MouseWatcher,
             "NodePath": NodePath,
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
             "Actor": Actor,
             "Sequence": Sequence,
             "Parallel": Parallel,
             "SoundInterval": SoundInterval,
             "ActorInterval": ActorInterval,
             "FunctionInterval": FunctionInterval,
             "LerpFunc": LerpFunc,
             "LerpPosQuatScaleShearInterval": LerpPosQuatScaleShearInterval,
             "LerpPosHprScaleShearInterval": LerpPosHprScaleShearInterval,
             "LerpPosHprScaleInterval": LerpPosHprScaleInterval,
             "LerpQuatScaleInterval": LerpQuatScaleInterval,
             "LerpHprScaleInterval": LerpHprScaleInterval,
             "LerpPosHprInterval": LerpPosHprInterval,
             "LerpPosQuatScaleInterval": LerpPosQuatScaleInterval,
             "LerpPosInterval": LerpPosInterval,
             "LerpColorInterval": LerpColorInterval,
             "Interval": Interval,
             "Func": Func,
             "Wait": Wait,
             "WaitInterval": WaitInterval,
             "ShowInterval": ShowInterval,
             "WrtParentInterval": WrtParentInterval,
             "IgnoreInterval": IgnoreInterval,
             "IndirectInterval": IndirectInterval,
             "MetaInterval": MetaInterval,
             "HprInterval": HprInterval,
             "PosInterval": PosInterval,
             "PosHprInterval": PosHprInterval,
             "HprScaleInterval": HprScaleInterval,
             "PosHprScaleInterval": PosHprScaleInterval,
             "AcceptInterval": AcceptInterval,
             "EventInterval": EventInterval,
             "ParentInterval": ParentInterval,
             "ScaleInterval": ScaleInterval,
             "LerpScaleInterval": LerpScaleInterval,
             "LerpTexScaleInterval": LerpTexScaleInterval,
             "LerpQuatInterval": LerpQuatInterval,
             "TestInterval": TestInterval,
             "ParticleInterval": ParticleInterval,
             "ProjectileInterval": ProjectileInterval,
             "MopathInterval": MopathInterval,
             "LerpShearInterval": LerpShearInterval,
             "LerpHprInterval": LerpHprInterval,
             "LerpNodePathInterval": LerpNodePathInterval,
             "LerpPosQuatInterval": LerpPosQuatInterval,
             "LerpAnimInterval": LerpAnimInterval,
             "LerpFunctionInterval": LerpFunctionInterval,
             "LerpTexOffsetInterval": LerpTexOffsetInterval,
             "LerpTexRotateInterval": LerpTexRotateInterval,
             "LerpColorScaleInterval": LerpColorScaleInterval,
             "LerpFunctionNoStateInterval": LerpFunctionNoStateInterval,
             "load_prc_file_data": load_prc_file_data,
             "load_prc_file": load_prc_file,
             "unload_prc_file": unload_prc_file,
             "FilterManager": FilterManager,
             "LODNode": LODNode,
             "FadeLODNode": FadeLODNode,
             "Event": DirectObject,
             "NetAddress": NetAddress,
             "look_at": look_at,
             "password_hash": password_hash,
             "transpose": transpose,
             "rotate_to": rotate_to,
             "old_to_new_hpr": old_to_new_hpr,
             "invert": invert,
             "heads_up": heads_up,
             "parse_color_space_string": parse_color_space_string,
             "format_color_space": format_color_space,
             "encrypt_string": encrypt_string,
             "encrypt_file": encrypt_file,
             "encode_sRGB_float": encode_sRGB_float,
             "encode_sRGB_uchar": encode_sRGB_uchar,
             "decode_sRGB_float": decode_sRGB_float,
             "decode_sRGB_uchar": decode_sRGB_uchar,
             "decrypt_file": decrypt_file,
             "decrypt_string": decrypt_string,
             "encrypt_stream": encrypt_stream,
             "decrypt_stream": decrypt_stream,
             "compress_stream": compress_stream,
             "compress_file": compress_file,
             "compress_string": compress_string,
             "decompress_stream": decompress_stream,
             "decompress_string": decompress_string,
             "decompress_file": decompress_file,
             "decompose_matrix": decompose_matrix,
             "decompose_matrix_old_hpr": decompose_matrix_old_hpr,
             "copy_stream": copy_stream,
             "compose_matrix": compose_matrix,
             "VirtualFileSystem": VirtualFileSystem,
             "PyDatagramIterator": PyDatagramIterator,
             "PyDatagram": PyDatagram,
             "QueuedConnectionManager": QueuedConnectionManager,
             "QueuedConnectionReader": QueuedConnectionReader,
             "QueuedConnectionListener": QueuedConnectionListener,
             "ConnectionWriter": ConnectionWriter,
             "NetDatagram": NetDatagram,
             "Geom": Geom,
             "GeomNode": GeomNode,
             "GeomVertexData": GeomVertexData,
             "GeomVertexFormat": GeomVertexFormat,
             "GeomPrimitive": GeomPrimitive,
             "GeomTriangles": GeomTriangles,
             "GeomLines": GeomLines,
             "GeomPoints": GeomPoints,
             "GeomPatches": GeomPatches,
             "GeomTrifans": GeomTrifans,
             "GeomVertexColumn": GeomVertexColumn,
             "GeomLinestrips": GeomLinestrips,
             "GeomTristrips": GeomTristrips,
             "GeomVertexRewriter": GeomVertexRewriter,
             "BoundingBox": BoundingBox,
             "BoundingLine": BoundingLine,
             "BoundingPlane": BoundingPlane,
             "BoundingSphere": BoundingSphere,
             "BoundingVolume": BoundingVolume,
             "BoundingHexahedron": BoundingHexahedron,
             "FiniteBoundingVolume": FiniteBoundingVolume,
             "OmniBoundingVolume": OmniBoundingVolume,
             "UnionBoundingVolume": UnionBoundingVolume,
             "GeometricBoundingVolume": GeometricBoundingVolume,
             "IntersectionBoundingVolume": IntersectionBoundingVolume,
             "ShowBoundsEffect": ShowBoundsEffect,
             "GeomVertexArrayData": GeomVertexArrayData,
             "MeshDrawer": MeshDrawer,
             "MeshDrawer2D": MeshDrawer2D,
             "EggPolygon": EggPolygon,
             "EggVertexPool": EggVertexPool,
             "EggData": EggData,
             "EggVertex": EggVertex,
             "load_egg_data": load_egg_data,
             "EggCoordinateSystem": EggCoordinateSystem,
             "FrameBufferProperties": FrameBufferProperties,
             "OrthographicLens": OrthographicLens,
             "PerspectiveLens": PerspectiveLens,
             "PerlinNoise": PerlinNoise,
             "PerlinNoise2": PerlinNoise2,
             "PerlinNoise3": PerlinNoise3,
             "StackedPerlinNoise2": StackedPerlinNoise2,
             "StackedPerlinNoise3": StackedPerlinNoise3,
             "HTTPClient": HTTPClient,
             "HTTPChannel": HTTPChannel,
             "HTTPCookie": HTTPCookie,
             "TransformState": TransformState,
             "BitMask32": BitMask32,
             "sqrt": sqrt,
             "ceil": ceil,
             "floor": floor,
             "pi": pi,
             "tau": tau,
             "tan": tan,
             "asin": asin,
             "acos": acos,
             "atan": atan,
             "exp": exp,
             "log": log,
             "dist": dist,
             "e": e,
             "degrees": degrees,
             "radians": radians
             }


class Scene:
    def __init__(self, scene_name):
        self.scene_name = scene_name
        self.load(scene_name + ".py")

    def reload(self):
        self.load(self.scene_name + ".py")

    def load(self, filename):
        try:
            with open(filename, "r") as file:
                python_code = compile(file.read(), "<string>", "exec")
                exec(python_code, built_ins)

        except Exception as exception:
            traceback.print_exc()
            print("Error in scene", self.scene_name)


built_ins["Scene"] = Scene


def start(main_scene_name):
    _game_task_list = []
    _game_task_list.extend(game.taskMgr.getTasks())

    TaskManager._origRun = TaskManager.run

    def _run(a):
        """Overrides the default task manager's run function because by default it throws exceptions which stop the
         program."""

        if PandaSystem.getPlatform() == 'emscripten':
            return

        # Set the clock to have last frame's time in case we were
        # Paused at the prompt for a long time
        t = game.taskMgr.globalClock.getFrameTime()
        timeDelta = t - game.taskMgr.globalClock.getRealTime()
        game.taskMgr.globalClock.setRealTime(t)
        game.messenger.send("resetClock", [timeDelta])

        if game.taskMgr.resumeFunc is not None:
            game.taskMgr.resumeFunc()

        if game.taskMgr.stepping:
            game.taskMgr.step()
        else:
            game.taskMgr.running = True
            while game.taskMgr.running:
                try:
                    if len(game.taskMgr._frameProfileQueue):
                        numFrames, session, callback = game.taskMgr._frameProfileQueue.pop(0)

                        def _profileFunc(numFrames=numFrames):
                            game.taskMgr._doProfiledFrames(numFrames)

                        session.setFunc(_profileFunc)
                        session.run()
                        _profileFunc = None
                        if callback:
                            callback()
                        session.release()
                    else:
                        game.taskMgr.step()
                except KeyboardInterrupt:
                    game.taskMgr.stop()
                except SystemExit:
                    game.taskMgr.stop()
                except:
                    traceback.print_exc()

        game.taskMgr.mgr.stopThreads()

    TaskManager.run = _run

    main_scene = Scene(main_scene_name)

    def reload():
        game.render.set_light_off()
        game.render2d.set_light_off()

        GraphicsOutput.remove_all_display_regions(game.win)

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
        print(game.taskMgr)
        print(game.win.getActiveDisplayRegions())
        print(TaskManager)

    game.accept("`", reload)
    game.accept("shift-`", debug)

    game.run()


if __name__ == "__main__":
    start("game")
