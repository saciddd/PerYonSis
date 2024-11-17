from .menu import Menu

def menu_processor(request):
    menu = Menu(request.user) if request.user.is_authenticated else []
    return {'menu': menu}