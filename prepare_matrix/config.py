import json

class Config:
    def __init__(self):
        config_file = './config.json'
        local_config_file = './local.config.json'

        self.config = json.loads(open(config_file).read())
        self.config.update(json.loads(open(local_config_file).read()))

    def __call__(self, param):
        return self.config[param]

get_config_param = Config()
