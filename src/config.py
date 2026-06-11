LIMIT_DAYS = 30
MAX_JOBS_PER_SPECIALTY = 100

DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
DEFAULT_TIMEOUT = 10

FEEDS = [
    ("Entertainment Careers", "https://www.entertainmentcareers.net/ecnjcat173"),
    ("WorkWithIndies", "https://www.workwithindies.com/careers/rss.xml"),
    ("Remote OK Dev", "https://remoteok.com/remote-dev-jobs.rss"),
    ("GameDev.net Jobs", "https://gamedev.net/jobs/rss"),
    ("Remote Game Jobs", "https://remotegamejobs.com/feed.rss"),
    ("Polycount Freelance", "https://polycount.com/categories/freelance-job-postings/feed.rss"),
    ("BlenderArtists Paid Jobs", "https://blenderartists.org/c/jobs/paid-work/53.rss"),
    ("We Work Remotely Programming", "https://weworkremotely.com/categories/remote-programming-jobs.rss"),
    ("We Work Remotely Design", "https://weworkremotely.com/categories/remote-design-jobs.rss"),
    ("Career Nest Jobs", "https://careernest.cloud/api/feed.xml"),
    ("Behance Jobs", "https://www.behance.net/feeds/jobs"),
    ("Dribbble Jobs", "https://dribbble.com/jobs.rss"),
]

ARC_DEV_URL = "https://arc.dev/en-ar/remote-jobs"

BYPASS_SOURCES = {"Entertainment Careers", "Catho", "Elempleo", "InGameJob"}

IMAGE_CAMPUS_SEARCH_TERMS = [
    "3d", "vfx", "blender", "maya", "houdini",
    "animacion", "modelado", "rigging", "ilustracion",
    "diseno grafico", "video", "produccion", "game",
    "unity", "unreal", "generalista",
    "programador", "desarrollador", "software", "developer",
    "solidworks", "fusion", "cad", "impresion 3d",
    "compositor", "musica", "musicalizacion", "audio",
    "doblaje", "locucion", "locutor",
    "diseno industrial", "ingeniero",
    "audiovisual", "fotografia",
]
