class ScaleThreshold:
    def __init__(self, domain, target_range):
        self.domain = domain
        self.target_range = target_range

    def interpolate(self, value):
        target_ind = 0
        for ind, domain_value in enumerate(self.domain):
            if domain_value > value:
                break
            target_ind = ind + 1
        return self.target_range[target_ind]
