from validx import Dict, Str

upload_schema = Dict(
    {
        'email': Str(pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'),
        'time': Str(pattern=r'[0-9]+::[0-9]+::')
    }
)