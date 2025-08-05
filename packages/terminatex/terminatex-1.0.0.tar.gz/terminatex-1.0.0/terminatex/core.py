# terminatex/core.py

import sys
import tempfile
import os
import matplotlib.pyplot as plt

# --- Using the correct imports you provided ---
try:
    from term_image.image import from_file
    from term_image.exceptions import TermImageError
except ImportError:
    print("Error: The 'term-image' library is not installed. Please run 'pip install term-image' and try again.", file=sys.stderr)
    sys.exit(1)


def display(latex_string: str, color: str = 'white'):
    """
    Renders and displays a LaTeX expression in the terminal using term-image.
    """
    image_path = None
    try:
        # 1. Render the LaTeX to a temporary image file
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f"${latex_string}$", size=80, ha='center', va='center', color=color)
        ax.axis('off')
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            fig.savefig(tmp.name, format='png', dpi=300, bbox_inches='tight', pad_inches=0.2, transparent=True)
            plt.close(fig)
            image_path = tmp.name

        # 2. Create a term-image object from the file path
        image = from_file(image_path)
        
        # 3. Draw the image to the console
        image.draw()

    except TermImageError as e:
        print(f"Error: term-image failed to render. Your terminal may not be supported. Error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error: An unexpected error occurred. Error: {e}", file=sys.stderr)
    finally:
        # 4. Ensure the temporary file is always deleted
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

