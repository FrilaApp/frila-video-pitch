"""O MP4 de bloco precisa sair em limited-range e BT.709 completo."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RAIZ = Path(__file__).parents[2]
sys.path.insert(0, str(RAIZ / 'motor'))
from render import trabalho, preparar_bloco
from fotos import servidor
from motor.tests.test_bloco_a import regua_teste


class EncodeBloco(unittest.TestCase):
    def test_subquadros_jpeg_geram_yuv420p_tv_bt709(self):
        s = servidor()
        try:
            with tempfile.TemporaryDirectory() as pasta:
                video = Path(pasta) / 'bloco.mp4'
                _, erros = trabalho(('pt', s.server_port, 0, 12, video,
                                      preparar_bloco(regua_teste())))
                self.assertEqual(erros, [])
                m = json.loads(subprocess.check_output([
                    'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(video)
                ]))['streams'][0]
                self.assertEqual(m['pix_fmt'], 'yuv420p')
                self.assertEqual(m.get('color_range'), 'tv')
                for campo in ('color_space', 'color_transfer', 'color_primaries'):
                    self.assertEqual(m.get(campo), 'bt709', campo)
                self.assertEqual(m['nb_frames'], '3')
                self.assertEqual(m['r_frame_rate'], '60/1')
                self.assertEqual((m['width'], m['height']), (1920, 1080))
        finally:
            s.shutdown()
            s.server_close()
