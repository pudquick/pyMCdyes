import zipfile, sys
from collections import namedtuple
from itertools import imap
col = namedtuple('col', 'r g b')
color_map, base_colors, base_mods = None, None, None

try:
    from itertools import combinations_with_replacement
except:
    # Replacement recipe for python 2.6
    def combinations_with_replacement(iterable, r):
        pool = tuple(iterable)
        n = len(pool)
        if not n and r:
            return
        indices = [0] * r
        yield tuple(pool[i] for i in indices)
        while True:
            for i in reversed(range(r)):
                if indices[i] != n - 1:
                    break
            else:
                return
            indices[i:] = [indices[i] + 1] * (r - i)
            yield tuple(pool[i] for i in indices)

def hc(s):
    return col(*map(lambda x: int(x,16), map(''.join, zip(*[iter(s.strip().lstrip('#'))]*2))))

def ch(c):
    return ('#' + hex(c.r)[2:].rjust(2,'0') + hex(c.g)[2:].rjust(2,'0') + hex(c.b)[2:].rjust(2,'0')).upper()

def avg_color(colors, l=None):
    if not l:
        l = len(colors)
    return col(sum([c.r for c in colors])//l,sum([c.g for c in colors])//l,sum([c.b for c in colors])//l)

dyes = {hc('#191919'): 'Ink Sac',
        hc('#CC4C4C'): 'Rose Red',
        hc('#667F33'): 'Cactus Green',
        hc('#7F664C'): 'Cocoa Beans',
        hc('#3366CC'): 'Lapis Lazuli',
        hc('#B266E5'): 'Purple Dye',
        hc('#4C99B2'): 'Cyan Dye',
        hc('#999999'): 'Light Gray',
        hc('#4C4C4C'): 'Gray Dye',
        hc('#F2B2CC'): 'Pink Dye',
        hc('#7FCC19'): 'Lime Dye',
        hc('#E5E533'): 'Dandelion Yellow',
        hc('#99B2F2'): 'Light Blue Dye',
        hc('#E57FD8'): 'Magenta Dye',
        hc('#F2B233'): 'Orange Dye',
        hc('#FFFFFF'): 'Bone Meal'}

def init_bases(dye_dict):
    new_colors, new_mods = dict(), [dict() for x in range(9)]
    print "Generating map key (SLOW - takes a minute) ..."
    for count in range(8,0,-1):
        print "... Level %s of 8 ..." % count
        for dye_set in combinations_with_replacement(dye_dict.items(), count):
            new_color_name = '[' + '+'.join(imap(lambda x: x[1], dye_set)) + ']'
            new_color_avg  = avg_color(list(imap(lambda x: x[0], dye_set)))
            new_color_sum  = avg_color(list(imap(lambda x: x[0], dye_set)), 1)
            new_colors[new_color_avg] = new_color_name
            new_mods[count][new_color_sum] = new_color_name
    print "... Sorting ..."
    for count in range(9):
        new_mods[count] = tuple(sorted(new_mods[count].items(), key=lambda x: x[0]))
    print "... Done!"
    return [tuple(sorted(new_colors.items(), key=lambda x: x[0])), new_mods]

def init_color_map():
    print "Loading color map (FAST) ..."
    archive = zipfile.ZipFile('color_map.zip', 'r')
    f_map  = archive.open('color_map.bytearray')
    new_map = bytearray(f_map.read())
    f_map.close()
    archive.close()
    print "... Done!"
    return new_map

def get_color_data(target_c):
    global color_map
    if (target_c.r < 25) or (target_c.g < 25) or (target_c.b < 25):
        return (col(0,0,0),0,1)
    i = ((target_c.r-25) + (target_c.g-25)*231 + (target_c.b-25)*231*231)*6
    source_c = col(*color_map[i:i+3])
    mod_level = ((color_map[i+3] & 0xe0) >> 5) + 1
    mod_0a = color_map[i+3] & 0x1f
    mod_i = (mod_0a << 16) | (color_map[i+4] << 8) | (color_map[i+5])
    return (source_c, mod_i, mod_level)

def get_color_ancestry(target_c):
    global color_map, base_colors, base_mods
    INVALID_COLOR = col(0,0,0)
    BASE_COLOR = col(1,1,1)
    parent_c, mod_i, mod_level = get_color_data(target_c)
    if (parent_c == INVALID_COLOR):
        return []
    elif (parent_c == BASE_COLOR):
        return [(base_colors[mod_i][0], base_colors[mod_i][1])]
    else:
        ancestry = get_color_ancestry(parent_c)
	if ancestry:
            return ancestry + [(base_mods[mod_level][mod_i][0], base_mods[mod_level][mod_i][1])]
        return ancestry

def verify_ancestry(target_c):
    a_chain = get_color_ancestry(target_c)
    new_c = a_chain[0][0]
    for dye_set, dye_name in a_chain[1:]:
        new_c = avg_color([new_c, dye_set], dye_name.count('+') + 2)
    return (new_c, target_c)

def pprint_ancestry(target_c, DEBUG=False):
    print "Goal color: %s - %s" % (ch(target_c), target_c)
    print "Checking ..."
    ancestry = get_color_ancestry(target_c)
    if not ancestry:
        print "... Sorry, but this color is not reachable with this map!\n"
    else:
        print "... FOUND!\n"
        print "(Apply these dye sets, in order, starting with a new leather item!)"
        print "\nRecipe for color:\n-----------------"
        for rgb, dyes in ancestry:
            if DEBUG:
                print "- %s \\\\ %s - %s" % (dyes, ch(rgb), rgb)
            else:
                print "- %s" % dyes
        result,target = verify_ancestry(target_c)
        if (target == result):
            print "\nRecipe Verified: GOOD\n"
        else:
            print "\nRecipe Verified: ERROR!! (please let pudquick@github-or-r/minecraft know!)"
            print "Problem color in question:", target_c
            sys.exit(1)

def main():
    global color_map, base_colors, base_mods
    color_map = init_color_map()
    base_colors, base_mods = init_bases(dyes)
    print "[4,001,584 color recipes loaded]\n"
    while True:
        instr = raw_input("[Enter RRGGBB hex color to find or Q to quit]: ").strip().lower()
        if instr == 'q':
            break
        else:
            print
            try:
                target_c = hc(instr)
                pprint_ancestry(target_c)
            except:
                print "... Whoops! Something went wrong there, let's try again ..."

if __name__ == "__main__":
    main()
