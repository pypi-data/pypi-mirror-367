class SKU:
    def __init__(self, sku_id, weight_kg, volume_m3):
        self.id, self.weight, self.volume = sku_id, float(weight_kg), float(volume_m3)