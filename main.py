
import traceback
from tkinter_module import *

if __name__ == '__main__':
    
    try:
        root = Interface()
        root.mainloop()
    except Exception as e:
        with open('log.txt', 'w') as f:
            f.write(str(e))
            f.write(traceback.format_exc())

    sys.exit(0)
