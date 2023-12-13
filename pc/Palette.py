'''
palette.py   Roland Kwee   26 june 2023
'''

class Palette:
    'palette with set of colors for each histogram bin'

    types = ['white', 'black', 'red']
    type  = 'white'
    size = 10 #nr of palette colors

    def greyscale(self, i):
        'return greyscale value nr i (zero-based) from total nr of n values; i=0 is black'
        return int(255 * i / (self.size -1))
        
    def greyscale_inverse(self, i):
        'same as greyscale() but i=0 is white'
        return self.greyscale(self.size - i - 1)

    def red_to_blue(self, i):
        r = self.greyscale(i)
        g = 0
        b = 255 - r
        hexcolor = f'#{r:>02x}{g:>02x}{b:>02x}'
        return hexcolor

    def greyscale_rgb(self, i):
        v = 0
        if self.type == 'white':
            v = self.greyscale(i)
            hh = f'{v:>02x}' # e.g. 07, a7, ae
            hexcolor = f'#{hh}{hh}{hh}'
        elif self.type == 'black':
            v = self.greyscale_inverse(i)
            hh = f'{v:>02x}' # e.g. 07, a7, ae
            hexcolor = f'#{hh}{hh}{hh}'
        elif self.type == 'red':
            hexcolor = self.red_to_blue(i)
        else:
            # this error should be avoided by checking value of type when it changes, i.e. in a new method
            raise ValueError(f'Palette: unsupported type: {self.type}')
        #endif
        return hexcolor
    
