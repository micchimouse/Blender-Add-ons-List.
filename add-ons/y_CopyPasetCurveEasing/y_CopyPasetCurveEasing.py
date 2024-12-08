bl_info = {
    "name" : "Copy Paset F-Curve Easing ",
    "author" : "Yukimituki",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "F-Curves"
}

import bpy
import json
class CURVE_PT_EasingCopyPaste(bpy.types.Panel):
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "F-Curve"
    bl_label = "Easing copy&paste"
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Fカーブの補完曲線をコピペ")
        row = layout.row()
        row.label(text="コントロールポイントを一つだけ選択してください")
        row = layout.row(align=True)
        row.operator("cureasing.copy")
        row.operator("cureasing.paste")

class CURVE_OT_EasingCopy(bpy.types.Operator):
    bl_idname = "cureasing.copy"
    bl_label = "Copy"
    def execute(self, context):
        obj = bpy.context.active_object
        animation_data = obj.animation_data
        if  hasattr(animation_data,"action"):
            fcurves = animation_data.action.fcurves
            for curve in fcurves:
                if curve.select:
                    keyframe_count = len(curve.keyframe_points)
                    for i in range(keyframe_count -1):
                        if curve.keyframe_points[i].select_control_point:
                            dic = self.get_ease_settings(curve, i)
                            # テキストをクリップボードに
                            bpy.context.window_manager.clipboard = json.dumps(dic)
                        break
        return {'FINISHED'}
    def get_ease_settings(self, curve, i):
        attr_dic = {}
        point_1 = curve.keyframe_points[i]
        handle_1 = curve.keyframe_points[i].handle_right - point_1.co
        point_2 = curve.keyframe_points[i +1]
        handle_2 = curve.keyframe_points[i +1].handle_left - point_2.co
        diff = point_2.co - point_1.co
        if diff[1] == 0: return()
        attr_dic['interpolation'] = point_1.interpolation #'BEZIER', 'BACK', 'ELASTIC', ...
        attr_dic['back'] = point_1.back #interpolation 'BACK'
        attr_dic['easing'] = point_1.easing
        attr_dic['out_handle'] = [handle_1[0]/diff[0], handle_1[1]/diff[1]]
        attr_dic['out_type'] = point_1.handle_right_type
        attr_dic['in_handle'] = [handle_2[0]/diff[0], handle_2[1]/diff[1]]
        attr_dic['in_type'] = point_2.handle_left_type
        attr_dic['interpolation'] = point_1.interpolation
        attr_dic['amplitude'] = point_1.amplitude #interpolation 'ELASTIC'
        attr_dic['period'] = point_1.period/diff[0] #interpolation 'ELASTIC'
        return attr_dic

class CURVE_OT_EasingPaste(bpy.types.Operator):
    bl_idname = "cureasing.paste"
    bl_label = "Paste"
    def execute(self, context):
        # クリップボードのテキストを利用して生成
        dic = json.loads(bpy.context.window_manager.clipboard)
        obj = bpy.context.active_object
        animation_data = obj.animation_data
        if  hasattr(animation_data,"action"):
            fcurves = animation_data.action.fcurves
            for curve in fcurves:
                if curve.select:
                    keyframe_count = len(curve.keyframe_points)
                    for i in range(keyframe_count -1):
                        if curve.keyframe_points[i].select_control_point:
                            self.set_ease_settings(curve, i, dic)
                        break
        return {'FINISHED'}
    def set_ease_settings(self, curve, i, attr_dic):
        point_1 = curve.keyframe_points[i]
        point_2 = curve.keyframe_points[i +1]
        diff = point_2.co - point_1.co
        if diff[1] == 0: return()
        out_handle = attr_dic['out_handle']
        handle_1 = [ float(out_handle[0]) *diff[0] +point_1.co[0], float(out_handle[1]) *diff[1] +point_1.co[1] ]
        curve.keyframe_points[i].handle_right = handle_1
        point_1.handle_right_type = attr_dic['out_type']

        in_handle = attr_dic['in_handle']
        handle_2 = [ float(in_handle[0]) *diff[0] +point_2.co[0], float(in_handle[1]) *diff[1] +point_2.co[1] ]
        curve.keyframe_points[i +1].handle_left = handle_2
        point_2.handle_left_type = attr_dic['in_type']
        
        point_1.interpolation = attr_dic['interpolation']
        point_1.back = float(attr_dic['back'])
        point_1.easing = attr_dic['easing']
        point_1.interpolation = attr_dic['interpolation']
        point_1.amplitude = float(attr_dic['amplitude'])
        point_1.period = float(attr_dic['period']) *diff[0]

classes = (
    CURVE_PT_EasingCopyPaste,
    CURVE_OT_EasingCopy,
    CURVE_OT_EasingPaste,
    )

    
#####################################
def register():
    Scene = bpy.types.Scene
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    Scene = bpy.types.Scene
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
#######################################

