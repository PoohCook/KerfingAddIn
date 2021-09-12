import adsk.core, adsk.fusion, adsk.cam

_handlers = []


# Some utility functions
def getUi():
    app = adsk.core.Application.get()
    return app.userInterface

def getWorkspacePanel(workspaceId, panelId):
    ui = getUi()
    workspaces = ui.workspaces
    modelingWorkspace = workspaces.itemById(workspaceId)
    toolbarPanels = modelingWorkspace.toolbarPanels
    return toolbarPanels.itemById(panelId)

def getControlAndDefinition( workspaceId, panelId, commandId):
    objects = []
    ui = getUi()
    panel = getWorkspacePanel(workspaceId, panelId) 
    commandControl = panel.controls.itemById(commandId)
    if commandControl:
        objects.append(commandControl)

    commandDefinition = ui.commandDefinitions.itemById(commandId)
    if commandDefinition:
        objects.append(commandDefinition)

    return objects
    
def addCommandToPanel( workspaceId, panelId, commandId, commandName, commandDescription, commandResources, onCommandCreated):
    ui = getUi()
    toolbarPanel = getWorkspacePanel(workspaceId, panelId) 
    toolbarControlsPanel = toolbarPanel.controls
    toolbarControlPanel = toolbarControlsPanel.itemById(commandId)
    if not toolbarControlPanel:
        commandDefinitionPanel = ui.commandDefinitions.itemById(commandId)
        if not commandDefinitionPanel:
            commandDefinitionPanel = ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription, commandResources)
        
        commandDefinitionPanel.commandCreated.add(onCommandCreated)
        
        # Keep the handler referenced beyond this function
        global _handlers
        _handlers.append(onCommandCreated)
        toolbarControlPanel = toolbarControlsPanel.addCommand(commandDefinitionPanel, '')
        toolbarControlPanel.isVisible = True  
