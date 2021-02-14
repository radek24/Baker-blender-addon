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
# Cleaner UI
# More baking options (combined)
# Baking from selected to active #### IMPORTANT ####
# Fix metalness baking #### SOMEHOW ####
# Delete old materials and create one with baked textures
# Are custom postfixes unnecessary? #### Maybe delete them ####

bl_info = {
    "name": "Baker",
    "author": "Radovan Stastny <radovan.stastny2004@gmail.com>",
    "version": (2, 5),
    "blender": (2, 85, 0),
    "category": "Import-Export",
    "doc_url": "https://docs.google.com/document/d/17DsHfqIfumDWSyVnHD1hiJe9GBZ9yfkCH4roNI1Zo4o/edit",
    "location": "View3D > Side Panel > Autobaking",
    "description": "This addon will help you with baking",
}


# UI
# -----------------------------------------------------------------------------------------------------------------------#


def menu_func(self, context):
    self.layout.operator(mesh.set_origin_to_selection)
    self.layout.operator(mesh.add_tracked_lamp_plane)


class VIEW3D_PT_BAKER_bake(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Autobaking"
    bl_label = "Auto bake"

    def draw(self, context):
        col = self.layout.column(align=True)
        bake_prop_grp = bpy.context.window_manager.bake_prop_grp
        col.label(text="Bake type")
        col.prop(bake_prop_grp, "bake_diffuse")
        col.prop(bake_prop_grp, "bake_roughness")
        col.prop(bake_prop_grp, "bake_normal")
        col.prop(bake_prop_grp, "bake_metal")
        # Info about broken metalness baking
        if bake_prop_grp.bake_metal:
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
        col = self.layout.column(align=True, )
        col.prop(bake_prop_grp, "delete_old_uvs")

        if bake_prop_grp.bake_metal:
            col.enabled = False
            bake_prop_grp.delete_old_uvs = False

        col = self.layout.column(align=True)
        col.scale_y = 1.5
        col.operator('mesh.autobake', icon='OUTLINER_OB_IMAGE')


class VIEW3D_PT_BAKER_bake_submenu_advanced(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Autobaking"
    bl_label = "Advanced"
    bl_parent_id = "VIEW3D_PT_BAKER_bake"

    def draw(self, context):
        bake_prop_grp = bpy.context.window_manager.bake_prop_grp

        if bake_prop_grp.bake_diffuse or bake_prop_grp.bake_roughness or bake_prop_grp.bake_normal or bake_prop_grp.bake_metal:
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


# ---------------------------------------------------------------------------------------------------------------------#
# Properities


class BakePropertyGroup(bpy.types.PropertyGroup):
    bake_diffuse: bpy.props.BoolProperty(name="Diffuse", default=True, description="Will bake diffuse/color map")
    bake_roughness: bpy.props.BoolProperty(name="Roughness", default=False, description="Will bake roughness map")
    bake_normal: bpy.props.BoolProperty(name="Normal", default=False, description="Will bake normal map")
    bake_metal: bpy.props.BoolProperty(name="Metalness", default=False, description="Will create metalness map")
    bake_ao: bpy.props.BoolProperty(name="AO", default=False, description="Will create AmbientOcclusion map")

    delete_old_uvs: bpy.props.BoolProperty(name="Delete old UV's", default=False,
                                           description="Will delete all UV's but bake one")
    name_of_img: bpy.props.StringProperty(name="Prefix", default="My_baked_image",
                                          description="Name of the baked image plus automatic suffix")
    baked_img_size: bpy.props.IntProperty(name="Image size", default=1024, soft_min=64, min=10, soft_max=3840,
                                          max=5000, subtype='PIXEL', description="Resolution of all baked images")
    file_bake_output: bpy.props.StringProperty(name="Path", default="/tmp/", subtype='DIR_PATH',
                                               description="Your images will be saved there")
    baking_samples: bpy.props.IntProperty(name="Bake samples", default=1, min=1, soft_max=512,
                                          max=2048, description="Baking samples, best to leave at 1")
    bake_ao_samples: bpy.props.IntProperty(name="AO samples", default=128, min=1, soft_max=1024,
                                           max=2048, description="Baking samples for AO")

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
        default='LIGHTMAP',
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
            current_mode = bpy.context.object.mode
            return context.area.type == 'VIEW_3D' and current_mode == 'OBJECT'
        else:
            return False


    def execute(self, context):

        # Define properties
        bake_prop_grp = bpy.context.window_manager.bake_prop_grp

        # Checking if its possible to perform operator using more user friendly error message than classmethod
        if bpy.context.object.type != "MESH":
            self.report({'ERROR'}, "You need to select a mesh ")
            return {'CANCELLED'}

        if not bake_prop_grp.bake_diffuse and not bake_prop_grp.bake_roughness and not bake_prop_grp.bake_normal and not bake_prop_grp.bake_metal and not bake_prop_grp.bake_ao:
            self.report({'ERROR'}, "You need to select bake type")
            return {'CANCELLED'}

        if not bpy.context.object.data.materials.items():
            self.report({'ERROR'}, "You need to have at least one material on your object ")
            return {'CANCELLED'}


        # UV map creation
        is_there_uv = False
        # Checking if there is UV map
        for uv in bpy.context.object.data.uv_layers.items():
            if uv[0] == bake_prop_grp.uv_map_name:
                is_there_uv = True

        # Creating new uv map after it was determined that the isn't any
        if not is_there_uv:
            bpy.context.object.data.uv_layers.new(name=bake_prop_grp.uv_map_name)

        bpy.ops.object.editmode_toggle()
        # Activating Uv map
        bpy.context.object.data.uv_layers[bake_prop_grp.uv_map_name].active = True

        bpy.ops.mesh.select_all(action='SELECT')
        # Unwrapping (selecting unwrap method)

        if bake_prop_grp.unwrap_method == 'LIGHTMAP':
            bpy.ops.uv.lightmap_pack(PREF_MARGIN_DIV=0.2)

        if bake_prop_grp.unwrap_method == 'SMARTUV':
            bpy.ops.uv.smart_project(island_margin=0.2)

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

        # Needlessly complicated suffixes function
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

        # Create images and save them to file
        for suffix in suffixes:
            bpy.data.images.new("test7854961", width=size, height=size)
            bpy.data.images["test7854961"].filepath = path + name + suffix + img_type
            bpy.data.images["test7854961"].file_format = 'PNG'
            bpy.data.images["test7854961"].save()
            img = bpy.data.images["test7854961"]
            bpy.data.images.remove(img)

        # Save image
        def save_baked_image(suffix_save):
            save_name = str(name + suffix_save + img_type)
            img_bake = bpy.data.images[save_name]
            img_bake.save()

        # Create image nodes in all materials and set it to active

        def assing_image(x):

            for mat in bpy.context.object.data.materials.items():
                image_texture_node = mat[1].node_tree.nodes.new('ShaderNodeTexImage')
                image_texture_node.name = "bake image242425"
                image_texture_node.label = "bake image242425"
                # check_existing=True will check if there is already image, set to False if you want bake every
                # material separately (maybe feature? was bug.)
                image_texture_node.image = bpy.data.images.load(path + name + suffixes[x] + img_type,
                                                                check_existing=True)
                image_texture_node.location = (-150, -200)
                image_texture_node.select = True
                mat[1].node_tree.nodes.active = image_texture_node

        # Delete images from materials
        def image_delete():
            for mat_ in bpy.context.object.data.materials.items():
                node_to_delete = mat_[1].node_tree.nodes["bake image242425"]
                mat_[1].node_tree.nodes.remove(node_to_delete)

        # Setting samples to accelerate baking process
        old_samples = bpy.context.scene.cycles.samples
        bpy.context.scene.cycles.samples = bake_prop_grp.baking_samples

        # Baking diffuse
        if bake_prop_grp.bake_diffuse:
            assing_image(suffixes.index(diffuse_postfix))
            bpy.context.scene.cycles.bake_type = 'DIFFUSE'
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')
            image_delete()
            save_baked_image(diffuse_postfix)

        # Baking roughness
        if bake_prop_grp.bake_roughness:
            assing_image(suffixes.index(roughness_postfix))
            bpy.context.scene.cycles.bake_type = 'ROUGHNESS'
            bpy.ops.object.bake(type='ROUGHNESS', save_mode='EXTERNAL')
            image_delete()
            save_baked_image(roughness_postfix)
        # Baking normal
        if bake_prop_grp.bake_normal:
            assing_image(suffixes.index(normal_postfix))
            bpy.context.scene.cycles.bake_type = 'NORMAL'
            bpy.ops.object.bake(type='NORMAL', save_mode='EXTERNAL')
            image_delete()
            save_baked_image(normal_postfix)
        # Baking metalness
        if bake_prop_grp.bake_metal:
            assing_image(suffixes.index(metal_postfix))
            save_baked_image(metal_postfix)

        # Baking AO
        if bake_prop_grp.bake_ao:
            bpy.context.scene.cycles.samples = bake_prop_grp.bake_ao_samples
            assing_image(suffixes.index(ao_postfix))
            bpy.context.scene.cycles.bake_type = 'AO'
            bpy.ops.object.bake(type='AO', save_mode='EXTERNAL')
            image_delete()
            save_baked_image(ao_postfix)
            bpy.context.scene.cycles.samples = bake_prop_grp.baking_samples

        bpy.context.scene.cycles.samples = old_samples

        # Delete unused UV's
        # TOHLE ZABRALO 2 HODINYYYYYYYYYYYYYYYYYYY AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        if bake_prop_grp.delete_old_uvs:
            for uv_map in bpy.context.object.data.uv_layers.items():
                if uv_map[0] != bake_prop_grp.uv_map_name:
                    bpy.context.object.data.uv_layers[uv_map[0]].active = True
                    bpy.ops.mesh.uv_texture_remove()
        # Konec bloku, který zabral 2 hodiny :)

        # Information
        self.report({'INFO'}, "Bake was successful, images were saved")

        return {'FINISHED'}


# --------------------------------------------------------------------------------------------------------------------#
# Registration


def register():
    # UI
    bpy.utils.register_class(VIEW3D_PT_BAKER_bake)
    bpy.utils.register_class(VIEW3D_PT_BAKER_bake_submenu_advanced)
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

    # Operators
    bpy.utils.unregister_class(MESH_OT_autobaking)

    # Properties
    bpy.utils.unregister_class(BakePropertyGroup)
    del bpy.types.WindowManager.bake_prop_grp
    print("naschle")
