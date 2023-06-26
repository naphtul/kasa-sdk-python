import asyncio
import logging

from kasa import Discover, SmartStrip

logging.basicConfig(level=logging.INFO)


class Kasa:
    def __init__(self):
        self.devices = {}
        self.event_loop = asyncio.get_event_loop()

    def discover_devices(self) -> dict:
        devices = asyncio.run(Discover.discover())
        self.devices.clear()
        for ip, device in devices.items():
            if 'children' in device.sys_info:
                for child in device.sys_info['children']:
                    self.devices[child['alias']] = dict(ip=ip, state=bool(child['state']), type=device.device_type.name, device=device)
            else:
                self.devices[device.alias] = dict(ip=ip, state=device.is_on, type=device.device_type.name, device=device)
        return self.devices

    def turn_on(self, device_name: str) -> None:
        asyncio.run(self._turn_on(device_name))

    async def _turn_on(self, device_name: str) -> None:
        device = self.devices.get(device_name)
        if device['type'] == 'Strip':
            strip = SmartStrip(device['ip'])
            await strip.update()
            for child in strip.children:
                if child.alias == device_name:
                    await child.turn_on()
                    break
        else:
            await self.devices.get(device_name)['device'].turn_on()

    def turn_off(self, device_name: str) -> None:
        asyncio.run(self._turn_off(device_name))

    async def _turn_off(self, device_name: str) -> None:
        device = self.devices.get(device_name)
        if device['type'] == 'Strip':
            strip = SmartStrip(device['ip'])
            await strip.update()
            for child in strip.children:
                if child.alias == device_name:
                    await child.turn_off()
                    break
        else:
            await self.devices.get(device_name)['device'].turn_off()

    def toggle(self, device_name: str) -> None:
        current_state = self.devices.get(device_name)['state']
        if current_state:
            self.turn_off(device_name)
        else:
            self.turn_on(device_name)
        self.devices.get(device_name)['state'] = not self.devices.get(device_name)['state']
        logging.info(f"{device_name} is now {'On' if self.devices.get(device_name)['state'] else 'Off'}")


if __name__ == '__main__':
    kasa = Kasa()
    device_list = kasa.discover_devices()
    kasa.toggle('Office')
    kasa.toggle('Top floor SE corner lamp')
