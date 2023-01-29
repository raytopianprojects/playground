from panda3d.core import GeoMipTerrain, DirectionalLight, PointLight, AmbientLight, Spotlight
from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
import traceback
from math import cos, sin
from direct.gui.DirectGui import DirectButton, DirectCheckButton, DirectRadioButton, DirectDialog, DirectEntry, DirectFrame, \
    DirectLabel, DirectOptionMenu, DirectScrolledList, DirectWaitBar, DirectSlider, DirectScrollBar, DirectScrolledFrame

def main():        
    game = ShowBase()
        
    _game_task_list = []
        
    def reload(file="game.py"):
        
        def add_task(a):
            _game_task_list.append(game.add_task(a))
        
        game.render.set_light_off()
        game.render2d.set_light_off()

        for child in game.render.get_children():
            if child.name != "camera":
                child.remove_node()
        
        for child in game.aspect2d.get_children():
            child.remove_node()
            
        if _game_task_list:
            for task in _game_task_list:
                task.remove()
        
        try:
            with open(file, "r") as file:
                python_code = compile(file.read(), "<string>", "exec")
                exec(python_code, {"game": game,
                                   "add_task": add_task,
                                   "Task": Task,
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
                                   "ScrolledList":DirectScrolledList,
                                   "WaitBar": DirectWaitBar,
                                   "Slider": DirectSlider,
                                   "ScrollBar": DirectScrollBar,
                                   "ScrolledFrame": DirectScrolledFrame})
                
        except Exception as exception:
            traceback.print_exc()

    
    def debug():
        game.render.ls()
        game.render2d.ls()
        print(_game_task_list)
    
    game.accept("r", reload)
    game.accept("`", debug)

    
    game.run()
    
if __name__ == "__main__":
    main()
