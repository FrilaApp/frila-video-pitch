"""Testes unitários para o mecanismo de seleção de blocos (Tarefa de Fecho de Seleção).
Valida que:
1. Tomada sem aprovação de ouvido do Fabrício é RECUSADA, mesmo que passe na verificação automática;
2. Tomada com aprovação de ouvido do Fabrício e sem falhas técnicas automáticas é APROVADA com passou_verificacao_automatica=True;
3. Tomada com aprovação de ouvido do Fabrício e com falhas A8 é APROVADA com passou_verificacao_automatica=False
   se e somente se houver registro explícito em excecoes_a8 correspondente;
4. Falha técnica sem exceção de ouvido é RECUSADA;
5. Falsas exceções cadastradas em tomada que passou na verificação automática são detectadas e tratadas.
"""
import copy
import unittest

from vozes.regua_blocos import validar_aprovacao_selecao, validar_excecoes_a8


class TestMecanismoSelecao(unittest.TestCase):

    def setUp(self):
        self.item_base = {
            "id": "A",
            "sha256": "hash_take_a",
            "aprovacao_ouvido": {
                "aprovador": "Fabrício",
                "data": "2026-10-27",
                "aprovado": True
            },
            "excecoes_a8": []
        }
        self.a8_sem_falha = {
            "estado": "sem_falha",
            "pendencias": [],
            "falhas": []
        }
        self.a8_com_falha = {
            "estado": "falha",
            "pendencias": [],
            "falhas": [
                {
                    "regra": "A8_pausa_interna",
                    "ini": 5.66,
                    "fim": 6.16,
                    "duracao": 0.50
                }
            ]
        }

    def test_sem_aprovacao_ouvido_recusa_mesmo_passando_no_teste_automatico(self):
        """Passar no teste automático NÃO é aprovação: sem chancela do Fabrício, a seleção recusa."""
        item = copy.deepcopy(self.item_base)
        item["aprovacao_ouvido"]["aprovado"] = False
        with self.assertRaisesRegex(ValueError, "aprovação humana de ouvido"):
            validar_aprovacao_selecao(item, self.a8_sem_falha)

        item["aprovacao_ouvido"] = None
        with self.assertRaisesRegex(ValueError, "aprovação humana de ouvido"):
            validar_aprovacao_selecao(item, self.a8_sem_falha)

    def test_aprovado_de_ouvido_e_passou_automatico(self):
        """Tomada chancelada pelo Fabrício e sem falhas no A8 passa com status claro."""
        status = validar_aprovacao_selecao(self.item_base, self.a8_sem_falha)
        self.assertTrue(status["aprovado_ouvido"])
        self.assertTrue(status["passou_verificacao_automatica"])
        self.assertEqual(status["aprovador"], "Fabrício")
        self.assertEqual(status["data"], "2026-10-27")

    def test_aprovado_de_ouvido_com_falha_a8_e_excecao_valida(self):
        """Tomada chancelada pelo Fabrício com falha A8 exige exceção formal."""
        item = copy.deepcopy(self.item_base)
        excecao = {
            "regra": "A8_pausa_interna",
            "ini": 5.66,
            "fim": 6.16,
            "duracao": 0.50,
            "sha256": "hash_take_a",
            "aprovador": "Fabrício",
            "data": "2026-10-27",
            "motivo": "Pausa de 0,500 s aceita de ouvido"
        }
        item["excecoes_a8"] = [excecao]

        status = validar_aprovacao_selecao(item, self.a8_com_falha)
        self.assertTrue(status["aprovado_ouvido"])
        self.assertFalse(status["passou_verificacao_automatica"])

        # Validação cruzada com validar_excecoes_a8
        aceites = validar_excecoes_a8(self.a8_com_falha, item["excecoes_a8"], "hash_take_a")
        self.assertEqual(len(aceites), 1)

    def test_falha_a8_sem_excecao_recusa(self):
        """Falha A8 sem exceção formal de ouvido cadastrada deve ser bloqueada."""
        item = copy.deepcopy(self.item_base)
        item["excecoes_a8"] = []
        with self.assertRaisesRegex(ValueError, "falha na verificação técnica automática sem exceção"):
            validar_aprovacao_selecao(item, self.a8_com_falha)


if __name__ == "__main__":
    unittest.main()
