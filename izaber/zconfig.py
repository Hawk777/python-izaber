# ==================================================
# some nice things about this class
# ==================================================
import appdirs
import os
import yaml
import re

class DictObj(object):
    def __init__(self,config,data):
        self._config = config
        self._data = data

    def dict(self):
        return self._data

    def __getattr__(self,k):
        v = self._data[k]
        if isinstance(v,dict):
            return DictObj(self._config,v)
        return v

    def __getitem__(self,k):
        return self.__getattr__(k)

    def __str__(self):
        return str(self._data)

    def __call__(self):
        return self._data

class YAMLConfig(object):
    _app_name = 'ZaberConfig'
    _app_author = 'Zaber'
    _config_filename = 'zaber.yaml'
    _config_dirs = [
                    appdirs.user_data_dir(_app_name, _app_author),
                    os.path.expanduser('~'),
                    '.',
                  ]

    def config_find(self,config_dirs=None,config_filename=None):
        """ Attempt to use the config dir/config_filenames to
            locate the configuration file requested. Some folks
            would prefer to keep their config in ~ where it's in 
            plain sight rather than the buried application
            specific location
        """
        if config_dirs is None:
            config_dirs = self._config_dirs
        else:
            if isinstance(config_dirs,basestring):
                config_dirs = [config_dirs]

        if config_filename is None:
            config_filename = self._config_filename
        for test_dir in config_dirs:
            test_fpath = os.path.join(test_dir,config_filename)
            if os.path.isfile(test_fpath):
                return test_fpath

        # No matches found
        return

    # ================================================
    # constructor
    # ================================================
    def __init__( self, 
                  config_buffer=None, 
                  config_dirs=None,
                  config_filename=None, 
                  environment=None
                ): 

        # Setup defaults
        if config_filename:
            self._config_filename = config_filename
        if config_dirs:
            if isinstance(config_dirs,basestring):
                self._config_dirs = [config_dirs]
            else:
                self._config_dirs = config_dirs

        import pdb; pdb.set_trace()
        if config_buffer:
            self._config_full_filname = None
            self._cfg = yaml.load(config_buffer)
        else:
            self._config_full_filename = self.config_find() \
                                          or os.path.join(self._config_dirs[0], \
                                                          self._config_filename)

            # check if config directory exists, and create if necessary
            self._config_dir = os.path.dirname(self._config_full_filename)
            if not os.path.exists(self._config_dir):
                os.makedirs(self._config_dir)
                    
            try:
                with open(self._config_full_filename,'r') as file_obj:
                    self._cfg = yaml.load(file_obj)
            except IOError:
                self._cfg = {}

        # initialize environment
        if environment == None:
            environment = 'default'
        self._env = environment

    # ================================================
    # dealing with dynamic attributes
    # ================================================
    def __getattr__(self, name):
        if name in self._cfg[self._env]:
            v = self._cfg[self._env][name] 
            if isinstance(v,dict):
                return DictObj(self,v)
            return v
        raise AttributeError("{} is not an attribute".format(name))

    def __getitem__(self,name):
        return self.__getattr__(name)

    def addon_config(self,name):
        if name in self._cfg[self._env]:
            v = self._cfg[self._env][name]
        elif name in self._cfg['default']:
            v = self._cfg['default'][name]
        else:
            v = {}
            self._cfg[self._env][name] = v
        return DictObj(self,v)


    # ================================================
    # choose the environment
    # ================================================
    def environment(self, env=None):
        if env != None:
            self._env = env 
            if self._env not in self._cfg:
                self._cfg[self._env] = {}
        return self._env


    # ================================================
    # run a basic wizard interface
    # ================================================
    def wizard(self, wizard_options): 
        for attribute in wizard_options:
            # if needed, this would be a good place to check for existence of
            # 'key' and 'prompt' and either 'default' or 'validate'
            # in attribute
            # for now we'll assume the wizard's not buggy
            default = ''

            # figure out the default value
            # if it has already been set in the config, use that
            # otherwise, use what's given in the wizard
            if attribute['key'] in self._cfg[self._env]:
                default = self._cfg[self._env][attribute['key']] 
            elif 'default' in attribute:
                try:
                    default = attribute['default']()
                except TypeError:
                    default = attribute['default']

            if not default:
                prompt = "{prompt}: ".format(**attribute)
            else:
                prompt = "{prompt} [{defaultval}]: ".format( \
                        defaultval=default, \
                        **attribute)

            # time to actually ask the user for input; use validation if given
            if attribute.has_key('validate'):
                while True:
                    try:
                        new_value = raw_input(prompt) or default
                        if attribute['validate'](self, new_value):
                            break
                    except Exception as e:
                        print(e)
            else:
                new_value = raw_input(prompt) or default

            # save value to dictionary
            self._cfg[self._env][attribute['key']] = new_value


    # ================================================
    # write config to yaml file
    # ================================================
    def save(self): 
        if self._config_full_filename == None:
            raise Exception("Cannot save config when ")
        file_obj = open(self._config_full_filename, 'w')
        yaml.dump(self._cfg, file_obj, default_flow_style=False)
        file_obj.close()
        print("Yay!  Configuration saved to {}".format(self._config_full_filename))


