class Shipment:
    def __init__(self, shipment_id, tracking_number):
        self.ShipNumber = shipment_id
        self.TrackingNumber = tracking_number

    def display_info(self):
        return (
            f"Shipment ID: {self.ShipNumber}\n"
            f"Tracking Number: {self.TrackingNumber}\n"
        )
