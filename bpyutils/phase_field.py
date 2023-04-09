#!/usr/bin/env -S blender --background --python
import numpy as np
# Turn off some warnings because bpy affects floating point maths (this may cause problems)
# https://moyix.blogspot.com/2022/09/someones-been-messing-with-my-subnormals.html
np.finfo(np.dtype("float32"))
np.finfo(np.dtype("float64"))
import bpy


def blender_setup():
    from .clean_scene import clean_scene
    clean_scene()
    scene = bpy.context.scene
    # scene.eevee.use_ssr = True
    # scene.eevee.use_ssr_refraction = True
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 8
    # Camera
    cam_data = bpy.data.cameras.new('camera')
    cam = bpy.data.objects.new('camera', cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam.location = 5 * np.array([np.cos(3.14/4), -np.sin(3.14/4), 1])
    cam.rotation_euler = (3.14/4, 0, 3.14/4)
    # constraint = cam.constraints.new(type='TRACK_TO')
    # constraint.target = liquid
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 4
    # Light
    light_data = bpy.data.lights.new('light', type='POINT')
    light = bpy.data.objects.new('light', light_data)
    bpy.context.collection.objects.link(light)
    light.location = (3,4,5)
    light.data.energy = 500


def render(file='render.png'):
    bpy.context.scene.render.filepath = file
    bpy.ops.render.render(write_still=True)


def isosurface(data, pos=None, level=0, name='isosurface', mesh_name='mesh', mat_name='mat'):
    from skimage.measure import marching_cubes
    verts, faces, norms, vals = marching_cubes(data, 0)
    if (pos is not None):
        pos = np.reshape(pos, [3,-1])
        pos_min = np.min(pos, axis=1)
        pos_max = np.max(pos, axis=1)
        verts = verts / data.shape * (pos_max - pos_min) + pos_min
    mesh = bpy.data.meshes.new(mesh_name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mat = bpy.data.materials.new(mat_name)
    obj.data.materials.append(mat)
    return obj


def material(obj, c=(1,1,1,1), t=0, r=0.5):
    mat = obj.active_material
    mat.use_screen_refraction = True
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = c
    bsdf.inputs['Transmission'].default_value = t
    bsdf.inputs['Roughness'].default_value = r


def material_abs(obj, c=(0,0.7,0.8,1), d=2):
    mat = obj.active_material
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    vol_abs = nodes.new('ShaderNodeVolumeAbsorption')
    vol_abs.inputs['Color'].default_value = c
    vol_abs.inputs['Density'].default_value = d
    mat_out = nodes['Material Output']
    links.new(mat_out.inputs[1], vol_abs.outputs[0])


def plot_fluid(fluid, solid=None, pos=None, file='render.png'):
    blender_setup()
    if (solid is not None):
        solid_obj = isosurface(solid, pos, name='solid')
        material(solid_obj, [0.7, 0.7, 0.7, 1])
    fluid_obj = isosurface(fluid, pos, name='liquid')
    material(fluid_obj, t=1, r=0)
    material_abs(fluid_obj, [0,0.7,0.8,1], 2)
    render(file)
