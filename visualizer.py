
import os
import trimesh
import polyscope as ps
import polyscope.imgui as psim

# Globals
available_objs = []
obj_selected = None
ps_mesh = None
obj_path = None

def launch_ps(data_path):
    global available_objs, obj_path
    obj_path = data_path

    # Init polyscope
    ps.init()
    available_objs = get_available_objs(data_path)

    # Register GUI
    ps.set_user_callback(gui_callback)

    # Show window
    ps.show()


def get_available_objs(path, filetype=".obj"):
    """Return list of .obj files in folder (filenames only)."""
    return [f for f in os.listdir(path) if f.endswith(filetype)]


def load_mesh(path, filename):
    """Load .obj with trimesh (or swap for your own loader)."""
    path = os.path.join(path, filename)
    return trimesh.load(path, force="mesh")


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