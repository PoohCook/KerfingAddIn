#Author-Pooh
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from . import PT
from . import CMD

_handlers = []

# command properties
commandId = 'KerfProfile'
commandName = 'Kerf Profile'
commandDescription = 'Kerf a profile for laser cutting\n'
commandResources = './resources/command'
workspaceToUse = 'FusionSolidEnvironment'
panelToUse = 'SketchModifyPanel'

class MyCommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmdArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = cmdArgs.command.commandInputs
            kerf_width = inputs.itemById("kerf_width").value
            selector = inputs.itemById("profile_select")
            if selector.selectionCount > 0:
                selectedProfile = adsk.fusion.Profile.cast(selector.selection(0).entity)

                profileTools = PT.ProfileTools()
                profileTools.offsetProfiles(selectedProfile, kerf_width)

        except:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))                

# Event handler that reacts to when the command is destroyed. This terminates the script.            
class MyCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            cmdArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = cmdArgs.command.commandInputs
            kerf_width = inputs.itemById("kerf_width").value
            selector = inputs.itemById("profile_select")
            selectedProfile = adsk.fusion.Profile.cast(selector.selection(0).entity)

            profileTools = PT.ProfileTools()
            profileTools.offsetProfiles(selectedProfile, kerf_width, deleteProfiles=True)

        except:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



# Event handler that creates my Command.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the execute event.           
            onExecute = MyCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute) 

            onExecutePreview = MyCommandExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            _handlers.append(onExecutePreview)        

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            # Create a selection input.
            selectionInput = inputs.addSelectionInput('profile_select', 'Profile', 'Profile to Kern')
            selectionInput.addSelectionFilter(adsk.core.SelectionCommandInput.Profiles)
            selectionInput.setSelectionLimits(1,1)

            inputs.addValueInput('kerf_width', 'Kerf width', 'mm', adsk.core.ValueInput.createByString("kerf_width"))

        except:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        # ui.messageBox('Hello addin')

        CMD.addCommandToPanel(workspaceToUse, panelToUse, 
                              commandId, commandName, commandDescription, commandResources, 
                              MyCommandCreatedHandler())

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        # ui.messageBox('Stop addin')

        objArray = CMD.getControlAndDefinition(workspaceToUse, panelToUse, commandId)
            
        for obj in objArray:
            obj.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
