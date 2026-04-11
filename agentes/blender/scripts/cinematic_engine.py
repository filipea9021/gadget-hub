"""
=====================================================
CINEMATIC ENGINE — Motor de vídeos cinematográficos 3D
=====================================================
Extensão do render_engine.py com efeitos avançados:

  • Iluminação dual-tone (frio/quente sci-fi)
  • Energy core (núcleo de emissão no centro)
  • Partículas (sparks, poeira, fragmentos)
  • Câmera cinematográfica (zoom lento, rotação suave)
  • Desmontagem procedural (Geometry Nodes / keyframes)
  • Camadas internas (wireframe, bevel, displace)
  • Motion blur
  • Sistema de templates reutilizáveis

Uso:
  blender --background --python cinematic_engine.py -- cinematic_job.json
=====================================================
"""

import bpy
import bmesh
import json
import sys
import os
import math
import time
import random
from pathlib import Path
from mathutils import Vector, Euler

# Importar módulos base
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from render_engine import (
    SceneSetup, CameraSetup, MaterialFactory,
    ProductGenerator, BackgroundSetup, parse_args, load_job
)

OUTPUT_DIR = Path(__file__).parent.parent / "output"


# =====================================================
# PALETAS DE COR CINEMATOGRÁFICAS
# =====================================================

COLOR_PALETTES = {
    "tech_blue": {
        "name": "Tech Blue",
        "primary": (0.0, 0.4, 1.0, 1.0),       # Azul elétrico
        "secondary": (0.0, 0.7, 1.0, 1.0),      # Azul claro
        "accent": (1.0, 0.6, 0.0, 1.0),          # Laranja quente
        "core": (0.2, 0.6, 1.0, 1.0),            # Core azul
        "light_cold": (0.3, 0.5, 1.0),           # Luz fria
        "light_warm": (1.0, 0.6, 0.2),           # Luz quente
    },
    "energy_orange": {
        "name": "Energy Orange",
        "primary": (1.0, 0.4, 0.0, 1.0),
        "secondary": (1.0, 0.7, 0.2, 1.0),
        "accent": (0.0, 0.5, 1.0, 1.0),
        "core": (1.0, 0.5, 0.1, 1.0),
        "light_cold": (0.2, 0.3, 0.8),
        "light_warm": (1.0, 0.5, 0.1),
    },
    "cyber_purple": {
        "name": "Cyber Purple",
        "primary": (0.5, 0.0, 1.0, 1.0),
        "secondary": (0.8, 0.2, 1.0, 1.0),
        "accent": (0.0, 1.0, 0.8, 1.0),
        "core": (0.6, 0.1, 1.0, 1.0),
        "light_cold": (0.4, 0.0, 0.8),
        "light_warm": (0.8, 0.2, 1.0),
    },
    "matrix_green": {
        "name": "Matrix Green",
        "primary": (0.0, 1.0, 0.3, 1.0),
        "secondary": (0.2, 0.8, 0.4, 1.0),
        "accent": (0.0, 0.5, 0.2, 1.0),
        "core": (0.1, 1.0, 0.4, 1.0),
        "light_cold": (0.0, 0.6, 0.3),
        "light_warm": (0.3, 1.0, 0.5),
    },
    "fire_red": {
        "name": "Fire Red",
        "primary": (1.0, 0.1, 0.0, 1.0),
        "secondary": (1.0, 0.3, 0.1, 1.0),
        "accent": (1.0, 0.8, 0.0, 1.0),
        "core": (1.0, 0.2, 0.05, 1.0),
        "light_cold": (0.2, 0.1, 0.5),
        "light_warm": (1.0, 0.3, 0.05),
    },
    "ice_white": {
        "name": "Ice White",
        "primary": (0.8, 0.9, 1.0, 1.0),
        "secondary": (0.6, 0.8, 1.0, 1.0),
        "accent": (0.0, 0.6, 1.0, 1.0),
        "core": (0.9, 0.95, 1.0, 1.0),
        "light_cold": (0.7, 0.85, 1.0),
        "light_warm": (0.9, 0.9, 1.0),
    },
}


# =====================================================
# CINEMATIC LIGHTING — Iluminação dual-tone sci-fi
# =====================================================

class CinematicLighting:
    """Iluminação cinematográfica com contraste frio/quente."""

    @staticmethod
    def dual_tone(palette_name="tech_blue", intensity=1.0):
        """Setup dual-tone: luz fria de um lado, quente do outro + HDRI."""
        palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["tech_blue"])
        lights = []

        # === LUZ FRIA (lado esquerdo) ===
        cold = bpy.data.lights.new(name="Cold_Light", type='AREA')
        cold.energy = 800 * intensity
        cold.size = 3.0
        cold.color = palette["light_cold"]
        cold_obj = bpy.data.objects.new("Cold_Light", cold)
        bpy.context.collection.objects.link(cold_obj)
        cold_obj.location = (-3.5, -1.0, 2.5)
        cold_obj.rotation_euler = (math.radians(50), 0, math.radians(-40))
        lights.append(cold_obj)

        # === LUZ QUENTE (lado direito) ===
        warm = bpy.data.lights.new(name="Warm_Light", type='AREA')
        warm.energy = 600 * intensity
        warm.size = 2.5
        warm.color = palette["light_warm"]
        warm_obj = bpy.data.objects.new("Warm_Light", warm)
        bpy.context.collection.objects.link(warm_obj)
        warm_obj.location = (3.0, 1.5, 2.0)
        warm_obj.rotation_euler = (math.radians(45), 0, math.radians(150))
        lights.append(warm_obj)

        # === RIM LIGHT (contorno de trás) ===
        rim = bpy.data.lights.new(name="Rim_Cinematic", type='AREA')
        rim.energy = 400 * intensity
        rim.size = 4.0
        rim.color = palette["light_cold"]
        rim_obj = bpy.data.objects.new("Rim_Cinematic", rim)
        bpy.context.collection.objects.link(rim_obj)
        rim_obj.location = (0, 3.0, 1.5)
        rim_obj.rotation_euler = (math.radians(-20), 0, math.radians(180))
        lights.append(rim_obj)

        # === FILL FRACO (preenche sombras sem matar contraste) ===
        fill = bpy.data.lights.new(name="Fill_Subtle", type='AREA')
        fill.energy = 100 * intensity
        fill.size = 6.0
        fill.color = (0.5, 0.5, 0.6)
        fill_obj = bpy.data.objects.new("Fill_Subtle", fill)
        bpy.context.collection.objects.link(fill_obj)
        fill_obj.location = (0, 0, 5.0)
        fill_obj.rotation_euler = (0, 0, 0)
        lights.append(fill_obj)

        return lights

    @staticmethod
    def setup_world_dark_gradient(palette_name="tech_blue"):
        """Fundo escuro com leve gradiente colorido."""
        palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["tech_blue"])
        world = bpy.data.worlds.new("Cinematic_World")
        bpy.context.scene.world = world
        world.use_nodes = True
        tree = world.node_tree
        tree.nodes.clear()

        # Gradiente radial escuro com hint de cor
        tex_coord = tree.nodes.new('ShaderNodeTexCoord')
        gradient = tree.nodes.new('ShaderNodeTexGradient')
        gradient.gradient_type = 'SPHERICAL'

        ramp = tree.nodes.new('ShaderNodeValToRGB')
        # Centro: quase preto
        ramp.color_ramp.elements[0].color = (0.005, 0.005, 0.01, 1.0)
        ramp.color_ramp.elements[0].position = 0.0
        # Borda: leve hint da cor da paleta
        hint_r = palette["light_cold"][0] * 0.03
        hint_g = palette["light_cold"][1] * 0.03
        hint_b = palette["light_cold"][2] * 0.03
        ramp.color_ramp.elements[1].color = (hint_r, hint_g, hint_b, 1.0)
        ramp.color_ramp.elements[1].position = 0.8

        bg = tree.nodes.new('ShaderNodeBackground')
        bg.inputs['Strength'].default_value = 1.0

        output = tree.nodes.new('ShaderNodeOutputWorld')

        tree.links.new(tex_coord.outputs['Generated'], gradient.inputs['Vector'])
        tree.links.new(gradient.outputs['Fac'], ramp.inputs['Fac'])
        tree.links.new(ramp.outputs['Color'], bg.inputs['Color'])
        tree.links.new(bg.outputs['Background'], output.inputs['Surface'])

        return world


# =====================================================
# ENERGY CORE — Núcleo de energia brilhante
# =====================================================

class EnergyCore:
    """Cria o efeito de núcleo energético no centro do objeto."""

    @staticmethod
    def create(location=(0, 0, 0), palette_name="tech_blue", size=0.15, strength=20.0):
        """Esfera emissiva central com glow volumétrico."""
        palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["tech_blue"])

        # === CORE PRINCIPAL ===
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=size, segments=32, ring_count=16, location=location
        )
        core = bpy.context.active_object
        core.name = "Energy_Core"

        # Material emissivo
        mat = bpy.data.materials.new("Core_Emission")
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        principled.inputs['Base Color'].default_value = palette["core"]
        principled.inputs['Emission Color'].default_value = palette["core"]
        principled.inputs['Emission Strength'].default_value = strength
        principled.inputs['Roughness'].default_value = 0.0

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        core.data.materials.append(mat)

        # === GLOW EXTERNO (esfera maior, semi-transparente) ===
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=size * 2.5, segments=32, ring_count=16, location=location
        )
        glow = bpy.context.active_object
        glow.name = "Energy_Glow"

        glow_mat = bpy.data.materials.new("Core_Glow")
        glow_mat.use_nodes = True
        glow_mat.blend_method = 'BLEND'  # Para EEVEE
        tree = glow_mat.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')

        # Mix de emissão com transparência
        mix = nodes.new('ShaderNodeMixShader')
        mix.inputs['Fac'].default_value = 0.85  # Maioria transparente

        transparent = nodes.new('ShaderNodeBsdfTransparent')

        emission = nodes.new('ShaderNodeEmission')
        emission.inputs['Color'].default_value = palette["core"]
        emission.inputs['Strength'].default_value = strength * 0.3

        links.new(transparent.outputs['BSDF'], mix.inputs[1])
        links.new(emission.outputs['Emission'], mix.inputs[2])
        links.new(mix.outputs['Shader'], output.inputs['Surface'])

        glow.data.materials.append(glow_mat)
        glow.parent = core

        # === ANIMAÇÃO DO CORE (pulsar) ===
        EnergyCore._animate_pulse(core, glow, frames=120)

        return core

    @staticmethod
    def _animate_pulse(core, glow, frames=120):
        """Pulso sutil — o core 'respira'."""
        scene = bpy.context.scene

        for frame in range(1, frames + 1, 10):
            t = frame / frames
            pulse = 1.0 + 0.08 * math.sin(t * math.pi * 6)  # 3 pulsos completos

            core.scale = (pulse, pulse, pulse)
            core.keyframe_insert(data_path="scale", frame=frame)

            glow_pulse = 1.0 + 0.15 * math.sin(t * math.pi * 6)
            glow.scale = (glow_pulse, glow_pulse, glow_pulse)
            glow.keyframe_insert(data_path="scale", frame=frame)


# =====================================================
# PARTICLE SYSTEMS — Efeitos de partículas
# =====================================================

class ParticleEffects:
    """Sistema de partículas cinematográficas."""

    @staticmethod
    def sparks(emitter_obj, palette_name="tech_blue", count=200, lifetime=60):
        """Sparks/faíscas saindo do centro."""
        palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["tech_blue"])

        # Criar partículas no emitter
        mod = emitter_obj.modifiers.new("Sparks", type='PARTICLE_SYSTEM')
        ps = mod.particle_system.settings

        ps.count = count
        ps.lifetime = lifetime
        ps.frame_start = 1
        ps.frame_end = 120
        ps.emit_from = 'VOLUME'

        # Velocidade
        ps.normal_factor = 2.0
        ps.factor_random = 1.5
        ps.tangent_factor = 0.5

        # Tamanho
        ps.particle_size = 0.008
        ps.size_random = 0.5

        # Física
        ps.physics_type = 'NEWTON'
        ps.mass = 0.01
        ps.effector_weights.gravity = 0.3

        # Material emissivo para partículas
        spark_mat = MaterialFactory.led_emissive(
            "Spark_Material", palette["primary"], 15.0
        )
        if not emitter_obj.data.materials:
            emitter_obj.data.materials.append(spark_mat)

        return mod

    @staticmethod
    def dust(scene_center=(0, 0, 0), palette_name="tech_blue", count=500):
        """Poeira flutuante — partículas lentas no ambiente."""
        # Criar emitter invisível grande
        bpy.ops.mesh.primitive_cube_add(size=6, location=scene_center)
        dust_emitter = bpy.context.active_object
        dust_emitter.name = "Dust_Emitter"
        dust_emitter.hide_render = True
        dust_emitter.display_type = 'WIRE'

        mod = dust_emitter.modifiers.new("Dust", type='PARTICLE_SYSTEM')
        ps = mod.particle_system.settings

        ps.count = count
        ps.lifetime = 200
        ps.frame_start = -50  # Já começa com partículas
        ps.frame_end = 10
        ps.emit_from = 'VOLUME'

        # Velocidade muito baixa (flutuando)
        ps.normal_factor = 0.05
        ps.factor_random = 0.1
        ps.brownian_factor = 0.3  # Movimento browniano

        # Tamanho pequeno
        ps.particle_size = 0.003
        ps.size_random = 0.8

        # Sem gravidade
        ps.physics_type = 'NEWTON'
        ps.effector_weights.gravity = 0.0

        # Material sutil
        palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["tech_blue"])
        dust_mat = bpy.data.materials.new("Dust_Material")
        dust_mat.use_nodes = True
        tree = dust_mat.node_tree
        nodes = tree.nodes
        links = tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.85, 1.0)
        principled.inputs['Emission Color'].default_value = palette["secondary"]
        principled.inputs['Emission Strength'].default_value = 0.5
        principled.inputs['Alpha'].default_value = 0.4
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])

        dust_emitter.data.materials.append(dust_mat)

        return dust_emitter

    @staticmethod
    def fragments(emitter_obj, count=50, lifetime=90):
        """Fragmentos — pedaços maiores saindo lentamente."""
        mod = emitter_obj.modifiers.new("Fragments", type='PARTICLE_SYSTEM')
        ps = mod.particle_system.settings

        ps.count = count
        ps.lifetime = lifetime
        ps.frame_start = 15  # Começa depois da explosão
        ps.frame_end = 50
        ps.emit_from = 'FACE'

        ps.normal_factor = 0.8
        ps.factor_random = 0.5
        ps.tangent_factor = 0.3

        ps.particle_size = 0.02
        ps.size_random = 0.7

        ps.physics_type = 'NEWTON'
        ps.mass = 0.1
        ps.effector_weights.gravity = 0.1

        # Rotação das partículas
        ps.use_rotations = True
        ps.rotation_factor_random = 1.0
        ps.angular_velocity_mode = 'VELOCITY'
        ps.angular_velocity_factor = 2.0

        return mod


# =====================================================
# CINEMATIC CAMERA — Câmera com movimento cinematográfico
# =====================================================

class CinematicCamera:
    """Câmera animada com movimentos cinematográficos suaves."""

    @staticmethod
    def create(target_location=(0, 0, 0)):
        """Criar câmera cinematográfica com DOF."""
        cam = bpy.data.cameras.new("Cinematic_Cam")
        cam.lens = 50            # 50mm — look cinematográfico
        cam.dof.use_dof = True
        cam.dof.aperture_fstop = 2.8  # DOF raso para look premium
        cam.sensor_width = 36    # Full frame

        cam_obj = bpy.data.objects.new("Cinematic_Cam", cam)
        bpy.context.collection.objects.link(cam_obj)
        bpy.context.scene.camera = cam_obj

        # Empty como target de tracking
        target = bpy.data.objects.new("Cam_Target", None)
        target.location = target_location
        bpy.context.collection.objects.link(target)

        # Track To constraint
        constraint = cam_obj.constraints.new(type='TRACK_TO')
        constraint.target = target
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'

        # DOF focado no target
        cam.dof.focus_object = target

        return cam_obj, target

    @staticmethod
    def animate_orbit_zoom(cam_obj, target_obj, frames=120,
                           start_distance=5.0, end_distance=3.5,
                           orbit_degrees=60, elevation_start=30, elevation_end=20):
        """Órbita suave com zoom lento — o clássico shot cinematográfico."""
        scene = bpy.context.scene
        scene.frame_start = 1
        scene.frame_end = frames

        center = target_obj.location

        for frame in range(1, frames + 1):
            t = frame / frames

            # Easing suave (ease in-out)
            t_smooth = t * t * (3 - 2 * t)

            # Distância (zoom lento)
            dist = start_distance + (end_distance - start_distance) * t_smooth

            # Ângulo de órbita
            azimuth = math.radians(orbit_degrees * t_smooth)

            # Elevação (descendo sutilmente)
            elevation = math.radians(
                elevation_start + (elevation_end - elevation_start) * t_smooth
            )

            # Coordenadas esféricas → cartesianas
            x = center.x + dist * math.cos(elevation) * math.cos(azimuth)
            y = center.y + dist * math.cos(elevation) * math.sin(azimuth)
            z = center.z + dist * math.sin(elevation)

            cam_obj.location = (x, y, z)
            cam_obj.keyframe_insert(data_path="location", frame=frame)

        # Suavizar curvas
        CinematicCamera._smooth_fcurves(cam_obj)

        return cam_obj

    @staticmethod
    def animate_push_in(cam_obj, target_obj, frames=120,
                        start_distance=6.0, end_distance=2.0):
        """Push in dramático — câmera avança em linha reta."""
        scene = bpy.context.scene
        scene.frame_start = 1
        scene.frame_end = frames

        center = target_obj.location

        for frame in range(1, frames + 1):
            t = frame / frames
            t_smooth = t * t * (3 - 2 * t)

            dist = start_distance + (end_distance - start_distance) * t_smooth

            # Ângulo fixo (3/4 view)
            azimuth = math.radians(35)
            elevation = math.radians(25)

            x = center.x + dist * math.cos(elevation) * math.cos(azimuth)
            y = center.y + dist * math.cos(elevation) * math.sin(azimuth)
            z = center.z + dist * math.sin(elevation)

            cam_obj.location = (x, y, z)
            cam_obj.keyframe_insert(data_path="location", frame=frame)

        CinematicCamera._smooth_fcurves(cam_obj)
        return cam_obj

    @staticmethod
    def animate_reveal(cam_obj, target_obj, frames=120):
        """Reveal — começa de perto (blur), afasta revelando o objeto."""
        scene = bpy.context.scene
        scene.frame_start = 1
        scene.frame_end = frames

        center = target_obj.location

        for frame in range(1, frames + 1):
            t = frame / frames
            t_smooth = t * t * (3 - 2 * t)

            # Começa perto, afasta
            dist = 1.5 + 3.5 * t_smooth

            # Sobe levemente
            elevation = math.radians(10 + 25 * t_smooth)
            azimuth = math.radians(20 * t_smooth)

            x = center.x + dist * math.cos(elevation) * math.cos(azimuth)
            y = center.y + dist * math.cos(elevation) * math.sin(azimuth)
            z = center.z + dist * math.sin(elevation)

            cam_obj.location = (x, y, z)
            cam_obj.keyframe_insert(data_path="location", frame=frame)

        CinematicCamera._smooth_fcurves(cam_obj)
        return cam_obj

    @staticmethod
    def _smooth_fcurves(obj):
        """Suavizar todas as curvas de animação."""
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'BEZIER'
                    kp.easing = 'EASE_IN_OUT'


# =====================================================
# INTERNAL LAYERS — Camadas internas do objeto
# =====================================================

class InternalLayers:
    """Cria o efeito de camadas internas visíveis durante a desmontagem."""

    @staticmethod
    def create_layered_object(base_obj, num_layers=4, palette_name="tech_blue"):
        """Duplica o objeto em camadas menores com efeitos diferentes."""
        palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["tech_blue"])
        layers = [base_obj]

        for i in range(1, num_layers):
            # Duplicar
            bpy.ops.object.select_all(action='DESELECT')
            base_obj.select_set(True)
            bpy.context.view_layer.objects.active = base_obj
            bpy.ops.object.duplicate()
            layer = bpy.context.active_object
            layer.name = f"Internal_Layer_{i}"

            # Escalar progressivamente menor
            scale_factor = 1.0 - (i * 0.18)
            layer.scale = (scale_factor, scale_factor, scale_factor)

            # Material diferente por camada
            layer.data.materials.clear()

            if i == 1:
                # Wireframe tech
                mat = InternalLayers._wireframe_material(
                    f"Wire_{i}", palette["primary"]
                )
            elif i == 2:
                # Emissivo fraco
                mat = MaterialFactory.led_emissive(
                    f"Inner_Glow_{i}", palette["secondary"],
                    strength=3.0 + i * 2
                )
            else:
                # Metal interno
                mat = MaterialFactory.metal_brushed(
                    f"Inner_Metal_{i}",
                    (palette["primary"][0] * 0.5,
                     palette["primary"][1] * 0.5,
                     palette["primary"][2] * 0.5, 1.0)
                )

            layer.data.materials.append(mat)

            # Modifier de wireframe na camada 1
            if i == 1:
                wire_mod = layer.modifiers.new("Wireframe", type='WIREFRAME')
                wire_mod.thickness = 0.005
                wire_mod.use_replace = True

            # Modifier de bevel nas camadas do meio
            if i == 2:
                bevel_mod = layer.modifiers.new("Bevel", type='BEVEL')
                bevel_mod.width = 0.01
                bevel_mod.segments = 2

            layer.parent = base_obj
            layers.append(layer)

        return layers

    @staticmethod
    def _wireframe_material(name, color):
        """Material para efeito wireframe emissivo."""
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
        principled.inputs['Emission Strength'].default_value = 5.0
        principled.inputs['Alpha'].default_value = 0.8

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        return mat


# =====================================================
# PROCEDURAL DISASSEMBLY — Desmontagem avançada
# =====================================================

class ProceduralDisassembly:
    """Sistema de desmontagem procedural avançada."""

    @staticmethod
    def explode_with_layers(main_obj, layers, frames=120,
                            explosion_start=20, explosion_end=80,
                            max_distance=2.0):
        """Explosão sequencial — camada por camada, de fora para dentro."""
        scene = bpy.context.scene
        scene.frame_start = 1
        scene.frame_end = frames

        center = main_obj.location.copy()
        num_layers = len(layers)

        for i, layer in enumerate(layers):
            if layer == main_obj:
                # Objeto principal — último a se mover
                delay = explosion_start + int((explosion_end - explosion_start) * 0.8)
            else:
                # Camadas internas — explodem primeiro as externas
                layer_progress = (num_layers - 1 - i) / max(num_layers - 1, 1)
                delay = explosion_start + int(
                    (explosion_end - explosion_start) * 0.3 * layer_progress
                )

            # Direção de explosão
            direction = layer.location - center
            if direction.length < 0.01:
                angle = (i / max(num_layers, 1)) * math.pi * 2
                direction = Vector((
                    math.cos(angle),
                    math.sin(angle),
                    0.2 + random.uniform(-0.1, 0.3)
                ))
            direction.normalize()

            # Distância proporcional à camada
            distance = max_distance * (1.0 - i * 0.15)

            # Rotação durante explosão
            rot_axis = random.choice([0, 1, 2])
            rot_amount = math.radians(random.uniform(15, 45))

            # KEYFRAMES
            orig_loc = layer.location.copy()
            orig_rot = layer.rotation_euler.copy()

            # Frame 1: posição original
            layer.location = orig_loc
            layer.rotation_euler = orig_rot
            layer.keyframe_insert(data_path="location", frame=1)
            layer.keyframe_insert(data_path="rotation_euler", frame=1)

            # Frame delay: ainda parado
            layer.keyframe_insert(data_path="location", frame=delay)
            layer.keyframe_insert(data_path="rotation_euler", frame=delay)

            # Frame explosão: posição final
            final_loc = orig_loc + direction * distance
            final_rot = list(orig_rot)
            final_rot[rot_axis] += rot_amount

            layer.location = final_loc
            layer.rotation_euler = Euler(final_rot)
            layer.keyframe_insert(data_path="location", frame=delay + 30)
            layer.keyframe_insert(data_path="rotation_euler", frame=delay + 30)

            # Suavizar
            if layer.animation_data and layer.animation_data.action:
                for fc in layer.animation_data.action.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'BEZIER'
                        kp.easing = 'EASE_IN_OUT'

    @staticmethod
    def reassemble(main_obj, layers, frames=120,
                   reassemble_start=80, reassemble_end=110):
        """Inverso da explosão — peças voltam ao lugar."""
        # Já precisa ter keyframes de explosão
        for layer in layers:
            if not layer.animation_data:
                continue

            # Adicionar keyframes de retorno
            orig_loc = Vector((0, 0, 0))
            if layer.parent:
                orig_loc = layer.parent.location

            # Volta suave
            layer.location = orig_loc
            layer.rotation_euler = (0, 0, 0)
            layer.keyframe_insert(data_path="location", frame=reassemble_end)
            layer.keyframe_insert(data_path="rotation_euler", frame=reassemble_end)


# =====================================================
# CINEMATIC OBJECTS — Objetos base cinematográficos
# =====================================================

class CinematicObjects:
    """Objetos base para vídeos cinematográficos."""

    @staticmethod
    def tech_sphere(palette_name="tech_blue", size=0.8):
        """Esfera tech — metálica com detalhes."""
        palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["tech_blue"])

        bpy.ops.mesh.primitive_uv_sphere_add(radius=size, segments=64, ring_count=32)
        sphere = bpy.context.active_object
        sphere.name = "Tech_Sphere"

        # Shade smooth
        bpy.ops.object.shade_smooth()

        # Material metálico
        mat = MaterialFactory.metal_brushed(
            "Sphere_Metal",
            (palette["primary"][0] * 0.3 + 0.5,
             palette["primary"][1] * 0.3 + 0.5,
             palette["primary"][2] * 0.3 + 0.5, 1.0)
        )
        sphere.data.materials.append(mat)

        return sphere

    @staticmethod
    def minimal_cube(palette_name="tech_blue", size=0.7):
        """Cubo minimalista com bevel."""
        palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["tech_blue"])

        bpy.ops.mesh.primitive_cube_add(size=size)
        cube = bpy.context.active_object
        cube.name = "Minimal_Cube"

        bpy.ops.object.modifier_add(type='BEVEL')
        cube.modifiers["Bevel"].width = 0.03
        cube.modifiers["Bevel"].segments = 4
        bpy.ops.object.modifier_apply(modifier="Bevel")

        bpy.ops.object.shade_smooth()

        mat = MaterialFactory.plastic_glossy(
            "Cube_Glossy", palette["primary"]
        )
        cube.data.materials.append(mat)

        return cube

    @staticmethod
    def abstract_torus(palette_name="tech_blue"):
        """Torus abstrato — visual futurista."""
        palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["tech_blue"])

        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.6, minor_radius=0.15,
            major_segments=64, minor_segments=24
        )
        torus = bpy.context.active_object
        torus.name = "Abstract_Torus"

        bpy.ops.object.shade_smooth()

        mat = MaterialFactory.metal_brushed(
            "Torus_Metal", palette["primary"]
        )
        torus.data.materials.append(mat)

        return torus

    @staticmethod
    def get_object(object_type, palette_name="tech_blue"):
        """Factory — retorna objeto por tipo."""
        generators = {
            "sphere": CinematicObjects.tech_sphere,
            "cube": CinematicObjects.minimal_cube,
            "torus": CinematicObjects.abstract_torus,
        }
        gen = generators.get(object_type, CinematicObjects.tech_sphere)
        return gen(palette_name)


# =====================================================
# COMPOSITING — Post-processing cinematográfico
# =====================================================

class CinematicCompositing:
    """Compositor nodes para post-processing profissional."""

    @staticmethod
    def setup(palette_name="tech_blue", bloom_intensity=0.8, vignette=True,
              chromatic_aberration=True, color_grade=True):
        """Setup completo de compositing cinematográfico."""
        scene = bpy.context.scene
        scene.use_nodes = True
        tree = scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # Limpar nodes existentes
        nodes.clear()

        # === NODES BASE ===
        render_layers = nodes.new('CompositorNodeRLayers')
        render_layers.location = (-600, 300)

        composite = nodes.new('CompositorNodeComposite')
        composite.location = (800, 300)

        # Último output a conectar
        last_output = render_layers.outputs['Image']

        # === BLOOM / GLARE ===
        if bloom_intensity > 0:
            glare = nodes.new('CompositorNodeGlare')
            glare.glare_type = 'FOG_GLOW'
            glare.quality = 'HIGH'
            glare.mix = -0.7 + (bloom_intensity * 0.5)  # Subtil por defeito
            glare.threshold = 0.8
            glare.size = 7
            glare.location = (-200, 300)
            links.new(last_output, glare.inputs['Image'])
            last_output = glare.outputs['Image']

        # === COLOR GRADING ===
        if color_grade:
            palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["tech_blue"])

            # Color Balance (Lift/Gamma/Gain)
            color_bal = nodes.new('CompositorNodeColorBalance')
            color_bal.correction_method = 'LIFT_GAMMA_GAIN'
            color_bal.location = (0, 300)

            # Sombras: ligeiramente frias (azuladas)
            cold = palette.get("light_cold", (0.3, 0.5, 1.0))
            color_bal.lift = (1.0 - cold[0] * 0.03, 1.0 - cold[1] * 0.01, 1.0 + cold[2] * 0.03)

            # Midtones: neutros com leve tint
            color_bal.gamma = (1.0, 1.0, 1.02)

            # Highlights: ligeiramente quentes
            warm = palette.get("light_warm", (1.0, 0.6, 0.2))
            color_bal.gain = (1.0 + warm[0] * 0.02, 1.0 + warm[1] * 0.01, 1.0)

            links.new(last_output, color_bal.inputs['Image'])
            last_output = color_bal.outputs['Image']

            # Contrast boost subtil
            bright_contrast = nodes.new('CompositorNodeBrightContrast')
            bright_contrast.inputs['Bright'].default_value = 0.0
            bright_contrast.inputs['Contrast'].default_value = 8.0
            bright_contrast.location = (200, 300)
            links.new(last_output, bright_contrast.inputs['Image'])
            last_output = bright_contrast.outputs['Image']

        # === VINHETA ===
        if vignette:
            # Ellipse mask
            ellipse = nodes.new('CompositorNodeEllipseMask')
            ellipse.width = 0.85
            ellipse.height = 0.85
            ellipse.location = (200, 0)

            # Blur a mascara para transicao suave
            blur = nodes.new('CompositorNodeBlur')
            blur.size_x = 200
            blur.size_y = 200
            blur.use_relative = False
            blur.location = (400, 0)
            links.new(ellipse.outputs['Mask'], blur.inputs['Image'])

            # Multiplicar imagem pela mascara
            mix_vig = nodes.new('CompositorNodeMixRGB')
            mix_vig.blend_type = 'MULTIPLY'
            mix_vig.inputs['Fac'].default_value = 0.4  # Intensidade subtil
            mix_vig.location = (400, 300)
            links.new(last_output, mix_vig.inputs[1])
            links.new(blur.outputs['Image'], mix_vig.inputs[2])
            last_output = mix_vig.outputs['Image']

        # === ABERRACAO CROMATICA ===
        if chromatic_aberration:
            lens_dist = nodes.new('CompositorNodeLensdist')
            lens_dist.inputs['Distort'].default_value = 0.0
            lens_dist.inputs['Dispersion'].default_value = 0.008  # Muito subtil
            lens_dist.use_projector = False
            lens_dist.location = (600, 300)
            links.new(last_output, lens_dist.inputs['Image'])
            last_output = lens_dist.outputs['Image']

        # === OUTPUT FINAL ===
        links.new(last_output, composite.inputs['Image'])

        # Viewer para debug
        viewer = nodes.new('CompositorNodeViewer')
        viewer.location = (800, 0)
        links.new(last_output, viewer.inputs['Image'])

        print(f"[CINEMATIC] Compositing: bloom={bloom_intensity}, vignette={vignette}, "
              f"chromatic={chromatic_aberration}, color_grade={color_grade}")


# =====================================================
# CINEMATIC JOB EXECUTOR
# =====================================================

class CinematicJobExecutor:
    """Executa jobs cinematográficos completos."""

    def __init__(self, job_data):
        self.job = job_data
        self.config = job_data.get('config', {})
        self.cinematic = job_data.get('cinematic', {})
        self.output_dir = OUTPUT_DIR / job_data.get('outputFolder', 'cinematic')
        self.results = {'renders': [], 'animations': [], 'renderTimeMs': 0}

    def execute(self):
        """Pipeline cinematográfico completo."""
        start_time = time.time()

        try:
            # Configuração
            palette_name = self.cinematic.get('palette', 'tech_blue')
            object_type = self.cinematic.get('objectType', 'sphere')
            camera_style = self.cinematic.get('cameraStyle', 'orbit_zoom')
            effects = self.cinematic.get('effects', ['core', 'dust', 'sparks'])
            frames = self.cinematic.get('frames', 120)
            do_disassembly = self.cinematic.get('disassembly', True)
            num_layers = self.cinematic.get('layers', 4)

            # 1. Limpar cena
            SceneSetup.clear_scene()
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # 2. Render engine (EEVEE para preview, Cycles para final)
            scene = bpy.context.scene
            use_eevee = self.config.get('engine', 'CYCLES').upper() == 'EEVEE'

            if use_eevee:
                scene.render.engine = 'BLENDER_EEVEE'
                scene.eevee.taa_render_samples = self.config.get('samples', 32)
                scene.eevee.use_bloom = True
                scene.eevee.bloom_threshold = 0.8
                scene.eevee.bloom_intensity = 0.5
                print("[CINEMATIC] Engine: EEVEE (preview rapido)")
            else:
                scene.render.engine = 'CYCLES'
                scene.cycles.samples = self.config.get('samples', 200)
                scene.cycles.use_denoising = True
                # Tentar GPU
                prefs = bpy.context.preferences.addons.get('cycles')
                if prefs:
                    try:
                        prefs.preferences.compute_device_type = 'CUDA'
                        scene.cycles.device = 'GPU'
                        print("[CINEMATIC] Engine: Cycles GPU (CUDA)")
                    except:
                        scene.cycles.device = 'CPU'
                        print("[CINEMATIC] Engine: Cycles CPU")

            scene.render.resolution_x = self.config.get('resolution', {}).get('x', 1920)
            scene.render.resolution_y = self.config.get('resolution', {}).get('y', 1080)
            scene.view_settings.view_transform = 'Filmic'
            scene.view_settings.look = 'High Contrast'

            # Motion blur
            if self.cinematic.get('motionBlur', True):
                scene.render.use_motion_blur = True
                scene.render.motion_blur_shutter = 0.5

            # 3. Fundo escuro cinematográfico
            CinematicLighting.setup_world_dark_gradient(palette_name)

            # 4. Criar objeto principal
            if object_type == 'product':
                # Usar gerador de produtos do render_engine
                template = self.cinematic.get('productTemplate', 'generic_product')
                product_info = self.cinematic.get('productInfo', {})
                main_obj = ProductGenerator.generate(template, product_info)
            else:
                main_obj = CinematicObjects.get_object(object_type, palette_name)

            print(f"[CINEMATIC] Objeto criado: {main_obj.name}")

            # 5. Camadas internas
            layers = [main_obj]
            if num_layers > 1:
                layers = InternalLayers.create_layered_object(
                    main_obj, num_layers, palette_name
                )
                print(f"[CINEMATIC] {len(layers)} camadas criadas")

            # 6. Energy core
            if 'core' in effects:
                core = EnergyCore.create(
                    location=main_obj.location,
                    palette_name=palette_name,
                    size=0.12,
                    strength=25.0
                )
                print("[CINEMATIC] Energy core criado")

            # 7. Iluminação dual-tone
            CinematicLighting.dual_tone(palette_name, intensity=1.0)

            # 8. Câmera cinematográfica
            cam_obj, cam_target = CinematicCamera.create(
                target_location=main_obj.location
            )

            camera_animators = {
                'orbit_zoom': CinematicCamera.animate_orbit_zoom,
                'push_in': CinematicCamera.animate_push_in,
                'reveal': CinematicCamera.animate_reveal,
            }
            animator = camera_animators.get(camera_style, CinematicCamera.animate_orbit_zoom)
            animator(cam_obj, cam_target, frames)
            print(f"[CINEMATIC] Câmera: {camera_style}")

            # 9. Partículas
            if 'dust' in effects:
                ParticleEffects.dust(main_obj.location, palette_name, count=300)
            if 'sparks' in effects:
                ParticleEffects.sparks(main_obj, palette_name, count=150, lifetime=50)
            if 'fragments' in effects:
                ParticleEffects.fragments(main_obj, count=40)

            # 10. Desmontagem procedural
            if do_disassembly and len(layers) > 1:
                ProceduralDisassembly.explode_with_layers(
                    main_obj, layers, frames,
                    explosion_start=int(frames * 0.15),
                    explosion_end=int(frames * 0.65),
                    max_distance=2.0
                )
                print("[CINEMATIC] Desmontagem animada")

            # 11. Compositing (post-processing)
            CinematicCompositing.setup(
                palette_name=palette_name,
                bloom_intensity=self.cinematic.get('bloom', 0.8),
                vignette=self.cinematic.get('vignette', True),
                chromatic_aberration=self.cinematic.get('chromaticAberration', True),
                color_grade=self.cinematic.get('colorGrade', True)
            )

            # 12. Frame range
            scene.frame_start = 1
            scene.frame_end = frames

            # === RENDER ===

            # 12a. Render de vídeo
            scene.render.image_settings.file_format = 'FFMPEG'
            scene.render.ffmpeg.format = 'MPEG4'
            scene.render.ffmpeg.codec = 'H264'
            scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
            scene.render.fps = self.config.get('fps', 30)

            video_path = str(self.output_dir / "cinematic_video.mp4")
            scene.render.filepath = video_path
            bpy.ops.render.render(animation=True)

            self.results['animations'].append({
                'type': f'cinematic_{camera_style}',
                'url': video_path,
                'duration': frames / scene.render.fps,
                'fps': scene.render.fps,
                'palette': palette_name,
                'objectType': object_type,
                'fileSize': os.path.getsize(video_path) if os.path.exists(video_path) else 0
            })

            # 12b. Thumbnail estático (frame do meio)
            scene.render.image_settings.file_format = 'PNG'
            scene.render.image_settings.color_mode = 'RGBA'
            scene.frame_set(frames // 2)
            thumb_path = str(self.output_dir / "cinematic_thumbnail.png")
            scene.render.filepath = thumb_path
            bpy.ops.render.render(write_still=True)

            self.results['renders'].append({
                'type': 'cinematic_thumbnail',
                'url': thumb_path,
                'resolution': {
                    'x': scene.render.resolution_x,
                    'y': scene.render.resolution_y
                },
                'fileSize': os.path.getsize(thumb_path) if os.path.exists(thumb_path) else 0
            })

            # 12c. Key frames estáticos
            key_frames = [1, frames // 4, frames // 2, int(frames * 0.75)]
            for kf in key_frames:
                scene.frame_set(kf)
                kf_path = str(self.output_dir / f"keyframe_{kf:04d}.png")
                scene.render.filepath = kf_path
                bpy.ops.render.render(write_still=True)

                self.results['renders'].append({
                    'type': f'keyframe_{kf}',
                    'url': kf_path,
                    'resolution': {
                        'x': scene.render.resolution_x,
                        'y': scene.render.resolution_y
                    },
                    'fileSize': os.path.getsize(kf_path) if os.path.exists(kf_path) else 0
                })

            self.results['renderTimeMs'] = int((time.time() - start_time) * 1000)
            self.results['status'] = 'completed'

            print(f"[CINEMATIC] Completo: {len(self.results['renders'])} renders, "
                  f"{len(self.results['animations'])} vídeos em {self.results['renderTimeMs']}ms")

        except Exception as e:
            self.results['status'] = 'failed'
            self.results['error'] = str(e)
            print(f"[CINEMATIC] ERRO: {e}")
            import traceback
            traceback.print_exc()

        return self.results


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    args = parse_args()

    if not args:
        print("[CINEMATIC] Uso: blender --background --python cinematic_engine.py -- job.json")
        sys.exit(1)

    job_data = load_job(args[0])
    executor = CinematicJobExecutor(job_data)
    results = executor.execute()

    result_path = args[0].replace('.json', '_result.json')
    with open(result_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"[CINEMATIC] Resultados: {result_path}")
