import re
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
        "design grafico", "designer grafico", "diseno grafico",
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
    Specialty("developer", "Developer / Programmer", [
        "software developer", "software engineer", "programmer",
        "full stack", "frontend", "backend", "web developer",
        "react", "angular", "vue", "node", "python", "java",
        "javascript", "typescript", "golang", "c++",
        "devops", "cloud engineer", "data engineer",
        "mobile developer", "ios", "android", "flutter",
        "react native", "api developer", "software architect",
        "desarrollador", "programador", "ingeniero de software",
        "desenvolvedor",
        "dotnet", ".net", "php", "ruby", "sql", "docker",
        "kubernetes", "aws", "azure", "backend developer",
        "frontend developer", "fullstack",
    ]),
    Specialty("cad_designer", "CAD / Industrial Design", [
        "solidworks", "fusion 360", "autocad",
        "cad software", "cad designer", "cad technician",
        "cad operator", "cad engineer", "cad design",
        "industrial designer", "industrial design",
        "mechanical designer", "mechanical engineer",
        "industrial product designer", "product design engineer", "autodesk inventor", "catia",
        "rhino", "draftsman", "dibujante",
        "diseno industrial", "ingeniero mecanico",
        "impresion 3d", "3d printing", "3d print",
        "additive manufacturing", "manufactura aditiva",
        "prototipado", "prototyping", "rapid prototyping",
        "creality", "prusa", "slicer", "cura slicer",
        "technical designer", "technical drafter",
        "diseñador industrial", "diseñador mecanico",
        "ingenieria inversa", "reverse engineering",
        "modelado 3d industrial", "industrial 3d",
        "projetista", "projetista mecanico", "projetista 3d",
    ]),
    Specialty("audio_composer", "Music / Audio", [
        "composer", "music producer",
        "sound designer", "audio engineer", "music",
        "soundtrack", "scoring", "audio post",
        "foley", "sound editor", "mixing",
        "mastering", "audio post-production",
        "banda sonora", "musicalizacion",
        "musico", "musician", "audio producer",
        "game audio", "audio programmer",
        "sound design", "sound effects",
        "compositor musical", "music composer",
    ]),
    Specialty("writer", "Writing / Content", [
        "writer", "copywriter", "content writer",
        "script writer", "screenwriter", "guionista",
        "editorial", "periodista", "journalist",
        "technical writer", "redactor", "content creator",
        "ghostwriter", "blog writer", "seo writer",
        "ux writer", "content strategist",
        "redaccion", "redactor creativo",
    ]),
    Specialty("video_production", "Video Production", [
        "video producer", "videographer",
        "film director", "production assistant", "camera",
        "director de cine", "filmacion", "camarografo",
        "drone", "fotografia", "photography",
        "film producer", "tv producer", "camera operator",
        "director de fotografia", "director of photography",
        "animador 2d", "motion graphics",
        "video production", "film production",
    ]),
]


def classify_job(title: str, description: str) -> list[str]:
    content = (title + " " + description).lower()
    matched: list[str] = []

    for spec in SPECIALTIES:
        for keyword in spec.keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', content):
                matched.append(spec.slug)
                break

    return matched
