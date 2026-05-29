from typing import NamedTuple


class Specialty(NamedTuple):
    slug: str
    label: str
    keywords: list[str]


SPECIALTIES: list[Specialty] = [
    Specialty("2d_artist", "2D Artist", [
        "2d artist", "2d designer", "illustrator", "graphic designer",
        "2d generalist", "motion graphics artist", "vector artist",
        "2d asset", "2d designer", "2d illustrator",
    ]),
    Specialty("2d_animator", "2D Animator", [
        "2d animator", "traditional animator", "frame by frame",
        "flash animator", "toon boom", "2d animation", "cel animation",
        "2d character animator", "moho", "tvpaint",
    ]),
    Specialty("3d_modeler", "3D Modeler", [
        "3d modeler", "3d modeling", "modeler", "modeling",
        "poly modeling", "zbrush", "sculpting", "sculpt artist",
        "organic modeler", "hard surface modeler",
        "maya modeler", "blender modeler", "3ds max",
        "lead modeler", "senior modeler", "character modeler",
        "environment modeler", "prop modeler", "retopology",
        "3d asset", "digital sculptor", "fusion 360", "solidworks",
        "digital modeler",
    ]),
    Specialty("3d_animator", "3D Animator", [
        "3d animator", "character animator", "keyframe",
        "motion capture", "mocap", "character animation",
        "3d animation", "maya animator", "blender animator",
        "animation td", "lead animator", "senior animator",
        "game animator", "vfx animator", "animation",
        "animator",
    ]),
    Specialty("technical_artist", "Technical Artist", [
        "technical artist", "tech artist", "tech art",
        "tools developer", "tools programmer", "cg tools",
        "python developer", "pipeline engineer",
        "technical director", "fx td", "lighting td",
    ]),
    Specialty("rigger", "Rigger", [
        "rigger", "rigging", "character setup", "skinning",
        "rigging artist", "rigging td", "character rigger",
        "creature rigger", "facial rigger",
    ]),
    Specialty("texture_surfacing", "Texture / Surfacing", [
        "texture", "texturing", "surfacing", "surface artist",
        "shader", "lookdev", "look development",
        "substance painter", "substance designer",
        "texture artist", "texturing artist",
        "mari", "shading", "material artist",
    ]),
    Specialty("lighting", "Lighting", [
        "lighting", "lighting artist", "lighting td",
        "look development", "look dev", "light artist",
        "lighting supervisor",
    ]),
    Specialty("compositor", "Compositor", [
        "compositing", "compositor", "nuke", "fusion",
        "after effects", "compositing artist",
        "vfx compositor", "digital compositor", "flame artist",
    ]),
    Specialty("vfx_fx", "VFX / FX", [
        "vfx", "visual effects", "fx artist", "fx td",
        "effects artist", "particle", "simulation",
        "houdini", "pyro", "fluid sim", "cloth sim",
        "destruction", "crowd artist",
    ]),
    Specialty("concept_artist", "Concept Artist", [
        "concept artist", "concept design", "concept art",
        "visual development", "visdev", "concept designer",
        "concept illustrator", "character design",
        "environment concept", "key art", "illustration",
    ]),
    Specialty("layout_previs", "Layout / Previs", [
        "layout artist", "layout", "previs", "previz",
        "previsualization", "camera layout",
        "matchmove", "match move", "tracking",
    ]),
    Specialty("render", "Render", [
        "render", "rendering", "renderman", "arnold",
        "render wrangler", "render farm", "render td",
        "render supervisor", "vray", "cycles",
        "redshift", "octane",
    ]),
    Specialty("editor", "Editor / Post", [
        "video editor", "video editing", "editor",
        "post production", "post-production", "color grading",
        "colorist", "online editor",
        "premiere", "final cut", "da vinci", "motion graphics",
    ]),
    Specialty("pipeline_td", "Pipeline TD", [
        "pipeline td", "pipeline developer", "cg supervisor",
        "pipeline engineer", "pipeline supervisor", "cg pipeline",
    ]),
    Specialty("generalist", "Generalist", [
        "generalist", "generalista", "3d generalist",
        "cg generalist", "art generalist", "3d artist",
        "blender generalist",
    ]),
    Specialty("production", "Production", [
        "producer", "production manager", "production coordinator",
        "line producer", "project manager", "production assistant",
        "post production supervisor", "production supervisor",
    ]),
    Specialty("game_dev", "Game Developer", [
        "game developer", "game designer", "unity developer",
        "unreal developer", "game programmer", "game dev",
        "gameplay programmer", "engine programmer",
        "level designer", "game engineer",
        "vr", "ar developer",
    ]),
    Specialty("art_director", "Art Director", [
        "art director", "creative director", "art direction",
        "art supervisor", "director of art",
    ]),
]


def classify_job(title: str, description: str) -> list[str]:
    content = (title + " " + description).lower()
    matched: list[str] = []

    for spec in SPECIALTIES:
        for keyword in spec.keywords:
            if keyword in content:
                matched.append(spec.slug)
                break

    return matched
