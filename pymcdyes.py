import zipfile, sys, os.path, exceptions, time
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
        hc('#999999'): 'Light Gray Dye',
        hc('#4C4C4C'): 'Gray Dye',
        hc('#F2B2CC'): 'Pink Dye',
        hc('#7FCC19'): 'Lime Dye',
        hc('#E5E533'): 'Dandelion Yellow',
        hc('#99B2F2'): 'Light Blue Dye',
        hc('#E57FD8'): 'Magenta Dye',
        hc('#F2B233'): 'Orange Dye',
        hc('#FFFFFF'): 'Bone Meal'}

def init_bases(dye_dict):
    start = time.time()
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
    new_colors = tuple(sorted(new_colors.items(), key=lambda x: x[0]))
    print "... Done!"
    stop = time.time()
    # Offer to save time by caching
    print "NOTE: This process took %0.2f seconds to complete." % (stop - start)
    print "For the cost of ~95MB of storage, would you like to cache these results?"
    print "(Average speedup time for loading cached results: 5x times faster - or more!)"
    response = raw_input("[N/y]: ").strip().lower()
    if (response in ["yes", "y"]):
        print "Saving base_colors.cache ..."
        f = open('base_colors.cache','wb')
        for x_c, x_n in new_colors:
            f.write("%s\t%s\t%s\t%s\n" % (x_c.r, x_c.g, x_c.b,x_n))
        f.close()
        print "Saving base_mods.cache ..."
        f = open('base_mods.cache','wb')
        for i in range(8,0,-1):
            for x_c, x_n in new_mods[i]:
                f.write("%s\t%s\t%s\t%s\t%s\n" % (i,x_c.r, x_c.g, x_c.b,x_n))
        f.close()
        print "... Done!"
    else:
        print "Skipped caching."
    return [new_colors, new_mods]

def init_cached_bases():
    print "Reading cached map key (SPEEDY-ISH - takes a few seconds) ..."
    cached_base_colors = []
    f = open('base_colors.cache','r')
    for line in f.xreadlines():
        r,g,b,n = line.split('\t')
        cached_base_colors.append((col(int(r),int(g),int(b)), n[:-1]))
    f.close()
    cached_base_colors = tuple(cached_base_colors)
    cached_base_mods = [[] for x in range(9)]
    f = open('base_mods.cache','r')
    old_level = ""
    for line in f.xreadlines():
        i,r,g,b,n = line.split('\t')
        if old_level != i:
            print "... Level %s of 8 ..." % i
            old_level = i
        cached_base_mods[int(i)].append((col(int(r),int(g),int(b)), n[:-1]))
    f.close()
    for i in range(9):
        cached_base_mods[i] = tuple(cached_base_mods[i])
    print "... Validating ..."
    if (len(cached_base_colors) == 327842) and (len(cached_base_mods[8]) == 414081):
        print "... Done!"
        return [cached_base_colors, cached_base_mods]
    else:
        print "... ERROR in cache! ... rebuilding ..."
        raise exceptions.Exception('Cache Mismatch')


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

def color_exists(target_c):
    global color_map
    if (target_c.r < 25) or (target_c.g < 25) or (target_c.b < 25): return False
    i = ((target_c.r-25) + (target_c.g-25)*231 + (target_c.b-25)*231*231)*6
    return bool(color_map[i])

def vector_projection(target_c):
    scalar = sum(map(lambda x: x*0.57735, target_c))
    new_coord = min(int(0.57735*scalar+0.5), 255)
    if new_coord > 24:
        return col(new_coord,new_coord,new_coord)
    return None

def dist_3d(target_c, new_c):
    return int(sum(map(lambda x: (x[1] - x[0])**2,  zip(target_c, new_c)))**0.5 + 1)

def next_pixel_in_3d(source_c, dest_c):
    x1,y1,z1 = pixel = list(source_c)
    x2,y2,z2 = dest_c
    dx,dy,dz = x2-x1, y2-y1, z2-z1
    x_inc = ((dx < 0) and -1) or 1
    y_inc = ((dy < 0) and -1) or 1
    z_inc = ((dz < 0) and -1) or 1
    l,m,n = abs(dx), abs(dy), abs(dz)
    dx2,dy2,dz2 = l << 1, m << 1, n << 1
    if (l >= m) and (l >= n):
        err_1, err_2 = dy2-l, dz2-l
        for i in range(l):
            if (color_exists(col(*pixel))):
                return col(*pixel)
            if (err_1 > 0):
                pixel[1] += y_inc
                err_1 -= dx2
            if (err_2 > 0):
                pixel[2] += z_inc
                err_2 -= dx2
            err_1 += dy2
            err_2 += dz2
            pixel[0] += x_inc
    elif (m >= l) and (m >= n):
        err_1, err_2 = dx2-m, dz2-m
        for i in range(m):
            if (color_exists(col(*pixel))):
                return col(*pixel)
            if (err_1 > 0):
                pixel[0] += x_inc
                err_1 -= dy2
            if (err_2 > 0):
                pixel[2] += z_inc
                err_2 -= dy2
            err_1 += dx2
            err_2 += dz2
            pixel[1] += y_inc
    else:
        err_1, err_2 = dy2-n, dx2-n
        for i in range(n):
            if (color_exists(col(*pixel))):
                return col(*pixel)
            if (err_1 > 0):
                pixel[1] += y_inc
                err_1 -= dz2
            if (err_2 > 0):
                pixel[0] += x_inc
                err_2 -= dz2
            err_1 += dy2
            err_2 += dx2
            pixel[2] += z_inc
    if (color_exists(col(*pixel))):
        return col(*pixel)
    return None

def cube_search(target_c, max_dist=255):
    print "\nSearching for the closest colors in RGB color space ..."
    r, best_dist, best_cs = 1, 500, []
    # double max dist passed
    max_dist = 2*max_dist
    while (r <= max_dist):
        # search sides in y-axis:
        for dy in ([0] + [j for i in zip(range(1,r),range(-1,-r,-1)) for j in i]):
            # This generates a list like [0, 1, -1, 2, -2, ... r-1, -r+1]
            y_g = target_c.g + dy
            if 24 < y_g < 256:
                # side 1 & 2
                for x_r in [target_c.r + r, target_c.r - r]:
                    if 24 < x_r < 256:
                        for z_b in range(target_c.b - r, target_c.b + r + 1):
                            if 24 < z_b < 256:
                                t_c = col(x_r, y_g, z_b)
                                if color_exists(t_c):
                                    # Found a color, update the max distance range
                                    t_dist = dist_3d(target_c, t_c)
                                    if t_dist < best_dist:
                                        max_dist = min(max_dist, 2*t_dist)
                                        best_dist = t_dist
                                        best_cs = [t_c]
                                    elif t_dist == best_dist:
                                        best_cs.append(t_c)
                # side 3 & 4
                for z_b in [target_c.b + r, target_c.b - r]:
                    if 24 < z_b < 256:
                        for x_r in range(target_c.r - r + 1, target_c.r + r):
                            if 24 < x_r < 256:
                                t_c = col(x_r, y_g, z_b)
                                if color_exists(t_c):
                                    # Found a color, update the max distance range
                                    t_dist = dist_3d(target_c, t_c)
                                    if t_dist < best_dist:
                                        max_dist = min(max_dist, 2*t_dist)
                                        best_dist = t_dist
                                        best_cs = [t_c]
                                    elif t_dist == best_dist:
                                        best_cs.append(t_c)
        # search top & bottom in y-axis
        for y_g in [target_c.g + r, target_c.g - r]:
            if 24 < y_g < 256:
                for x_r in range(target_c.r - r, target_c.r + r + 1):
                    if 24 < x_r < 256:
                        for z_b in range(target_c.b - r, target_c.b + r + 1):
                            if 24 < z_b < 256:
                                t_c = col(x_r, y_g, z_b)
                                if color_exists(t_c):
                                    # Found a color, update the max distance range
                                    t_dist = dist_3d(target_c, t_c)
                                    if t_dist < best_dist:
                                        max_dist = min(max_dist, 2*t_dist)
                                        best_dist = t_dist
                                        best_cs = [t_c]
                                    elif t_dist == best_dist:
                                        best_cs.append(t_c)
        r += 1
    if best_cs:
        return (best_dist, best_cs)
    return None

def try_offer_alternative(target_c):
    instr = raw_input("Look for a closest match? [Y/n]: ").strip().lower()
    if instr not in ['n', 'no', 'quit', 'q']:
        print "Suggested closest colors:\n-------------------------"
        max_dist = 256
        t_c = next_pixel_in_3d(target_c, col(127,127,127))
        if t_c:
            print "Towards gray: %s - %s" % (ch(t_c), t_c)
            max_dist = min(dist_3d(t_c, target_c), max_dist)
        t_c = next_pixel_in_3d(target_c, col(255,255,255))
        if t_c:
            print "Towards white: %s - %s" % (ch(t_c), t_c)
            max_dist = min(dist_3d(t_c, target_c), max_dist)
        v_c = vector_projection(target_c)
        if v_c:
            t_c = next_pixel_in_3d(target_c, v_c)
            if t_c:
                print "Projection mapped to black->white: %s - %s" % (ch(t_c), t_c)
                max_dist = min(dist_3d(t_c, target_c), max_dist)
        t_c = next_pixel_in_3d(target_c, col(25,25,25))
        if t_c:
            print "Towards black: %s - %s" % (ch(t_c), t_c)
            max_dist = min(dist_3d(t_c, target_c), max_dist)
        closest_c = cube_search(target_c, max_dist)
        if closest_c:
            c_dist, t_cs = closest_c
            print "The following", len(t_cs), "closest colors were found at a distance of:", c_dist
            print ",\n".join([("  " + ", ".join(map(lambda x: "%s - %s" % (ch(x), x), t_cs[i:i+2]))) for i in range(0, len(t_cs), 2)])
    print ""


def pprint_ancestry(target_c, DEBUG=False):
    print "Goal color: %s - %s" % (ch(target_c), target_c)
    print "Checking ..."
    ancestry = get_color_ancestry(target_c)
    if not ancestry:
        print "... Sorry, but this color is not reachable with this map!\n"
        try_offer_alternative(target_c)
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

def init_main():
    global color_map, base_colors, base_mods
    color_map = init_color_map()
    if (os.path.exists('base_colors.cache') and os.path.exists('base_mods.cache')):
        try:
            # Attempt loading cache
            base_colors, base_mods = init_cached_bases()
        except:
            # Cache mismatch, redo
            base_colors, base_mods = init_bases(dyes)
    else:
        base_colors, base_mods = init_bases(dyes)        
    print "[4,001,584 color recipes loaded]\n"

def main():
    init_main()
    while True:
        instr = raw_input("[Enter RRGGBB hex color to find or Q to quit]: ").strip().lower()
        if instr in ['q','quit','exit']:
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
