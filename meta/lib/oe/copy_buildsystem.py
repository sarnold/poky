# This class should provide easy access to the different aspects of the
# buildsystem such as layers, bitbake location, etc.
import stat
import shutil

def _smart_copy(src, dest):
    # smart_copy will choose the correct function depending on whether the
    # source is a file or a directory.
    mode = os.stat(src).st_mode
    if stat.S_ISDIR(mode):
        shutil.copytree(src, dest, symlinks=True)
    else:
        shutil.copyfile(src, dest)
        shutil.copymode(src, dest)

class BuildSystem(object):
    def __init__(self, d):
        self.d = d
        self.layerdirs = d.getVar('BBLAYERS', True).split()

    def copy_bitbake_and_layers(self, destdir):
        # Copy in all metadata layers + bitbake (as repositories)
        layers_copied = []
        bb.utils.mkdirhier(destdir)
        layers = list(self.layerdirs)

        corebase = self.d.getVar('COREBASE', True)
        layers.append(corebase)

        corebase_files = self.d.getVar('COREBASE_FILES', True).split()
        corebase_files = [corebase + '/' +x for x in corebase_files]
        # Make sure bitbake goes in
        bitbake_dir = bb.__file__.rsplit('/', 3)[0]
        corebase_files.append(bitbake_dir)

        for layer in layers:
            layerconf = os.path.join(layer, 'conf', 'layer.conf')
            if os.path.exists(layerconf):
                with open(layerconf, 'r') as f:
                    if f.readline().startswith("# ### workspace layer auto-generated by devtool ###"):
                        bb.warn("Skipping local workspace layer %s" % layer)
                        continue

            # If the layer was already under corebase, leave it there
            # since layers such as meta have issues when moved.
            layerdestpath = destdir
            if corebase == os.path.dirname(layer):
                layerdestpath += '/' + os.path.basename(corebase)
            layerdestpath += '/' + os.path.basename(layer)

            layer_relative = os.path.relpath(layerdestpath,
                                             destdir)
            layers_copied.append(layer_relative)

            # Treat corebase as special since it typically will contain
            # build directories or other custom items.
            if corebase == layer:
                bb.utils.mkdirhier(layerdestpath)
                for f in corebase_files:
                    f_basename = os.path.basename(f)
                    destname = os.path.join(layerdestpath, f_basename)
                    _smart_copy(f, destname)
            else:
                if os.path.exists(layerdestpath):
                    bb.note("Skipping layer %s, already handled" % layer)
                else:
                    _smart_copy(layer, layerdestpath)

        return layers_copied

def generate_locked_sigs(sigfile, d):
    bb.utils.mkdirhier(os.path.dirname(sigfile))
    depd = d.getVar('BB_TASKDEPDATA', False)
    tasks = ['%s.%s' % (v[2], v[1]) for v in depd.itervalues()]
    bb.parse.siggen.dump_lockedsigs(sigfile, tasks)

def prune_lockedsigs(allowed_tasks, excluded_targets, lockedsigs, pruned_output):
    with open(lockedsigs, 'r') as infile:
        bb.utils.mkdirhier(os.path.dirname(pruned_output))
        with open(pruned_output, 'w') as f:
            invalue = False
            for line in infile:
                if invalue:
                    if line.endswith('\\\n'):
                        splitval = line.strip().split(':')
                        if splitval[1] in allowed_tasks and not splitval[0] in excluded_targets:
                            f.write(line)
                    else:
                        f.write(line)
                        invalue = False
                elif line.startswith('SIGGEN_LOCKEDSIGS'):
                    invalue = True
                    f.write(line)

def create_locked_sstate_cache(lockedsigs, input_sstate_cache, output_sstate_cache, d, fixedlsbstring=""):
    bb.note('Generating sstate-cache...')

    bb.process.run("gen-lockedsig-cache %s %s %s" % (lockedsigs, input_sstate_cache, output_sstate_cache))
    if fixedlsbstring:
        os.rename(output_sstate_cache + '/' + d.getVar('NATIVELSBSTRING', True),
        output_sstate_cache + '/' + fixedlsbstring)
