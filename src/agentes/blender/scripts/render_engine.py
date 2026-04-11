"""
=====================================================
BLENDER RENDER ENGINE — Motor principal de renderização
=====================================================
Executado DENTRO do Blender via: blender --background --python render_engine.py -- <job.json>

Pipeline por job:
  1. Carregar template de cena (.blend)
  2. Importar/gerar modelo 3D do produto
  3. Aplicar materiais PBR
  4. Configurar iluminação
  5. Posicionar câmera(s)
  6. Renderizar cada tipo pedido
  7. Exportar resultados + metadados
=====================================================
"""

import bpy
import json
import sys
import os
import time
import math
from pathlib import Path

# =====================================================
# CONFIGURAÇÃO GLOBAL
# =====================================================

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def parse_args():
    """Extrair argumentos após '--' na linha de comando do Blender."""
    argv = sys.argv
    if "--" in argv:
        return argv[argv.index("--") + 1:]
    return []


def load_job(job_path):
    """Carregar definição do job."""
    with open(job_path, 'r') as f:
        return json.load(f)


# =====================================================
# SCENE SETUP — Configuração da cena
# =====================================================

class SceneSetup:
    """Configura a cena base do Blender para renders de produto."""

    @staticmethod
    def clear_scene():
        """Limpar cena existente."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        # Limpar dados órfãos
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)
        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)

    @staticmethod
    def setup_render_engine(config):
        """Configurar engine de render (Cycles ou EEVEE)."""
        scene = bpy.context.scene
        engine = config.get('engine', 'CYCLES')

        if engine == 'CYCLES':
            scene.render.engine = 'CYCLES'
            scene.cycles.samples = config.get('samples', 128)
            scene.cycles.use_denoising = config.get('denoising', True)

            # Tentar usar GPU se disponível
            prefs = bpy.context.preferences.addons.get('cycles')
            if prefs:
                prefs.preferences.compute_device_type = 'CUDA'  # ou OPTIX, METAL
                bpy.context.scene.cycles.device = 'GPU'
        else:
            scene.render.engine = 'BLENDER_EEVEE'
            scene.eevee.taa_render_samples = config.get('samples', 64)

        # Resolução
        res = config.get('resolution', {'x': 1920, 'y': 1920})
        scene.render.resolution_x = res['x']
        scene.render.resolution_y = res['y']
        scene.render.resolution_percentage = 100

        # Color management
        scene.view_settings.view_transform = config.get('colorManagement', 'Filmic')
        scene.view_settings.look = 'Medium High Contrast'

        # Formato de saída
        scene.render.image_settings.file_format = config.get('imageFormat', 'PNG')
        if config.get('transparentBackground', True):
            scene.render.film_transparent = True
            scene.render.image_settings.color_mode = 'RGBA'

    @staticmethod
    def setup_resolution(resolution):
        """Configurar resolução específica para um render."""
        scene = bpy.context.scene
        scene.render.resolution_x = resolution.get('x', 1920)
        scene.render.resolution_y = resolution.get('y', 1920)


# =====================================================
# LIGHTING — Sistemas de iluminação
# =====================================================

class LightingSetup:
    """Iluminação profissional para fotografia de produto."""

    @staticmethod
    def studio_3point():
        """Iluminação clássica de estúdio — 3 pontos."""
        # Key light — principal (acima e à direita)
        key = bpy.data.lights.new(name="Key_Light", type='AREA')
        key.energy = 500
        key.size = 2.0
        key.color = (1.0, 0.98, 0.95)  # Ligeiramente quente
        key_obj = bpy.data.objects.new("Key_Light", key)
        bpy.context.collection.objects.link(key_obj)
        key_obj.location = (2.0, -1.5, 3.0)
        key_obj.rotation_euler = (math.radians(45), 0, math.radians(25))

        # Fill light — preenchimento (esquerda, mais suave)
        fill = bpy.data.lights.new(name="Fill_Light", type='AREA')
        fill.energy = 200
        fill.size = 3.0
        fill.color = (0.95, 0.97, 1.0)  # Ligeiramente frio
        fill_obj = bpy.data.objects.new("Fill_Light", fill)
        bpy.context.collection.objects.link(fill_obj)
        fill_obj.location = (-2.5, -1.0, 2.0)
        fill_obj.rotation_euler = (math.radians(40), 0, math.radians(-30))

        # Rim light — contorno (trás)
        rim = bpy.data.lights.new(name="Rim_Light", type='AREA')
        rim.energy = 350
        rim.size = 1.5
        rim.color = (1.0, 1.0, 1.0)
        rim_obj = bpy.data.objects.new("Rim_Light", rim)
        bpy.context.collection.objects.link(rim_obj)
        rim_obj.location = (0.5, 2.5, 2.5)
        rim_obj.rotation_euler = (math.radians(-30), 0, math.radians(170))

        return [key_obj, fill_obj, rim_obj]

    @staticmethod
    def studio_soft():
        """Iluminação suave e uniforme — ideal para multi-angle."""
        lights = []
        # 4 painéis de luz ao redor
        positions = [
            (3, 0, 2.5, "Front"),
            (-3, 0, 2.5, "Back"),
            (0, 3, 2.5, "Right"),
            (0, -3, 2.5, "Left"),
        ]
        for x, y, z, name in positions:
            light = bpy.data.lights.new(name=f"Soft_{name}", type='AREA')
            light.energy = 200
            light.size = 4.0
            light.color = (1.0, 1.0, 1.0)
            obj = bpy.data.objects.new(f"Soft_{name}", light)
            bpy.context.collection.objects.link(obj)
            obj.location = (x, y, z)
            # Apontar para o centro
            direction = (-x, -y, -z + 0.5)
            obj.rotation_euler = (
                math.atan2(math.sqrt(direction[0]**2 + direction[1]**2), direction[2]),
                0,
                math.atan2(direction[0], direction[1])
            )
            lights.append(obj)

        # Luz de baixo (bounce suave)
        bounce = bpy.data.lights.new(name="Bounce", type='AREA')
        bounce.energy = 50
        bounce.size = 5.0
        bounce_obj = bpy.data.objects.new("Bounce", bounce)
        bpy.context.collection.objects.link(bounce_obj)
        bounce_obj.location = (0, 0, -0.5)
        bounce_obj.rotation_euler = (math.radians(180), 0, 0)
        lights.append(bounce_obj)

        return lights

    @staticmethod
    def studio_clean():
        """Iluminação limpa e direcional — bom para explosão de peças."""
        key = bpy.data.lights.new(name="Clean_Key", type='SUN')
        key.energy = 3
        key.color = (1.0, 1.0, 1.0)
        key_obj = bpy.data.objects.new("Clean_Key", key)
        bpy.context.collection.objects.link(key_obj)
        key_obj.rotation_euler = (math.radians(50), 0, math.radians(30))

        env = bpy.data.lights.new(name="Clean_Env", type='AREA')
        env.energy = 100
        env.size = 10.0
        env_obj = bpy.data.objects.new("Clean_Env", env)
        bpy.context.collection.objects.link(env_obj)
        env_obj.location = (0, 0, 5)
        env_obj.rotation_euler = (0, 0, 0)

        return [key_obj, env_obj]

    @staticmethod
    def environment_hdri(hdri_path=None):
        """Iluminação ambiente com HDRI — para lifestyle shots."""
        world = bpy.data.worlds.new("HDRI_World")
        bpy.context.scene.world = world
        world.use_nodes = True
        tree = world.node_tree
        tree.nodes.clear()

        # Background node
        bg_node = tree.nodes.new('ShaderNodeBackground')
        bg_node.inputs['Strength'].default_value = 1.0

        output_node = tree.nodes.new('ShaderNodeOutputWorld')

        if hdri_path and os.path.exists(hdri_path):
            # Usar HDRI real
            env_tex = tree.nodes.new('ShaderNodeTexEnvironment')
            env_tex.image = bpy.data.images.load(hdri_path)
            tree.links.new(env_tex.outputs['Color'], bg_node.inputs['Color'])
        else:
            # Gradiente como fallback
            bg_node.inputs['Color'].default_value = (0.8, 0.85, 0.9, 1.0)

        tree.links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

        return world

    @staticmethod
    def get_lighting_setup(name):
        """Factory method — retorna setup de iluminação por nome."""
        setups = {
            'studio_3point': LightingSetup.studio_3point,
            'studio_soft': LightingSetup.studio_soft,
            'studio_clean': LightingSetup.studio_clean,
            'environment_hdri': LightingSetup.environment_hdri,
        }
        return setups.get(name, LightingSetup.studio_3point)()


# =====================================================
# CAMERA — Posicionamento de câmera
# =====================================================

class CameraSetup:
    """Posicionamento profissional de câmera para fotografia de produto."""

    @staticmethod
    def create_camera(name="RenderCamera"):
        """Criar câmera com configurações de fotografia de produto."""
        cam = bpy.data.cameras.new(name)
        cam.lens = 85  # 85mm — lente padrão para produto
        cam.dof.use_dof = True
        cam.dof.aperture_fstop = 5.6
        cam_obj = bpy.data.objects.new(name, cam)
        bpy.context.collection.objects.link(cam_obj)
        bpy.context.scene.camera = cam_obj
        return cam_obj

    @staticmethod
    def position_camera(cam_obj, target_obj, angle='three_quarter', distance='medium'):
        """Posicionar câmera relativa ao objeto."""
        # Calcular bounding box do objeto
        bbox = target_obj.bound_box
        dims = target_obj.dimensions
        center = target_obj.location
        max_dim = max(dims)

        # Distância baseada no tamanho do objeto
        dist_multipliers = {'close': 2.0, 'medium': 3.0, 'far': 5.0, 'scene': 7.0}
        dist = max_dim * dist_multipliers.get(distance, 3.0)

        # Ângulos predefinidos
        angle_configs = {
            'front': (0, math.radians(75), 0),
            'right': (math.radians(90), math.radians(75), 0),
            'back': (math.radians(180), math.radians(75), 0),
            'left': (math.radians(270), math.radians(75), 0),
            'top': (0, math.radians(10), 0),
            'three_quarter': (math.radians(35), math.radians(65), 0),
            'perspective': (math.radians(45), math.radians(55), 0),
            'low_angle': (math.radians(30), math.radians(85), 0),
        }

        azimuth, elevation, roll = angle_configs.get(angle, angle_configs['three_quarter'])

        # Converter coordenadas esféricas para cartesianas
        x = center.x + dist * math.sin(elevation) * math.cos(azimuth)
        y = center.y + dist * math.sin(elevation) * math.sin(azimuth)
        z = center.z + dist * math.cos(elevation)

        cam_obj.location = (x, y, z)

        # Apontar para o centro do objeto
        direction = center - cam_obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()

        # Track to constraint (mais preciso)
        constraint = cam_obj.constraints.new(type='TRACK_TO')
        constraint.target = target_obj
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'

        return cam_obj


# =====================================================
# MATERIALS — Sistema de materiais PBR
# =====================================================

class MaterialFactory:
    """Cria materiais PBR realistas para produtos eletrônicos."""

    @staticmethod
    def plastic_glossy(name="Plastic_Glossy", color=(0.1, 0.1, 0.1, 1.0)):
        """Plástico brilhante — padrão para eletrônicos."""
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        principled.inputs['Base Color'].default_value = color
        principled.inputs['Roughness'].default_value = 0.15
        principled.inputs['Specular IOR Level'].default_value = 0.5
        principled.inputs['Coat Weight'].default_value = 0.3

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        return mat

    @staticmethod
    def plastic_matte(name="Plastic_Matte", color=(0.2, 0.2, 0.2, 1.0)):
        """Plástico fosco — gabinetes, cases."""
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        principled.inputs['Base Color'].default_value = color
        principled.inputs['Roughness'].default_value = 0.7
        principled.inputs['Specular IOR Level'].default_value = 0.2

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        return mat

    @staticmethod
    def metal_brushed(name="Metal_Brushed", color=(0.8, 0.8, 0.82, 1.0)):
        """Metal escovado — alumínio, aço."""
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        principled.inputs['Base Color'].default_value = color
        principled.inputs['Metallic'].default_value = 1.0
        principled.inputs['Roughness'].default_value = 0.3
        principled.inputs['Anisotropic'].default_value = 0.8

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        return mat

    @staticmethod
    def glass_screen(name="Glass_Screen"):
        """Vidro de tela — smartphones, smartwatches."""
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        principled.inputs['Base Color'].default_value = (0.02, 0.02, 0.05, 1.0)
        principled.inputs['Roughness'].default_value = 0.02
        principled.inputs['Specular IOR Level'].default_value = 0.8
        principled.inputs['Coat Weight'].default_value = 1.0
        principled.inputs['Coat Roughness'].default_value = 0.01

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        return mat

    @staticmethod
    def rubber_soft(name="Rubber_Soft", color=(0.05, 0.05, 0.05, 1.0)):
        """Borracha macia — grips, cabos."""
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        principled.inputs['Base Color'].default_value = color
        principled.inputs['Roughness'].default_value = 0.9
        principled.inputs['Specular IOR Level'].default_value = 0.1
        principled.inputs['Sheen Weight'].default_value = 0.3

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        return mat

    @staticmethod
    def led_emissive(name="LED_Glow", color=(0.0, 0.5, 1.0, 1.0), strength=5.0):
        """LED emissivo — indicadores, RGB strips."""
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        principled.inputs['Base Color'].default_value = color
        principled.inputs['Emission Color'].default_value = color
        principled.inputs['Emission Strength'].default_value = strength

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        return mat

    @staticmethod
    def fabric_mesh(name="Fabric_Mesh", color=(0.15, 0.15, 0.18, 1.0)):
        """Tecido mesh — capas de speakers, headbands."""
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        principled.inputs['Base Color'].default_value = color
        principled.inputs['Roughness'].default_value = 0.85
        principled.inputs['Sheen Weight'].default_value = 0.7
        principled.inputs['Sheen Tint'].default_value = 0.3

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        return mat


# =====================================================
# ANIMATIONS — Animações de produto
# =====================================================

class AnimationEngine:
    """Motor de animação para turntable 360° e explosão de peças."""

    @staticmethod
    def turntable_360(target_obj, frames=120, cam_obj=None):
        """Animação de rotação 360° do produto."""
        scene = bpy.context.scene
        scene.frame_start = 1
        scene.frame_end = frames

        # Criar empty no centro do objeto para rotação
        empty = bpy.data.objects.new("Turntable_Pivot", None)
        bpy.context.collection.objects.link(empty)
        empty.location = target_obj.location

        # Parentear produto ao pivot
        target_obj.parent = empty

        # Keyframes de rotação
        empty.rotation_euler = (0, 0, 0)
        empty.keyframe_insert(data_path="rotation_euler", frame=1)

        empty.rotation_euler = (0, 0, math.radians(360))
        empty.keyframe_insert(data_path="rotation_euler", frame=frames)

        # Interpolação linear para rotação suave
        if empty.animation_data and empty.animation_data.action:
            for fc in empty.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'LINEAR'

        return empty

    @staticmethod
    def exploded_view(target_obj, frames=90, explosion_distance=1.5):
        """Animação de explosão — peças se separam do centro."""
        scene = bpy.context.scene
        scene.frame_start = 1
        scene.frame_end = frames

        center = target_obj.location.copy()
        children = list(target_obj.children) if target_obj.children else []

        # Se não tem filhos, simular dividindo o mesh
        if not children and target_obj.type == 'MESH':
            # Separar por loose parts
            bpy.context.view_layer.objects.active = target_obj
            target_obj.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')
            children = [obj for obj in bpy.context.selected_objects if obj != target_obj]

        # Se ainda não tem partes, criar explosão simulada
        if not children:
            children = [target_obj]

        frame_hold = 20       # Frames parado no início
        frame_explode = 40    # Frames da explosão
        frame_hold_out = 30   # Frames parado no final

        for i, child in enumerate(children):
            if child.type != 'MESH':
                continue

            # Posição original
            orig_loc = child.location.copy()

            # Direção de explosão (do centro para fora)
            direction = orig_loc - center
            if direction.length < 0.01:
                # Se está no centro, explode para fora baseado no índice
                angle = (i / max(len(children), 1)) * math.pi * 2
                direction.x = math.cos(angle)
                direction.y = math.sin(angle)
                direction.z = 0.3
            direction.normalize()

            # Posição explodida
            exploded_loc = orig_loc + direction * explosion_distance

            # Frame 1: posição original
            child.location = orig_loc
            child.keyframe_insert(data_path="location", frame=1)

            # Frame hold: ainda na posição original
            child.keyframe_insert(data_path="location", frame=frame_hold)

            # Frame explodido: posição final
            child.location = exploded_loc
            child.keyframe_insert(data_path="location", frame=frame_hold + frame_explode)

            # Suavizar a animação
            if child.animation_data and child.animation_data.action:
                for fc in child.animation_data.action.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'BEZIER'
                        kp.easing = 'EASE_IN_OUT'


# =====================================================
# BACKGROUND — Fundos de cena
# =====================================================

class BackgroundSetup:
    """Configuração de fundos para diferentes tipos de render."""

    @staticmethod
    def gradient_white():
        """Gradiente branco — padrão e-commerce."""
        world = bpy.data.worlds.new("White_Gradient")
        bpy.context.scene.world = world
        world.use_nodes = True
        tree = world.node_tree
        tree.nodes.clear()

        bg = tree.nodes.new('ShaderNodeBackground')
        bg.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        bg.inputs['Strength'].default_value = 0.5

        output = tree.nodes.new('ShaderNodeOutputWorld')
        tree.links.new(bg.outputs['Background'], output.inputs['Surface'])

    @staticmethod
    def gradient_dark():
        """Gradiente escuro — premium look."""
        world = bpy.data.worlds.new("Dark_Gradient")
        bpy.context.scene.world = world
        world.use_nodes = True
        tree = world.node_tree
        tree.nodes.clear()

        # Gradiente com color ramp
        tex_coord = tree.nodes.new('ShaderNodeTexCoord')
        gradient = tree.nodes.new('ShaderNodeTexGradient')
        gradient.gradient_type = 'SPHERICAL'

        ramp = tree.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.03, 1.0)
        ramp.color_ramp.elements[1].color = (0.08, 0.08, 0.1, 1.0)
        ramp.color_ramp.elements[1].position = 0.7

        bg = tree.nodes.new('ShaderNodeBackground')
        bg.inputs['Strength'].default_value = 1.0

        output = tree.nodes.new('ShaderNodeOutputWorld')

        tree.links.new(tex_coord.outputs['Generated'], gradient.inputs['Vector'])
        tree.links.new(gradient.outputs['Fac'], ramp.inputs['Fac'])
        tree.links.new(ramp.outputs['Color'], bg.inputs['Color'])
        tree.links.new(bg.outputs['Background'], output.inputs['Surface'])

    @staticmethod
    def transparent():
        """Fundo transparente — para composição."""
        bpy.context.scene.render.film_transparent = True
        world = bpy.data.worlds.new("Transparent")
        bpy.context.scene.world = world
        world.use_nodes = True
        tree = world.node_tree
        tree.nodes.clear()

        bg = tree.nodes.new('ShaderNodeBackground')
        bg.inputs['Color'].default_value = (0, 0, 0, 0)
        bg.inputs['Strength'].default_value = 0.0

        output = tree.nodes.new('ShaderNodeOutputWorld')
        tree.links.new(bg.outputs['Background'], output.inputs['Surface'])

    @staticmethod
    def get_background(name):
        setups = {
            'gradient_white': BackgroundSetup.gradient_white,
            'gradient_dark': BackgroundSetup.gradient_dark,
            'transparent': BackgroundSetup.transparent,
            'scene': BackgroundSetup.gradient_white,
        }
        return setups.get(name, BackgroundSetup.gradient_white)()


# =====================================================
# PRODUCT GENERATOR — Gera geometria procedural
# =====================================================

class ProductGenerator:
    """Gera modelos 3D procedurais baseados na categoria do produto."""

    @staticmethod
    def generate(template, product_info):
        """Factory — gera modelo baseado no template."""
        generators = {
            'electronics_small': ProductGenerator._electronics_small,
            'audio_wearable': ProductGenerator._audio_wearable,
            'audio_speaker': ProductGenerator._audio_speaker,
            'lighting_strip': ProductGenerator._lighting_strip,
            'wearable_watch': ProductGenerator._wearable_watch,
            'smarthome_plug': ProductGenerator._smarthome_plug,
            'gaming_controller': ProductGenerator._gaming_controller,
            'gaming_mouse': ProductGenerator._gaming_mouse,
            'phone_case': ProductGenerator._phone_case,
            'generic_product': ProductGenerator._generic_product,
        }

        gen_func = generators.get(template, ProductGenerator._generic_product)
        return gen_func(product_info)

    @staticmethod
    def _electronics_small(info):
        """Eletrônico pequeno — caixa arredondada com LED."""
        # Corpo principal
        bpy.ops.mesh.primitive_cube_add(size=1)
        body = bpy.context.active_object
        body.name = f"Product_{info.get('sku', 'unknown')}"
        body.scale = (0.6, 0.6, 0.25)

        # Bevel para arredondar
        bpy.ops.object.modifier_add(type='BEVEL')
        body.modifiers["Bevel"].width = 0.05
        body.modifiers["Bevel"].segments = 4
        bpy.ops.object.modifier_apply(modifier="Bevel")

        # Material plástico
        mat = MaterialFactory.plastic_glossy("Body_Plastic", (0.15, 0.15, 0.18, 1.0))
        body.data.materials.append(mat)

        # LED indicador
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.01)
        led = bpy.context.active_object
        led.name = "LED_Indicator"
        led.location = (0, 0.25, 0.13)
        led_mat = MaterialFactory.led_emissive("LED_Green", (0.0, 1.0, 0.3, 1.0), 3.0)
        led.data.materials.append(led_mat)
        led.parent = body

        # Aplicar subdivisão para suavidade
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.modifier_add(type='SUBSURF')
        body.modifiers["Subdivision"].levels = 2

        return body

    @staticmethod
    def _audio_wearable(info):
        """Fone/earbuds — forma orgânica."""
        # Earbud esquerdo
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, segments=32, ring_count=16)
        bud = bpy.context.active_object
        bud.name = f"Product_{info.get('sku', 'earbud')}"
        bud.scale = (1.0, 0.8, 0.9)

        mat = MaterialFactory.plastic_glossy("Earbud_Body", (0.95, 0.95, 0.97, 1.0))
        bud.data.materials.append(mat)

        # Ponta de silicone
        bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0.05, depth=0.1)
        tip = bpy.context.active_object
        tip.name = "Silicone_Tip"
        tip.location = (0.15, 0, 0)
        tip.rotation_euler = (0, math.radians(90), 0)
        tip_mat = MaterialFactory.rubber_soft("Silicone", (0.3, 0.3, 0.35, 1.0))
        tip.data.materials.append(tip_mat)
        tip.parent = bud

        return bud

    @staticmethod
    def _audio_speaker(info):
        """Speaker/caixa de som cilíndrica."""
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, vertices=64)
        body = bpy.context.active_object
        body.name = f"Product_{info.get('sku', 'speaker')}"

        # Bevel
        bpy.ops.object.modifier_add(type='BEVEL')
        body.modifiers["Bevel"].width = 0.02
        body.modifiers["Bevel"].segments = 3
        bpy.ops.object.modifier_apply(modifier="Bevel")

        mat = MaterialFactory.fabric_mesh("Speaker_Fabric", (0.1, 0.1, 0.12, 1.0))
        body.data.materials.append(mat)

        # Grille do speaker
        bpy.ops.mesh.primitive_circle_add(radius=0.25, vertices=64)
        grille = bpy.context.active_object
        grille.name = "Speaker_Grille"
        grille.location = (0, 0, 0.26)
        grille_mat = MaterialFactory.metal_brushed("Grille_Metal", (0.5, 0.5, 0.52, 1.0))
        grille.data.materials.append(grille_mat)
        grille.parent = body

        return body

    @staticmethod
    def _lighting_strip(info):
        """Fita LED — curva com LEDs emissivos."""
        # Curva base
        bpy.ops.curve.primitive_bezier_curve_add()
        curve = bpy.context.active_object
        curve.name = f"Product_{info.get('sku', 'led_strip')}"
        curve.data.bevel_depth = 0.02
        curve.data.bevel_resolution = 4

        mat = MaterialFactory.rubber_soft("Strip_Base", (0.9, 0.9, 0.9, 1.0))
        curve.data.materials.append(mat)

        # LEDs ao longo da curva
        colors = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 0, 1, 1), (0, 1, 1, 1)]
        for i in range(10):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.01)
            led = bpy.context.active_object
            led.name = f"LED_{i}"
            led.location = (-1 + i * 0.22, 0, 0.025)
            led_mat = MaterialFactory.led_emissive(f"LED_Color_{i}", colors[i % len(colors)], 8.0)
            led.data.materials.append(led_mat)
            led.parent = curve

        return curve

    @staticmethod
    def _wearable_watch(info):
        """Smartwatch — corpo redondo com tela."""
        # Corpo do relógio
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.06, vertices=64)
        body = bpy.context.active_object
        body.name = f"Product_{info.get('sku', 'watch')}"

        mat = MaterialFactory.metal_brushed("Watch_Case", (0.6, 0.6, 0.65, 1.0))
        body.data.materials.append(mat)

        # Tela
        bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.005, vertices=64)
        screen = bpy.context.active_object
        screen.name = "Watch_Screen"
        screen.location = (0, 0, 0.033)
        screen_mat = MaterialFactory.glass_screen("Screen_Glass")
        screen.data.materials.append(screen_mat)
        screen.parent = body

        # Botão lateral
        bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.04, vertices=16)
        button = bpy.context.active_object
        button.name = "Watch_Button"
        button.location = (0.21, 0, 0)
        button.rotation_euler = (0, math.radians(90), 0)
        btn_mat = MaterialFactory.metal_brushed("Button_Metal", (0.5, 0.5, 0.55, 1.0))
        button.data.materials.append(btn_mat)
        button.parent = body

        # Pulseira (simplificada)
        bpy.ops.mesh.primitive_cube_add(size=1)
        strap = bpy.context.active_object
        strap.name = "Watch_Strap"
        strap.scale = (0.12, 0.5, 0.015)
        strap.location = (0, 0.45, 0)
        strap_mat = MaterialFactory.rubber_soft("Strap_Rubber", (0.05, 0.05, 0.06, 1.0))
        strap.data.materials.append(strap_mat)
        strap.parent = body

        return body

    @staticmethod
    def _smarthome_plug(info):
        """Smart plug — tomada inteligente."""
        # Corpo
        bpy.ops.mesh.primitive_cube_add(size=1)
        body = bpy.context.active_object
        body.name = f"Product_{info.get('sku', 'plug')}"
        body.scale = (0.35, 0.35, 0.5)

        bpy.ops.object.modifier_add(type='BEVEL')
        body.modifiers["Bevel"].width = 0.04
        body.modifiers["Bevel"].segments = 3
        bpy.ops.object.modifier_apply(modifier="Bevel")

        mat = MaterialFactory.plastic_glossy("Plug_Body", (0.95, 0.95, 0.97, 1.0))
        body.data.materials.append(mat)

        # Botão on/off
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.02, vertices=32)
        btn = bpy.context.active_object
        btn.name = "Power_Button"
        btn.location = (0, 0, 0.26)
        btn_mat = MaterialFactory.plastic_matte("Button_Matte", (0.8, 0.8, 0.82, 1.0))
        btn.data.materials.append(btn_mat)
        btn.parent = body

        # LED de status
        bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.005, vertices=16)
        led = bpy.context.active_object
        led.name = "Status_LED"
        led.location = (0, 0.17, 0.26)
        led_mat = MaterialFactory.led_emissive("Status_Blue", (0.0, 0.4, 1.0, 1.0), 5.0)
        led.data.materials.append(led_mat)
        led.parent = body

        return body

    @staticmethod
    def _gaming_controller(info):
        """Controle de jogo — forma ergonômica."""
        # Corpo principal (simplificado)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25)
        body = bpy.context.active_object
        body.name = f"Product_{info.get('sku', 'controller')}"
        body.scale = (1.5, 1.0, 0.4)

        mat = MaterialFactory.plastic_matte("Controller_Body", (0.08, 0.08, 0.1, 1.0))
        body.data.materials.append(mat)

        # Analógicos
        for x_pos in [-0.12, 0.12]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.03, vertices=32)
            stick = bpy.context.active_object
            stick.name = f"Analog_{'L' if x_pos < 0 else 'R'}"
            stick.location = (x_pos, -0.05, 0.11)
            stick_mat = MaterialFactory.rubber_soft("Stick_Rubber")
            stick.data.materials.append(stick_mat)
            stick.parent = body

        # Botões ABXY
        colors = [(0, 0.5, 0, 1), (1, 0, 0, 1), (0, 0, 1, 1), (1, 1, 0, 1)]
        positions = [(0.18, -0.02, 0.1), (0.22, 0.02, 0.1), (0.14, 0.02, 0.1), (0.18, 0.06, 0.1)]
        for i, (pos, col) in enumerate(zip(positions, colors)):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.008, vertices=16)
            btn = bpy.context.active_object
            btn.name = f"Button_{i}"
            btn.location = pos
            btn_mat = MaterialFactory.plastic_glossy(f"Btn_{i}", col)
            btn.data.materials.append(btn_mat)
            btn.parent = body

        return body

    @staticmethod
    def _gaming_mouse(info):
        """Mouse gamer — forma ergonômica com RGB."""
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15)
        body = bpy.context.active_object
        body.name = f"Product_{info.get('sku', 'mouse')}"
        body.scale = (0.7, 1.2, 0.4)

        mat = MaterialFactory.plastic_matte("Mouse_Body", (0.05, 0.05, 0.07, 1.0))
        body.data.materials.append(mat)

        # Scroll wheel
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.04, vertices=32)
        scroll = bpy.context.active_object
        scroll.name = "Scroll_Wheel"
        scroll.location = (0, -0.05, 0.065)
        scroll.rotation_euler = (math.radians(90), 0, 0)
        scroll_mat = MaterialFactory.rubber_soft("Scroll_Rubber")
        scroll.data.materials.append(scroll_mat)
        scroll.parent = body

        # RGB strip
        bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.005)
        rgb = bpy.context.active_object
        rgb.name = "RGB_Strip"
        rgb.location = (0, 0, 0.01)
        rgb.scale = (0.7, 1.2, 1.0)
        rgb_mat = MaterialFactory.led_emissive("RGB_Purple", (0.5, 0.0, 1.0, 1.0), 10.0)
        rgb.data.materials.append(rgb_mat)
        rgb.parent = body

        return body

    @staticmethod
    def _phone_case(info):
        """Capinha de celular."""
        bpy.ops.mesh.primitive_cube_add(size=1)
        body = bpy.context.active_object
        body.name = f"Product_{info.get('sku', 'case')}"
        body.scale = (0.4, 0.8, 0.05)

        bpy.ops.object.modifier_add(type='BEVEL')
        body.modifiers["Bevel"].width = 0.03
        body.modifiers["Bevel"].segments = 4
        bpy.ops.object.modifier_apply(modifier="Bevel")

        mat = MaterialFactory.plastic_matte("Case_Body", (0.1, 0.2, 0.4, 1.0))
        body.data.materials.append(mat)

        # Cutout da câmera
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.06, vertices=32)
        cam_cutout = bpy.context.active_object
        cam_cutout.name = "Camera_Cutout"
        cam_cutout.location = (0.1, 0.3, 0)
        cam_mat = MaterialFactory.plastic_glossy("Cam_Ring", (0.3, 0.3, 0.32, 1.0))
        cam_cutout.data.materials.append(cam_mat)
        cam_cutout.parent = body

        return body

    @staticmethod
    def _generic_product(info):
        """Produto genérico — caixa arredondada."""
        bpy.ops.mesh.primitive_cube_add(size=1)
        body = bpy.context.active_object
        body.name = f"Product_{info.get('sku', 'generic')}"
        body.scale = (0.5, 0.5, 0.3)

        bpy.ops.object.modifier_add(type='BEVEL')
        body.modifiers["Bevel"].width = 0.04
        body.modifiers["Bevel"].segments = 3
        bpy.ops.object.modifier_apply(modifier="Bevel")

        bpy.ops.object.modifier_add(type='SUBSURF')
        body.modifiers["Subdivision"].levels = 2

        mat = MaterialFactory.plastic_glossy("Generic_Body", (0.2, 0.2, 0.22, 1.0))
        body.data.materials.append(mat)

        return body


# =====================================================
# RENDER JOB EXECUTOR — Executa o pipeline completo
# =====================================================

class RenderJobExecutor:
    """Executa um job completo de render."""

    def __init__(self, job_data):
        self.job = job_data
        self.product_info = job_data.get('product', {})
        self.template = job_data.get('template', 'generic_product')
        self.renders = job_data.get('renders', [])
        self.config = job_data.get('config', {})
        self.output_dir = OUTPUT_DIR / self.product_info.get('sku', 'unknown')
        self.results = {'renders': [], 'animations': [], 'renderTimeMs': 0}

    def execute(self):
        """Pipeline completo de render."""
        start_time = time.time()

        try:
            # 1. Limpar e configurar cena
            SceneSetup.clear_scene()
            SceneSetup.setup_render_engine(self.config)

            # 2. Gerar modelo 3D do produto
            product_obj = ProductGenerator.generate(self.template, self.product_info)
            print(f"[BLENDER] Modelo gerado: {product_obj.name}")

            # 3. Criar câmera
            cam = CameraSetup.create_camera()

            # 4. Criar diretório de output
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # 5. Executar cada render pedido
            for render_spec in self.renders:
                render_id = render_spec.get('id', 'unknown')
                print(f"[BLENDER] Renderizando: {render_id}")

                if render_id in ('turntable_360', 'exploded_view'):
                    self._render_animation(product_obj, cam, render_spec)
                elif render_id == 'multi_angle':
                    self._render_multi_angle(product_obj, cam, render_spec)
                else:
                    self._render_static(product_obj, cam, render_spec)

            # 6. Calcular tempo total
            self.results['renderTimeMs'] = int((time.time() - start_time) * 1000)
            self.results['status'] = 'completed'

            print(f"[BLENDER] Job completo: {len(self.results['renders'])} renders, "
                  f"{len(self.results['animations'])} animações em {self.results['renderTimeMs']}ms")

        except Exception as e:
            self.results['status'] = 'failed'
            self.results['error'] = str(e)
            print(f"[BLENDER] ERRO: {e}")

        return self.results

    def _render_static(self, product_obj, cam, spec):
        """Render estático único."""
        # Configurar resolução
        res = spec.get('resolution', self.config.get('resolution', {'x': 1920, 'y': 1920}))
        SceneSetup.setup_resolution(res)

        # Samples específicos
        if spec.get('samples'):
            bpy.context.scene.cycles.samples = spec['samples']

        # Iluminação
        lighting = spec.get('lighting', 'studio_3point')
        LightingSetup.get_lighting_setup(lighting)

        # Background
        bg = spec.get('background', 'gradient_white')
        BackgroundSetup.get_background(bg)

        # Posicionar câmera
        camera_config = spec.get('camera', {'angle': 'three_quarter', 'distance': 'medium'})
        CameraSetup.position_camera(cam, product_obj, **camera_config)

        # Render
        output_path = str(self.output_dir / f"{spec['id']}.png")
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)

        self.results['renders'].append({
            'type': spec['id'],
            'url': output_path,
            'resolution': res,
            'fileSize': os.path.getsize(output_path) if os.path.exists(output_path) else 0
        })

    def _render_multi_angle(self, product_obj, cam, spec):
        """Render de múltiplos ângulos."""
        angles = spec.get('angles', ['front', 'right', 'back', 'top'])
        res = spec.get('resolution', {'x': 1200, 'y': 1200})
        SceneSetup.setup_resolution(res)

        if spec.get('samples'):
            bpy.context.scene.cycles.samples = spec['samples']

        lighting = spec.get('lighting', 'studio_soft')
        LightingSetup.get_lighting_setup(lighting)

        bg = spec.get('background', 'transparent')
        BackgroundSetup.get_background(bg)

        for angle in angles:
            CameraSetup.position_camera(cam, product_obj, angle=angle, distance='medium')

            output_path = str(self.output_dir / f"multi_angle_{angle}.png")
            bpy.context.scene.render.filepath = output_path
            bpy.ops.render.render(write_still=True)

            self.results['renders'].append({
                'type': f'multi_angle_{angle}',
                'url': output_path,
                'resolution': res,
                'fileSize': os.path.getsize(output_path) if os.path.exists(output_path) else 0
            })

    def _render_animation(self, product_obj, cam, spec):
        """Render de animação (turntable ou explosão)."""
        render_id = spec.get('id', 'turntable_360')
        frames = spec.get('frames', 120)
        res = spec.get('resolution', {'x': 1080, 'y': 1080})
        SceneSetup.setup_resolution(res)

        if spec.get('samples'):
            bpy.context.scene.cycles.samples = spec['samples']

        lighting = spec.get('lighting', 'studio_3point')
        LightingSetup.get_lighting_setup(lighting)

        bg = spec.get('background', 'gradient_dark')
        BackgroundSetup.get_background(bg)

        # Posicionar câmera
        CameraSetup.position_camera(cam, product_obj, angle='three_quarter', distance='medium')

        # Criar animação
        if render_id == 'turntable_360':
            AnimationEngine.turntable_360(product_obj, frames, cam)
        elif render_id == 'exploded_view':
            AnimationEngine.exploded_view(product_obj, frames)

        # Configurar output de vídeo
        scene = bpy.context.scene
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
        scene.render.fps = self.config.get('fps', 30)

        output_path = str(self.output_dir / f"{render_id}.mp4")
        scene.render.filepath = output_path

        # Render animação
        bpy.ops.render.render(animation=True)

        self.results['animations'].append({
            'type': render_id,
            'url': output_path,
            'duration': frames / scene.render.fps,
            'fps': scene.render.fps,
            'fileSize': os.path.getsize(output_path) if os.path.exists(output_path) else 0
        })


# =====================================================
# MAIN — Ponto de entrada
# =====================================================

if __name__ == "__main__":
    args = parse_args()

    if not args:
        print("[BLENDER] Uso: blender --background --python render_engine.py -- job.json")
        sys.exit(1)

    job_path = args[0]
    print(f"[BLENDER] Carregando job: {job_path}")

    job_data = load_job(job_path)
    executor = RenderJobExecutor(job_data)
    results = executor.execute()

    # Salvar resultados
    result_path = job_path.replace('.json', '_result.json')
    with open(result_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"[BLENDER] Resultados salvos em: {result_path}")
