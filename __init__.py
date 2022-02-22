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


from tokenize import String
import bpy
import time
from bpy.utils import register_class, unregister_class
from bpy.types import Operator, Panel, PropertyGroup, UIList
from bpy.props import IntProperty, StringProperty, BoolProperty, CollectionProperty


bl_info = {
    "name": "Blend File Analyzer",
    "description": "",
    "author": "Daniel Grauer",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Properties space > Scene > Blend Analyzer",
    "wiki_url": "https://github.com/kromar/blender_BlendFileAnalyzer",
    "tracker_url": "https://github.com/kromar/blender_BlendFileAnalyzer/issues",
    "category": "Scene"}


class BFA_PG_ListItems(PropertyGroup): 
    """Group of properties representing an button in the list."""
    
    name: bpy.props.StringProperty(
        name="Test Property", 
        default="Unknown")

    vertices: bpy.props.IntProperty(
        name="Test Property", 
        default=0)

    vertices_modified: bpy.props.IntProperty(
        name="Test Property", 
        default=0)

        

class BFA_UL_List(UIList): 
    """Custom Buttons List."""    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):         
        layout.operator('scene.blend_analyzer', text='', icon = 'RESTRICT_SELECT_OFF').button_input=item.name
        layout.label(text=item.name)
        layout.label(text=str(item.vertices))
        layout.label(text=str(item.vertices_modified))
        #row.prop(props, 'chart', text=str(i[0]), slider=True)


class BFA_OT_BlendAnalyzer(Operator):    
    bl_idname = 'scene.blend_analyzer'
    bl_label = 'Analyze Blend File'
    bl_description = 'Analyze Blend File'
    
    button_input: StringProperty()
            
    def get_mesh_size(self, context):        
        scene = context.scene
        objects = bpy.data.objects
        scene.bfa_list_item.clear()
        for ob in objects:
            if  ob.type == 'MESH':
                depsgraph = bpy.context.evaluated_depsgraph_get() 
                object_eval = ob.evaluated_get(depsgraph)
                object_eval.data.calc_loop_triangles()
                numTris = len(object_eval.data.loop_triangles) 
                                                
                new_item = scene.bfa_list_item.add()  
                new_item.name = ob.name
                new_item.vertices = len(ob.data.vertices)
                new_item.vertices_modified = numTris                    


    def execute(self, context):  
        if self.button_input=='ANALYZE':
            self.get_mesh_size(context) 
        else:      
            objname = self.button_input
            try:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[objname].select_set(True)
                context.view_layer.objects.active = bpy.data.objects[objname]
            except:
                pass
        return {'FINISHED'}


def profiler(start_time=0, string=None): 
    elapsed = time.time()
    print("{:.4f}".format(elapsed-start_time), "<< ", string)  
    start_time = time.time()
    return start_time  
       

class BFA_PT_UI(Panel):
    """Panel for the file analyzer, located in Properties > Scene."""
    bl_label = 'Blend File Analyzer'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        scene = context.scene 
        layout = self.layout  
        row = layout.row()
        
        row.scale_y = 1.5
        row.operator('scene.blend_analyzer', text='Analyze Content').button_input = 'ANALYZE'
        layout.split(factor=2.0, align=False)
        
        layout = self.layout  
        col = layout.column(align=True)   
        row = col.row(align=False)  
        row.operator('scene.blend_analyzer', text='Objects', icon = 'OUTLINER_OB_MESH',depress=False, emboss=True).button_input='SORT_OBJ'   
        row.operator('scene.blend_analyzer', text='Vertices', text_ctxt='Sort by Vertex count before modifiers', icon = 'GROUP_VERTEX').button_input='SORT_VERTS'  
        row.operator('scene.blend_analyzer', text='After Modifiers', text_ctxt='Sort by Vertex count after modifiers', icon = 'MODIFIER').button_input='SORT_MODS' 
        col.template_list("BFA_UL_List", "Blend File Analisys", 
                            scene, "bfa_list_item", 
                            scene, "bfa_list_index",                            
                            type='DEFAULT',
                            columns=1, rows = 1,
                        )                    


classes = (
    BFA_PT_UI,
    BFA_OT_BlendAnalyzer,
    BFA_PG_ListItems,
    BFA_UL_List,
    )


def register() -> None:
    [register_class(c) for c in classes]  
    bpy.types.Scene.bfa_list_item = CollectionProperty(type = BFA_PG_ListItems) 
    bpy.types.Scene.bfa_list_index = IntProperty(default = 0) 


def unregister() -> None:
    del bpy.types.Scene.bfa_list_item 
    del bpy.types.Scene.bfa_list_index 
    [unregister_class(c) for c in classes]


if __name__ == "__main__":
    register()