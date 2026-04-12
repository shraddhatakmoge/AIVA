import os
import time
import pyautogui
import pygetwindow as gw
import win32com.client
from common import close_app


# -------- FOCUS POWERPOINT --------
# -------- FOCUS POWERPOINT --------
def focus_pp():
    # Look for PowerPoint windows
    windows = gw.getWindowsWithTitle("PowerPoint")
    
    for win in windows:
        # 🔥 THE FIX: Ignore off-screen ghost windows and 0x0 processes
        if win.width > 10 and win.left > -10000: 
            try:
                if win.isMinimized:
                    win.restore()
                
                # 🛡️ THE BYPASS: Press Alt to trick Windows security
                pyautogui.press('alt')
                time.sleep(0.1)
                
                win.activate()
                # ⌨️ THE ESCAPE: Drops any menu highlights caused by the Alt key
                pyautogui.press('esc')
                time.sleep(0.2)
                return win
            except Exception as e:
                print(f"⚠️ JARVIS: Could not focus PowerPoint: {e}")
                continue

    # If no physical window is found, launch it
    print("🚀 JARVIS: PowerPoint not found in foreground. Launching...")
    os.system("start powerpnt")
    time.sleep(2)
    return None

# -------- OPEN --------
def open_powerpoint():
    """
    Universal Launch: Uses the official executable name 'powerpnt'.
    """
    print("🚀 JARVIS: Opening Microsoft PowerPoint...")
    try:
        # 'powerpnt' is the universal command for all versions of PP
        os.startfile("powerpnt") 
        
        # 🔥 THE FIX: Wait for the Template Gallery to load
        time.sleep(6) 
        
        # Press Enter to select 'Blank Presentation'
        pyautogui.press('enter')
        print("✅ PowerPoint is ready.")
    except Exception as e:
        print(f"❌ Error opening PowerPoint: {e}")

def add_slide():
    """
    Universal Add Slide: Uses Ctrl+M shortcut.
    """
    if focus_pp():
        # Give a small pause to ensure focus is stable
        time.sleep(0.5)
        # Ctrl + M is the global shortcut for a new slide
        pyautogui.hotkey('ctrl', 'm')
        print("✅ JARVIS: New slide added.")
    else:
        print("❌ PowerPoint not found. Opening it now...")
        open_powerpoint()


# -------- SET TITLE --------
def set_slide_title(text):
    focus_pp()
    try:
        # Connect to the active PowerPoint window
        pp_app = win32com.client.GetActiveObject("PowerPoint.Application")
        # Get the slide currently on your screen
        slide = pp_app.ActiveWindow.View.Slide
        
        # 1. Try to find the built-in Title placeholder
        try:
            slide.Shapes.Title.TextFrame.TextRange.Text = text
            print(f"✅ JARVIS: Title set to '{text}'")
        except:
            # 2. Fallback: Search all shapes for a text box
            for shape in slide.Shapes:
                if shape.HasTextFrame:
                    shape.TextFrame.TextRange.Text = text
                    print(f"✅ JARVIS: Text set in available box: '{text}'")
                    return
    except Exception as e:
        print(f"❌ PowerPoint Error: {e}")
        

# -------- SET CONTENT --------
def set_slide_content(text):
    try:
        pp_app = win32com.client.GetActiveObject("PowerPoint.Application")
        slide = pp_app.ActiveWindow.View.Slide
        
        found_box = False
        for shape in slide.Shapes:
            # Look for Body/Content placeholders
            if shape.HasTextFrame and (shape.Type == 2 or "Content" in shape.Name):
                shape.TextFrame.TextRange.Text = text
                found_box = True
                print(f"✅ JARVIS: Content set!")
                break
        
        # 🔥 IF NO BOX FOUND: Create a new text box automatically!
        if not found_box:
            print("⚠️ No box found. Creating a new one for you...")
            # Left=100, Top=150, Width=500, Height=300
            new_box = slide.Shapes.AddTextbox(Orientation=1, Left=100, Top=150, Width=500, Height=300)
            new_box.TextFrame.TextRange.Text = text
            print("✅ JARVIS: Created a new box and added the content.")
            
    except Exception as e:
        print(f"❌ PowerPoint Content Error: {e}")
        
# -------- SET SUBTITLE -------------
def set_slide_subtitle(text):
    """Scans shapes but specifically targets 'Subtitle' while ignoring 'Title'."""
    focus_pp()
    try:
        pp_app = win32com.client.GetActiveObject("PowerPoint.Application")
        slide = pp_app.ActiveWindow.View.Slide
        
        found_subtitle = False
        print(f"🔍 JARVIS: Scanning {slide.Shapes.Count} shapes for Subtitle...")

        for shape in slide.Shapes:
            shape_name = shape.Name.lower()
            
            # 🎯 THE FIX: Only skip if it's the MAIN Title. 
            # If the name has 'subtitle' in it, we WANT to use it!
            if "subtitle" in shape_name:
                shape.TextFrame.TextRange.Text = text
                found_subtitle = True
               
                break
                
            if "title" in shape_name:
                
                continue
            
            # Fallback for the second box if it doesn't have a standard name
            if shape.HasTextFrame and not found_subtitle:
                shape.TextFrame.TextRange.Text = text
                found_subtitle = True
             
                break
        
        if not found_subtitle:
            print("⚠️ JARVIS: I checked every box, but couldn't find a valid subtitle placeholder.")
                
    except Exception as e:
        print(f"❌ PowerPoint Subtitle Error: {e}")

# --------- DELETE SLIDE -------------        
def delete_slide(slide_no=None):
    """Deletes either a specific slide number or the current active slide."""
    focus_pp()
    try:
        pp_app = win32com.client.GetActiveObject("PowerPoint.Application")
        presentation = pp_app.ActivePresentation
        
        if slide_no:
            # Delete by specific number (1-based index)
            presentation.Slides(int(slide_no)).Delete()
            print(f"✅ JARVIS: Deleted slide number {slide_no}")
        else:
            # Delete the one currently on screen
            current_index = pp_app.ActiveWindow.View.Slide.SlideIndex
            presentation.Slides(current_index).Delete()
            print(f"✅ JARVIS: Deleted current slide ({current_index})")
            
    except Exception as e:
        print(f"❌ PowerPoint Delete Error: {e}")
        
        
# -------- NAVIGATOR SLIDESHOW -------------
def navigate_slide(target):
    """Handles jumping to next, previous, or specific slide numbers."""
    focus_pp()
    try:
        pp_app = win32com.client.GetActiveObject("PowerPoint.Application")
        
        # 1. Detect View: Are we in a Slideshow or the Editor?
        if pp_app.SlideShowWindows.Count > 0:
            view = pp_app.SlideShowWindow(1).View
        else:
            view = pp_app.ActiveWindow.View
            
        presentation = pp_app.ActivePresentation
        current_index = view.Slide.SlideIndex

        # 2. Execute Navigation
        if target == "next":
            if current_index < presentation.Slides.Count:
                view.GotoSlide(current_index + 1)
                print(f"✅ JARVIS: Moved to slide {current_index + 1}")
        elif target == "previous":
            if current_index > 1:
                view.GotoSlide(current_index - 1)
                print(f"✅ JARVIS: Moved to slide {current_index - 1}")
        else:
            # Handle numbers like "slide 3"
            slide_no = int(target)
            view.GotoSlide(slide_no)
            print(f"✅ JARVIS: Jumped to slide {slide_no}")
            
    except Exception as e:
        print(f"❌ PowerPoint Navigation Error: {e}")

# ------- SLIDESHOW --------------
def start_slideshow():
    """Starts the full-screen presentation by pressing F5."""
    if focus_pp():
        
        pyautogui.press('f5')
    else:
        print("❌ JARVIS: PowerPoint is not open to start a show.")

def stop_slideshow():
    """Exits the slideshow mode by pressing Escape."""
    if focus_pp():
        print("🛑 JARVIS: Stopping Slideshow...")
        pyautogui.press('esc')
    else:
        print("❌ JARVIS: PowerPoint not found.")

# Note: Your existing navigate_slide already handles 'next' and 'previous' 
# by checking if a SlideshowWindow exists!
       
# --------- APPLY THEME ------------ 
def apply_presentation_theme(theme_name):
    focus_pp()
    try:
        pp_app = win32com.client.GetActiveObject("PowerPoint.Application")
        presentation = pp_app.ActivePresentation
        
        # 🟢 STEP 1: Try the direct name (Works for some Office 365 versions)
        try:
            presentation.ApplyTemplate(theme_name)
            print(f"🎨 JARVIS: Applied theme '{theme_name}' directly.")
            return
        except:
            pass

        # 🟢 STEP 2: Try common Windows Theme Paths (The "Brute Force" search)
        user_profile = os.environ['USERPROFILE']
        possible_paths = [
            f"C:\\Program Files\\Microsoft Office\\root\\Document Themes 16\\{theme_name}.thmx",
            f"C:\\Program Files (x86)\\Microsoft Office\\root\\Document Themes 16\\{theme_name}.thmx",
            f"{user_profile}\\AppData\\Roaming\\Microsoft\\Templates\\Document Themes\\{theme_name}.thmx"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                presentation.ApplyTemplate(path)
                print(f"🎨 JARVIS: Theme applied from {path}")
                return

        print(f"❌ JARVIS: Could not find theme '{theme_name}' on your disk.")
            
    except Exception as e:
        print(f"❌ PowerPoint Theme Error: {e}")
        
# -------- CLOSE --------
def close_powerpoint():
    print("❌ Closing PowerPoint...")
    close_app("POWERPNT")