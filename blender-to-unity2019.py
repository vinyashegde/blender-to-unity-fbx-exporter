import bpy
blender249 = True
blender280 = (2,80,0) <= bpy.app.version

#
# FUNCTION TO APPLY ALL SHARED MODIFIERS. IT DOES NOT CHECK MODIFIER CONFIGURATION, ONLY NAME
#
def ApplySharedModifiers():
    #start by OBJECT mode and deselect all
    objs = bpy.data.objects
    oLen = len(objs)
    #1. Group by shared mesh data
    groups = {}
    for obj in objs:
        meshDataName = obj.data.name

        if not groups.get(meshDataName):
            groups[meshDataName] = [] 
            print("Shared Mesh "+meshDataName)
            
        groups[meshDataName].append(obj)
        print("\tAdd object"+obj.name)
        
    #2. Keep groups with shared only data and modifiers.
    for groupName in groups:
        # check same modifiers
        group = groups[groupName]
        modifiers = group[0].modifiers
        print("Checking shared "+groupName)
        groupValid = ''
        for modifier in modifiers:
            print("\tChecking modifier "+modifier.name)
            for obj in group[1:]:
              if obj.modifiers.find(modifier.name) == -1:
                  groupValid = obj.name+"."+modifier.name
                  break
        if not groupValid == '': 
            print("\tNot Shared "+groupValid)
            continue            
        
        #3. Apply to geometry modifiers on first group data    
        #print("\tgroup[0].convert(target='MESH')")
        #group[0].to_mesh()
        bpy.context.view_layer.objects.active = group[0]
        group[0].select_set(state=True)
        #bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='MESH')
        group[0].select_set(state=False)
        

        #4. clean modifiers for other
        for obj in group[1:]:
            #print("\tobj.modifiers.clear()")
            obj.modifiers.clear()


try:
    import Blender
except:
    blender249 = False

if not blender280:
    if blender249:
        try:
            import export_fbx
        except:
            print('error: export_fbx not found.')
            Blender.Quit()
    else :
        try:
            import io_scene_fbx.export_fbx
        except:
            print('error: io_scene_fbx.export_fbx not found.')
            # This might need to be bpy.Quit()
            raise

# Find the Blender output file
import os
outfile = os.getenv("UNITY_BLENDER_EXPORTER_OUTPUT_FILE")

# Do the conversion
print("Starting blender to FBX conversion " + outfile)

#APPLY ALL SHARED MODIFIERS
ApplySharedModifiers()

if blender280:
    import bpy.ops
    bpy.ops.export_scene.fbx(filepath=outfile,
        check_existing=False,
        use_selection=False,
        use_active_collection=False,
        object_types= {'ARMATURE','CAMERA','LIGHT','MESH','OTHER','EMPTY'},
        use_mesh_modifiers=True,
        mesh_smooth_type='OFF',
        use_custom_props=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        apply_scale_options='FBX_SCALE_ALL')
elif blender249:
    mtx4_x90n = Blender.Mathutils.RotationMatrix(-90, 4, 'x')
    export_fbx.write(outfile,
        EXP_OBS_SELECTED=False,
        EXP_MESH=True,
        EXP_MESH_APPLY_MOD=True,
        EXP_MESH_HQ_NORMALS=True,
        EXP_ARMATURE=True,
        EXP_LAMP=True,
        EXP_CAMERA=True,
        EXP_EMPTY=True,
        EXP_IMAGE_COPY=False,
        ANIM_ENABLE=True,
        ANIM_OPTIMIZE=False,
        ANIM_ACTION_ALL=True,
        GLOBAL_MATRIX=mtx4_x90n)
else:
    # blender 2.58 or newer
    import math
    from mathutils import Matrix
    # -90 degrees
    mtx4_x90n = Matrix.Rotation(-math.pi / 2.0, 4, 'X')

    class FakeOp:
        def report(self, tp, msg):
            print("%s: %s" % (tp, msg))

    exportObjects = ['ARMATURE', 'EMPTY', 'MESH']

    minorVersion = bpy.app.version[1];
    if minorVersion <= 58:
        # 2.58
        io_scene_fbx.export_fbx.save(FakeOp(), bpy.context, filepath=outfile,
            global_matrix=mtx4_x90n,
            use_selection=False,
            object_types=exportObjects,
            mesh_apply_modifiers=True,
            ANIM_ENABLE=True,
            ANIM_OPTIMIZE=False,
            ANIM_OPTIMIZE_PRECISSION=6,
            ANIM_ACTION_ALL=True,
            batch_mode='OFF',
            BATCH_OWN_DIR=False)
    else:
        # 2.59 and later
        kwargs = io_scene_fbx.export_fbx.defaults_unity3d()
        io_scene_fbx.export_fbx.save(FakeOp(), bpy.context, filepath=outfile, **kwargs)
    # HQ normals are not supported in the current exporter

print("Finished blender to FBX conversion " + outfile)