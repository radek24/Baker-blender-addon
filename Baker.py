# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy

# TODO:
# Progress bar                                                          # probably impossible
# Baking multiple objects at a time                                     #
# More baking options (combined)                                        #
# Baking from selected to active                                        #
# Fix metalness baking                                                  # DONE
# Delete old materials and create one with baked textures               # DONE
# Are custom postfixes unnecessary?                                     # Maybe delete them
# 32-bit normal map                                                     # !important

bl_info = {
    "name": "Baker",
    "author": "Radovan Stastny <radovan.stastny2004@gmail.com>",
    "version": (3, 0),
    "blender": (2, 85, 0),
    "category": "Import-Export",
    "doc_url": "https://docs.google.com/document/d/1PrbxBye0iFXDtc9CN75W7rA8QD3h0k3_yFR-IAtDYMI/edit",
    "location": "View3D > Side Panel > Autobaking",
    "description": "This addon will help you with baking",
}


# UI
# -------------------------------------------------------------------------------------------------------------------- #


class VIEW3D_PT_BAKER_bake(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Autobaking"
    bl_label = "Auto bake"

    def draw(self, context):
      

        
        col = self.layout.column(align=True)
        bake_prop_grp = context.window_manager.bake_prop_grp
        objs = context.selected_objects
        if len(objs) != 0:
            bake_prop_grp.name_of_img = objs[0].name
        col.prop(context.scene.render.bake, "use_selected_to_active", text="Selected to active")
        col.label(text="Bake type")
        col.prop(bake_prop_grp, "bake_diffuse")
        col.prop(bake_prop_grp, "bake_roughness")
        col.prop(bake_prop_grp, "bake_normal")
        col.prop(bake_prop_grp, "bake_metal")
        # Info about broken metalness baking
        if bake_prop_grp.bake_metal and not bake_prop_grp.metalness_experimantal:
            col.label(text="Metalness will only create image", icon='ERROR')
        col.prop(bake_prop_grp, "bake_ao")

        col = self.layout.column(align=True)
        col.label(text="Same images will be overwritten", icon='INFO')
        col = self.layout.column(align=True)
        col.prop(bake_prop_grp, "name_of_img")
        col = self.layout.column(align=True)
        col.prop(bake_prop_grp, "file_bake_output")
        col = self.layout.column(align=True)
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        col.prop(bake_prop_grp, "baked_img_size")
        col = self.layout.column(align=True)
        col.prop(bake_prop_grp, "baking_samples")
        col = self.layout.column(align=True)
        col.prop(bake_prop_grp, "uv_map_name")
        col = self.layout.column(align=True)
        col.prop(bake_prop_grp, "unwrap_method")
        if bake_prop_grp.unwrap_method == 'LIGHTMAP' or bake_prop_grp.unwrap_method == 'SMARTUV':
            col = self.layout.column(align=True)
            col.prop(bake_prop_grp, "island_margin", slider=True)
        col = self.layout.column(align=True, )
        col.prop(bake_prop_grp, "delete_old_uvs")
        col.prop(bake_prop_grp, "create_new_mat")
        if bake_prop_grp.bake_metal and not bake_prop_grp.metalness_experimantal:
            col.enabled = False
            bake_prop_grp.delete_old_uvs = False
            bake_prop_grp.create_new_mat = False
        col = self.layout.column(align=True)
        col.scale_y = 1.5
        col.operator('mesh.autobake', icon='OUTLINER_OB_IMAGE')

class VIEW3D_PT_BAKER_bake_selected_to_active(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Autobaking"
    bl_label = "From selected to active"
    bl_parent_id = "VIEW3D_PT_BAKER_bake"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        cbk = context.scene.render.bake
        col = self.layout.column(align=True)
        bake_prop_grp = context.window_manager.bake_prop_grp
        col.prop(cbk, "use_cage", text="Cage")
        if cbk.use_cage:
            col.prop(cbk, "cage_object")
            col = layout.column()
            col.prop(cbk, "cage_extrusion")
            col.active = cbk.cage_object is None
        else:
            col.prop(cbk, "cage_extrusion", text="Extrusion")

        col = layout.column()
        col.prop(cbk, "max_ray_distance")



class VIEW3D_PT_BAKER_bake_submenu_advanced(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Autobaking"
    bl_label = "Advanced"
    bl_parent_id = "VIEW3D_PT_BAKER_bake"

    def draw(self, context):
        bake_prop_grp = context.window_manager.bake_prop_grp
        col = self.layout.column(align=True)
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        col.prop(bake_prop_grp, "disable_metal")
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        col.prop(bake_prop_grp, "metalness_experimantal")
        if bake_prop_grp.bake_diffuse \
                or bake_prop_grp.bake_roughness \
                or bake_prop_grp.bake_normal \
                or bake_prop_grp.bake_metal:
            col = self.layout.column(align=True)
            self.layout.use_property_split = True
            self.layout.use_property_decorate = False
            col.label(text="Postfixes:")
        if bake_prop_grp.bake_diffuse:
            col = self.layout.column(align=True)
            self.layout.use_property_split = True
            self.layout.use_property_decorate = False
            col.prop(bake_prop_grp, "bake_postfix_diffuse")
        if bake_prop_grp.bake_roughness:
            col = self.layout.column(align=True)
            self.layout.use_property_split = True
            self.layout.use_property_decorate = False
            col.prop(bake_prop_grp, "bake_postfix_roughness")
        if bake_prop_grp.bake_normal:
            col = self.layout.column(align=True)
            self.layout.use_property_split = True
            self.layout.use_property_decorate = False
            col.prop(bake_prop_grp, "bake_postfix_normal")
        if bake_prop_grp.bake_metal:
            col = self.layout.column(align=True)
            self.layout.use_property_split = True
            self.layout.use_property_decorate = False
            col.prop(bake_prop_grp, "bake_postfix_metalness")

        if bake_prop_grp.bake_ao:
            col = self.layout.column(align=True)
            self.layout.use_property_split = True
            self.layout.use_property_decorate = False
            col.prop(bake_prop_grp, "bake_postfix_ao")
            col = self.layout.column(align=True)
            col.prop(bake_prop_grp, "bake_ao_samples")


# -------------------------------------------------------------------------------------------------------------------- #
# Properities


class BakePropertyGroup(bpy.types.PropertyGroup):
    bake_diffuse: bpy.props.BoolProperty(name="Diffuse", default=True, description="Will bake diffuse/color map")
    bake_roughness: bpy.props.BoolProperty(name="Roughness", default=True, description="Will bake roughness map")
    bake_normal: bpy.props.BoolProperty(name="Normal", default=False, description="Will bake normal map")
    bake_metal: bpy.props.BoolProperty(name="Metalness", default=False, description="Will create metalness map")
    bake_ao: bpy.props.BoolProperty(name="AO", default=False, description="Will create AmbientOcclusion map")

    metalness_experimantal: bpy.props.BoolProperty(name="Experimental metalness", default=True,
                                                   description="Will try to bake metalness map, checks docs for info")
    create_new_mat: bpy.props.BoolProperty(name="Create new material", default=True,
                                           description="Will create new material with baked images and delete old mat.")
    disable_metal: bpy.props.BoolProperty(name="Disable metalness", default=True,
                                          description="will set metalness to 0 for all bakes but metallic")

    delete_old_uvs: bpy.props.BoolProperty(name="Delete old UV's", default=True,
                                           description="Will delete all UV's but bake one")
    name_of_img: bpy.props.StringProperty(name="Prefix", default="My_baked_image",
                                          description="Name of the baked image plus automatic suffix")
    island_margin: bpy.props.FloatProperty(name="UV margin", default=0.2, min=0, soft_max=1, max=4, precision=2,
                                           description="margin of UV islands")
    baked_img_size: bpy.props.IntProperty(name="Image size", default=256, soft_min=64, min=10, soft_max=3840,
                                          max=5000, subtype='PIXEL', description="Resolution of all baked images")
    file_bake_output: bpy.props.StringProperty(name="Path", default="C:/Users/home/OneDrive/Dokumenty/GitHub/Codename_RED/Content/textures", subtype='DIR_PATH',
                                               description="Your images will be saved there")
    baking_samples: bpy.props.IntProperty(name="Bake samples", default=1, min=1, soft_max=512,
                                          max=2048, description="Baking samples, best to leave at 1")
    bake_ao_samples: bpy.props.IntProperty(name="AO samples", default=128, min=1, soft_max=1024,
                                           max=2048, description="Baking samples for AO")
    from_selected_to_active: bpy.props.BoolProperty(name="Selected to active", default=False, description="Will bake from selected to active")

    bit32normal: bpy.props.BoolProperty(name="32-bit normal", default=False, description="Will create 32-bit image for "
                                                                                         "normal map")
    # Custom postfixes
    bake_postfix_diffuse: bpy.props.StringProperty(name="Diffuse", default="_diffuse")
    bake_postfix_roughness: bpy.props.StringProperty(name="Roughness", default="_roughness")
    bake_postfix_normal: bpy.props.StringProperty(name="Normal", default="_normal")
    bake_postfix_metalness: bpy.props.StringProperty(name="Metalness", default="_metalness")
    bake_postfix_ao: bpy.props.StringProperty(name="AO", default="_AO")
    uv_map_name: bpy.props.StringProperty(
        description="if you already have baking uv map, write its name here."
                    " Otherwise UV map with this name will be created",
        name="Uv map name", default="Bake")
    unwrap_method: bpy.props.EnumProperty(
        name="Unwrap method",
        items=[
            ('LIGHTMAP', "Lightmap pack", "Lightmap pack with default settings"),
            ('SMARTUV', "Smart UV project", "Smart uv project with default settings"),
            ('PLAINUV', "Unwrap", "Basic unwrap"),
            ('NONE', "None, preserve UV", "Use if you already have bake uv map"),
        ],
        default='NONE',
    )


# BAKING OPERATOR
# ---------------------------------------------------------------------------------------------------------------------#


class MESH_OT_autobaking(bpy.types.Operator):
    """will bake everything automatically, note that blender will freeze for a moment"""
    bl_idname = 'mesh.autobake'
    bl_label = "Autobake"
    bl_options = {'REGISTER', 'UNDO', 'UNDO_GROUPED', }

    # Checking if it is possible to perform operator

    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        if len(objs) != 0:
            current_mode = context.object.mode
            return context.area.type == 'VIEW_3D' and current_mode == 'OBJECT'
        else:
            return False

    def execute(self, context):
        
        # Define properties
        bake_prop_grp = context.window_manager.bake_prop_grp

        # Checking if its possible to perform operator using more user friendly error message than classmethod
        if context.scene.render.engine != 'CYCLES':
            self.report({'ERROR'}, "You need to be in Cycles render engine to bake")
            return {'CANCELLED'}

        if context.object.type != "MESH":
            self.report({'ERROR'}, "You need to select a mesh ")
            return {'CANCELLED'}

        if not bake_prop_grp.bake_diffuse \
                and not bake_prop_grp.bake_roughness \
                and not bake_prop_grp.bake_normal \
                and not bake_prop_grp.bake_metal \
                and not bake_prop_grp.bake_ao:
            self.report({'ERROR'}, "You need to select bake type")
            return {'CANCELLED'}

        if not context.object.data.materials.items():
            self.report({'ERROR'}, "You need to have at least one material on your object ")
            return {'CANCELLED'}

        # UV map creation
        is_there_uv = False
        # Checking if there is UV map
        for uv in context.object.data.uv_layers.items():
            if uv[0] == bake_prop_grp.uv_map_name:
                is_there_uv = True

        # Creating new uv map after it was determined that the isn't any
        if not is_there_uv:
            context.object.data.uv_layers.new(name=bake_prop_grp.uv_map_name)

        bpy.ops.object.editmode_toggle()
        # Activating Uv map
        context.object.data.uv_layers[bake_prop_grp.uv_map_name].active = True

        bpy.ops.mesh.select_all(action='SELECT')
        # Unwrapping (selecting unwrap method)

        if bake_prop_grp.unwrap_method == 'LIGHTMAP':
            bpy.ops.uv.lightmap_pack(PREF_MARGIN_DIV=bake_prop_grp.island_margin)

        if bake_prop_grp.unwrap_method == 'SMARTUV':
            bpy.ops.uv.smart_project(island_margin=bake_prop_grp.island_margin)

        if bake_prop_grp.unwrap_method == 'PLAINUV':
            bpy.ops.uv.unwrap()

        if bake_prop_grp.unwrap_method == 'NONE':
            pass
            # Pass just to be clear

        # Exiting edit mode
        bpy.ops.object.editmode_toggle()

        # Variables
        diffuse_postfix = bake_prop_grp.bake_postfix_diffuse
        roughness_postfix = bake_prop_grp.bake_postfix_roughness
        normal_postfix = bake_prop_grp.bake_postfix_normal
        metal_postfix = bake_prop_grp.bake_postfix_metalness
        ao_postfix = bake_prop_grp.bake_postfix_ao

        size = bake_prop_grp.baked_img_size
        name = bake_prop_grp.name_of_img
        img_type = ".png"
        path = bake_prop_grp.file_bake_output
        # Needlessly complicated suffixes adding function
        suffixes = []
        suffixes.clear()
        if bake_prop_grp.bake_diffuse:
            suffixes.append(diffuse_postfix)
        if bake_prop_grp.bake_roughness:
            suffixes.append(roughness_postfix)
        if bake_prop_grp.bake_normal:
            suffixes.append(normal_postfix)
        if bake_prop_grp.bake_metal:
            suffixes.append(metal_postfix)
        if bake_prop_grp.bake_ao:
            suffixes.append(ao_postfix)

        # Create images and save them to file (weird name just so there isn't similar images)
        for suffix in suffixes:

            bpy.data.images.new("EiqlgubGMcfVLIiu", width=size, height=size)
            bpy.data.images["EiqlgubGMcfVLIiu"].filepath = path + name + suffix + img_type
            bpy.data.images["EiqlgubGMcfVLIiu"].file_format = 'PNG'
            bpy.data.images["EiqlgubGMcfVLIiu"].save()
            img = bpy.data.images["EiqlgubGMcfVLIiu"]
            bpy.data.images.remove(img)

        # Save image
        def save_baked_image(suffix_save):
            save_name = str(name + suffix_save + img_type)
            img_bake = bpy.data.images[save_name]
            img_bake.save()

        # Create image nodes in all materials and set it to active

        def assing_image(x_type):

            for mat in context.object.data.materials.items():
                image_texture_node = mat[1].node_tree.nodes.new('ShaderNodeTexImage')
                image_texture_node.name = "bake image242425"
                image_texture_node.label = "bake image242425"
                # check_existing=True will check if there is already image, set to False if you want bake every
                # material separately (maybe feature? was bug.)
                image_texture_node.image = bpy.data.images.load(path + name + suffixes[x_type] + img_type,
                                                                check_existing=True)
                image_texture_node.location = (-150, -200)
                image_texture_node.select = True
                mat[1].node_tree.nodes.active = image_texture_node

        # Delete images from materials
        def image_delete():
            for mat_ in context.object.data.materials.items():
                node_to_delete = mat_[1].node_tree.nodes["bake image242425"]
                mat_[1].node_tree.nodes.remove(node_to_delete)

        # Setting samples to accelerate baking process
        old_samples = context.scene.cycles.samples
        context.scene.cycles.samples = bake_prop_grp.baking_samples

        # setting metalness to 0
        if bake_prop_grp.disable_metal:
            # Variables
            metalness_nodes_names = []
            metalness_nodes_sockets = []
            materials_with_met_nodes = []
            # CONNECT VALUE TO IT

            for curr_material in context.object.data.materials:
                # Define link
                link = curr_material.node_tree.links.new
                # Find principled node
                principled_node = curr_material.node_tree.nodes.get('Principled BSDF')

                # If metalness is coming from node
                if principled_node.inputs[4].links:
                    # NEED TO STORE NODE AND OUTUPT--------------------------------------------------------------------
                    for x in principled_node.inputs[4].links:
                        metalness_nodes_sockets.append(int(x.from_socket.path_from_id()[-2:-1]))
                        metalness_nodes_names.append(x.from_node.name)
                    materials_with_met_nodes.append(curr_material.name)
                    zero_value = curr_material.node_tree.nodes.new('ShaderNodeValue')
                    zero_value.outputs[0].default_value = 0
                    zero_value.location = (0, 0)
                    zero_value.name = "zero_value"
                    zero_value.label = "zero_value"
                    link(zero_value.outputs[0], principled_node.inputs[4])

                # If metalness is only one value
                if not principled_node.inputs[4].links:
                    # Adding values and connecting it
                    zero_value = curr_material.node_tree.nodes.new('ShaderNodeValue')
                    zero_value.outputs[0].default_value = 0
                    zero_value.location = (0, 0)
                    zero_value.name = "zero_value"
                    zero_value.label = "zero_value"
                    link(zero_value.outputs[0], principled_node.inputs[4])

        # Baking diffuse
        if bake_prop_grp.bake_diffuse:
            assing_image(suffixes.index(diffuse_postfix))
            context.scene.cycles.bake_type = 'DIFFUSE'
            context.scene.render.bake.use_pass_direct = False
            context.scene.render.bake.use_pass_indirect = False
            bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')
            image_delete()
            save_baked_image(diffuse_postfix)
        # Baking roughness
        if bake_prop_grp.bake_roughness:
            assing_image(suffixes.index(roughness_postfix))
            context.scene.cycles.bake_type = 'ROUGHNESS'
            bpy.ops.object.bake(type='ROUGHNESS', save_mode='EXTERNAL')
            image_delete()
            save_baked_image(roughness_postfix)
        # Baking normal
        if bake_prop_grp.bake_normal:
            assing_image(suffixes.index(normal_postfix))
            context.scene.cycles.bake_type = 'NORMAL'
            bpy.ops.object.bake(type='NORMAL', save_mode='EXTERNAL')
            image_delete()
            save_baked_image(normal_postfix)

        # Baking AO
        if bake_prop_grp.bake_ao:
            context.scene.cycles.samples = bake_prop_grp.bake_ao_samples
            assing_image(suffixes.index(ao_postfix))
            context.scene.cycles.bake_type = 'AO'
            bpy.ops.object.bake(type='AO', save_mode='EXTERNAL')
            image_delete()
            save_baked_image(ao_postfix)
            context.scene.cycles.samples = bake_prop_grp.baking_samples

        # Return back metalness
        if bake_prop_grp.disable_metal:
            material_index = 0
            for curr_material in context.object.data.materials:
                link = curr_material.node_tree.links.new

                # Find principled node
                principled_node = curr_material.node_tree.nodes.get('Principled BSDF')
                node_to_delete_value_zero = curr_material.node_tree.nodes.get("zero_value")
                curr_material.node_tree.nodes.remove(node_to_delete_value_zero)
                # If metalness is coming from node
                # Check if index will be out of range(!important)
                if len(materials_with_met_nodes) > material_index:
                    if materials_with_met_nodes[material_index] == curr_material.name:
                        metalness_node = curr_material.node_tree.nodes.get(str(metalness_nodes_names[material_index]))
                        link(metalness_node.outputs[metalness_nodes_sockets[material_index]], principled_node.inputs[4])
                        material_index = material_index + 1

        # Baking metalness
        if bake_prop_grp.bake_metal:
            assing_image(suffixes.index(metal_postfix))
            if bake_prop_grp.metalness_experimantal:
                for curr_material in context.object.data.materials:
                    # Define link
                    link = curr_material.node_tree.links.new
                    # Find principled node
                    principled_node = curr_material.node_tree.nodes.get('Principled BSDF')
                    # If metalness is coming from node
                    if principled_node.inputs[4].links:
                        for x in principled_node.inputs[4].links:
                            output_index = int(x.from_socket.path_from_id()[-2:-1])
                            output_node = curr_material.node_tree.nodes.get("Material Output")
                            metalness_node = curr_material.node_tree.nodes.get(str(x.from_node.name))
                            link(metalness_node.outputs[output_index], output_node.inputs[0])

                    # If metalness is only one value
                    if not principled_node.inputs[4].links:
                        # Adding values and connecting it
                        value_for_bake = curr_material.node_tree.nodes.new('ShaderNodeValue')
                        value_for_bake.outputs[0].default_value = principled_node.inputs[4].default_value
                        value_for_bake.location = (0, 0)
                        value_for_bake.name = "Metallic_Value"
                        output_node = curr_material.node_tree.nodes.get("Material Output")
                        link(value_for_bake.outputs[0], output_node.inputs[0])

                # Baking "emission"
                context.scene.cycles.bake_type = 'EMIT'
                bpy.ops.object.bake(type='EMIT', save_mode='EXTERNAL')

                # Deleting value
                # reconnecting metallic nodes back(enough is to connect principled to output)
                for curr_material in context.object.data.materials:
                    principled_node = curr_material.node_tree.nodes.get('Principled BSDF')

                    # If metalness is coming from node
                    if principled_node.inputs[4].links:
                        # Define link
                        link = curr_material.node_tree.links.new
                        # Get nodes
                        principled_node = curr_material.node_tree.nodes.get('Principled BSDF')
                        output_node = curr_material.node_tree.nodes.get("Material Output")
                        link(principled_node.outputs[0], output_node.inputs[0])
                    # If metalness is only one value
                    if not principled_node.inputs[4].links:
                        # Define link
                        link = curr_material.node_tree.links.new
                        # Get nodes
                        principled_node = curr_material.node_tree.nodes.get('Principled BSDF')
                        output_node = curr_material.node_tree.nodes.get("Material Output")
                        # Link them back
                        link(principled_node.outputs[0], output_node.inputs[0])
                        # Delete value node
                        node_to_delete_value = curr_material.node_tree.nodes.get("Metallic_Value")
                        curr_material.node_tree.nodes.remove(node_to_delete_value)
            image_delete()
            save_baked_image(metal_postfix)

        # Return samples to "old" samples
        context.scene.cycles.samples = old_samples

        # Delete unused UV's
        # TOHLE ZABRALO 2 HODINYYYYYYYYYYYYYYYYYYY AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        if bake_prop_grp.delete_old_uvs:
            for uv_map in context.object.data.uv_layers.items():
                if uv_map[0] != bake_prop_grp.uv_map_name:
                    context.object.data.uv_layers[uv_map[0]].active = True
                    bpy.ops.mesh.uv_texture_remove()
        # Konec bloku, který zabral 2 hodiny :)

        # Creating material for baked textures
        if bake_prop_grp.create_new_mat:
            # Deleting materials
            for material in context.object.data.materials.items():
                bpy.ops.object.material_slot_remove()

            # Creating material
            baked_material = bpy.data.materials.new(name="Baked_mat")
            baked_material.use_nodes = True

            # Define link
            link = baked_material.node_tree.links.new

            # Material modification
            principled_node = baked_material.node_tree.nodes['Principled BSDF']
            # Adding all posible textures
            for index in suffixes:
                texture_node = baked_material.node_tree.nodes.new('ShaderNodeTexImage')
                texture_node.label = str(index)
                texture_node.name = str(index)
                texture_node.image = bpy.data.images.load(path + name + index + img_type,
                                                          check_existing=True)
            # checking which textures were baked, accesing them and connecting them
            if bake_prop_grp.bake_diffuse:
                image_node = baked_material.node_tree.nodes[str(diffuse_postfix)]
                image_node.location = (-500, 600)
                link(image_node.outputs[0], principled_node.inputs[0])

            if bake_prop_grp.bake_roughness:
                image_node = baked_material.node_tree.nodes[str(roughness_postfix)]
                # Setting location
                image_node.location = (-500, 0)
                # Setting color space
                image_node.image.colorspace_settings.name = 'Non-Color'
                # connecting
                link(image_node.outputs[0], principled_node.inputs[7])

            if bake_prop_grp.bake_normal:
                # Creating normal map node
                normal_converter = baked_material.node_tree.nodes.new('ShaderNodeNormalMap')
                image_node = baked_material.node_tree.nodes[str(normal_postfix)]
                normal_converter.location = (-200, -300)
                image_node.image.colorspace_settings.name = 'Non-Color'
                image_node.location = (-500, -300)
                link(image_node.outputs[0], normal_converter.inputs[1])
                link(normal_converter.outputs[0], principled_node.inputs['Normal'])

            if bake_prop_grp.bake_metal:
                image_node = baked_material.node_tree.nodes[str(metal_postfix)]
                image_node.location = (-500, 300)
                image_node.image.colorspace_settings.name = 'Non-Color'
                link(image_node.outputs[0], principled_node.inputs[4])

            # Assign material to object
            context.object.active_material = baked_material

        # Information
        self.report({'INFO'}, "Bake was successful, images were saved")

        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------------------------- #
# Registration


def register():
    # UI
    bpy.utils.register_class(VIEW3D_PT_BAKER_bake)
    bpy.utils.register_class(VIEW3D_PT_BAKER_bake_submenu_advanced)
    bpy.utils.register_class(VIEW3D_PT_BAKER_bake_selected_to_active)
    # operators

    bpy.utils.register_class(MESH_OT_autobaking)

    # Properties
    bpy.utils.register_class(BakePropertyGroup)
    bpy.types.WindowManager.bake_prop_grp = bpy.props.PointerProperty(type=BakePropertyGroup)

    # Vypíše do konzole tajnou zprávu :)
    print("I1C jsou borci")


def unregister():
    # UI
    bpy.utils.unregister_class(VIEW3D_PT_BAKER_bake)
    bpy.utils.unregister_class(VIEW3D_PT_BAKER_bake_submenu_advanced)
    bpy.utils.unregister_class(VIEW3D_PT_BAKER_bake_selected_to_active)

    # Operators
    bpy.utils.unregister_class(MESH_OT_autobaking)

    # Properties
    bpy.utils.unregister_class(BakePropertyGroup)
    del bpy.types.WindowManager.bake_prop_grp
    print("naschle")
