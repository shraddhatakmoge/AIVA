
def get_active_app():
    try:
        win = gw.getActiveWindow()
        if win:
            title = win.title.lower()
            if "whatsapp" in title:
                return "whatsapp"
            elif "notepad" in title:
                return "notepad"
    except:
        pass
    return None


# ==============================