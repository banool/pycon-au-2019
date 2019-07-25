sys.modules = []

def import(module):
    for m in module.imports:
        if m in sys.modules:
            continue
        import(m)
        sys.modules.append(m)

    
