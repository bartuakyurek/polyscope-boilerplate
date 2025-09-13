
import os
import trimesh
import polyscope as ps
import polyscope.imgui as psim

# Globals
available_objs = []
on_reload_callbacks = []
obj_selected = None
ps_mesh = None
obj_path = None

def launch(data_path,  extra_callbacks=None):
    """
        data_path: string path of a folder containing .obj data

        extra_callbacks: provide a callback function or a list of functions
        to extend polyscope gui callbacks. This is useful when you want to
        add extra utilities on top of the boilerplate.
    """
    global available_objs, obj_path
    obj_path = data_path

    ps.init()
    available_objs = get_available_objs(data_path)

    if extra_callbacks is None: callbacks = []
    elif callable(extra_callbacks): callbacks = [extra_callbacks]
    else: callbacks = list(extra_callbacks)

    def combined_callback():
        gui_callback() # default OBJ dropdown menu
        for cb in callbacks: # user-provided callbacks
            cb()

    ps.set_user_callback(combined_callback)
    ps.show()


def update_current_mesh(vertices, faces):
    """Update the currently visualized mesh geometry."""
    global ps_mesh
    if ps_mesh is not None:
        ps_mesh.update_geometry(vertices, faces)


def get_available_objs(path, filetype=".obj"):
    """Return list of .obj files in folder (filenames only)."""
    return [f for f in os.listdir(path) if f.endswith(filetype)]


def load_mesh(path, filename):
    """Load .obj with trimesh (or swap for your own loader)."""
    path = os.path.join(path, filename)
    return trimesh.load(path, force="mesh")

def add_on_reload_callback(cb):
    """Register a function that runs after hitting reload button."""
    on_reload_callbacks.append(cb)

def reload_mesh():
    """Load the currently selected mesh into Polyscope."""
    global ps_mesh

    if obj_selected is None:
        return

    mesh = load_mesh(obj_path, obj_selected)

    # Remove previous mesh if needed
    if ps_mesh is not None:
        ps_mesh.remove()

    # Register new mesh
    ps_mesh = ps.register_surface_mesh(
        name="mesh",
        vertices=mesh.vertices,
        faces=mesh.faces,
        transparency=0.5
    )
    ps.reset_camera_to_home_view()

    for cb in on_reload_callbacks:
        cb(mesh)
    return mesh


def gui_callback():
    """ImGui UI elements."""
    global obj_selected

    # Dropdown for selecting .obj
    psim.PushItemWidth(200)
    if psim.BeginCombo("OBJ file", obj_selected if obj_selected else "Select"):
        for val in available_objs:
            _, selected = psim.Selectable(val, obj_selected == val)
            if selected:
                obj_selected = val
        psim.EndCombo()
    psim.PopItemWidth()

    # Reload button
    if psim.Button("Reload") and obj_selected is not None:
        reload_mesh()