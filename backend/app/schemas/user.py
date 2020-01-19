from validx import Dict, Str

user_schema = Dict(
    {
        "name": Str(),
        "email": Str(pattern=r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"),
        "password": Str(minlen=5),
    },
    optional=["name"],
)
