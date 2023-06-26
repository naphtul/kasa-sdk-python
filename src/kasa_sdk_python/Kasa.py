import asyncio
import logging

from kasa import Discover, SmartStrip

logging.basicConfig(level=logging.INFO)


class Kasa:
    def __init__(self):
        self.devices = {}
        self.context = asyncio.Runner()

    def discover(self) -> dict:
        return self.context.run(self._discover())

    async def _discover(self) -> dict:
        devices = await Discover.discover()
        self.devices.clear()
        for ip, device in devices.items():
            if 'children' in device.sys_info:
                for child in device.sys_info['children']:
                    self.devices[child['alias']] = dict(ip=ip, state=bool(child['state']), type=device.device_type.name,
                                                        device=device)
            else:
                self.devices[device.alias] = dict(ip=ip, state=device.is_on, type=device.device_type.name,
                                                  device=device)
        return {k: dict(state=v['state'], type=v['type']) for k, v in self.devices.items()}

    def turn_on(self, device_name: str) -> None:
        return self.context.run(self._turn_on(device_name))

    async def _turn_on(self, device_name: str) -> None:
        if not self.devices:
            await self._discover()
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
        return self.context.run(self._turn_off(device_name))

    async def _turn_off(self, device_name: str) -> None:
        if not self.devices:
            await self._discover()
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
        return self.context.run(self._toggle(device_name))

    async def _toggle(self, device_name: str) -> None:
        if not self.devices:
            await self._discover()
        current_state = self.devices.get(device_name)['state']
        if current_state:
            await self._turn_off(device_name)
        else:
            await self._turn_on(device_name)
        self.devices.get(device_name)['state'] = not self.devices.get(device_name)['state']
        logging.info(f"{device_name} is now {'On' if self.devices.get(device_name)['state'] else 'Off'}")


if __name__ == '__main__':
    kasa = Kasa()
    device_list = kasa.discover()
    kasa.toggle('Office')
    kasa.toggle('Top floor SE corner lamp')
