app_config = {}
dependancies = {}
initialization_rack = {}

def initializer(key,before=[]):
    def rack(key,f):
        initialization_rack[key] = f
        if before:
            for b in before:
                dependancies.setdefault(b,[])
                dependancies[b].append(key)
        return f

    return lambda f: rack(key,f)

def initialize(name,**kwargs):
    kwargs['name'] = name
    app_config.update(kwargs)
    for key, func in dict(initialization_rack).items():
        if not initialization_rack[key]:
            continue
        if key in dependancies:
            for b in dependancies.get(key,[]):
                kwargs = request_initialize(b,**kwargs)

        kwargs = request_initialize(key,**kwargs)
        initialization_rack[key] = None

def request_initialize(key,**kwargs):
    if not initialization_rack[key]:
        return
    result = initialization_rack[key](**kwargs)
    initialization_rack[key] = None
    if result: return result
    return kwargs
