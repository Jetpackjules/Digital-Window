import bpy

def setup_scene():
    # Set the rendering engine to Cycles and enable OSL
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.shading_system = True

    # Delete all existing mesh objects (like the default cube)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    # Add a plane
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))

def load_osl_shader(osl_path):
    # Create a new material
    mat = bpy.data.materials.new(name="OSL_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    # Add an OSL script node
    osl_node = nodes.new(type="ShaderNodeScript")
    osl_node.mode = 'EXTERNAL'
    osl_node.filepath = osl_path

    # Connect OSL node to Material Output
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    mat.node_tree.links.new(osl_node.outputs[0], output_node.inputs["Surface"])

    # Assign material to plane
    plane = bpy.data.objects['Plane']
    plane.data.materials.append(mat)

def adjust_perspective(x, y, distance):
    # Adjust the camera location and rotation based on the given parameters
    camera = bpy.data.objects['Camera']
    camera.location = (x, y, distance)
    camera.rotation_euler = (0, 0, 0)  # Reset rotation
    # Note: bpy.ops.object.camera_fit_coords() was removed as it's not a standard function in Blender's API.

if __name__ == "__main__":
    osl_path = "shader\\OSL_Shaders\\jiWindowBox_All_v1_10.osl"  # Replace with your OSL shader path
    x, y, distance = float(input("Enter x: ")), float(input("Enter y: ")), float(input("Enter distance: "))

    setup_scene()
    load_osl_shader(osl_path)
    adjust_perspective(x, y, distance)
