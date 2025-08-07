from IPython.core.magic import (Magics, line_magic, cell_magic, magics_class)
from IPython.display import display, HTML
import pandas as pd
from io import StringIO

@magics_class
class csv_magic(Magics):
    

    def __init__(self, shell):
        super(csv_magic, self).__init__(shell)

    @cell_magic("csv")
    def dmtCell(self, line, cell):
        df = pd.read_csv(StringIO(cell))
        display(HTML(df.to_html(index=False)))


    @line_magic("csv")
    def dmtLine(self, line):
        print("%%csv is a cell magic (use %%csv instead of %csv)") 



def load_ipython_extension(ipython):
    ipython.register_magics(csv_magic)
