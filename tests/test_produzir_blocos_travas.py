"""Testes unitários de travas e segurança do script de produção dos blocos (PR #27).
Garante:
1. Dry-run por padrão: não acessa rede nem lê chave de API e sai com código 0;
2. --executar sem --teto-caracteres é recusado;
3. Termos com status 'candidata' bloqueiam a execução com código 2;
4. Termos 'aprovada' aplicam a forma fonética na fala enviada;
5. roteiro.json e as legendas permanecem 100% inalterados.
"""
import copy
import json
import pathlib
import sys
import unittest
from unittest.mock import patch, MagicMock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import vozes.produzir_blocos_tarefa6 as prod
from vozes.pronuncia import carregar_pronuncia

ROTEIRO_PATH = ROOT / "roteiro.json"


class TestProduzirBlocosTravas(unittest.TestCase):

    def setUp(self):
        self.roteiro_original = json.loads(ROTEIRO_PATH.read_text(encoding="utf-8"))

    def test_dry_run_padrao_nao_chama_rede_nem_le_chave(self):
        """Dry-run por padrão lista o planejamento, não acessa rede/chave e sai com 0."""
        # Se chamar() ou chave() forem invocados em dry-run, o teste falha
        with patch("vozes.produzir_blocos_tarefa6.chamar", side_effect=AssertionError("Rede chamada em dry-run!")), \
             patch("vozes.produzir_blocos_tarefa6.chave", side_effect=AssertionError("Chave lida em dry-run!")):
            
            codigo = prod.main([])
            self.assertEqual(codigo, 0)

    def test_executar_sem_teto_recusa(self):
        """Passar --executar sem informar --teto-caracteres deve recusar a execução."""
        with self.assertRaises(SystemExit) as ctx:
            prod.main(["--executar"])
        self.assertNotEqual(ctx.exception.code, 0)

    def test_executar_com_teto_insuficiente_recusa(self):
        """Passar --executar com teto inferior aos caracteres previstos deve recusar."""
        with self.assertRaises(SystemExit) as ctx:
            prod.main(["--executar", "--teto-caracteres", "100"])
        self.assertNotEqual(ctx.exception.code, 0)

    def test_termo_candidata_bloqueia_com_codigo_2(self):
        """Se houver termos com status 'candidata' na fala dos blocos, aborta com código 2."""
        dicionario_com_candidata = {
            "Frila": {
                "termo": "Frila",
                "forma": "Fríla",
                "voz": "gabriel",
                "status": "candidata",
                "nota": "teste pendente"
            }
        }
        with patch("vozes.produzir_blocos_tarefa6.carregar_pronuncia", return_value=dicionario_com_candidata), \
             patch("vozes.produzir_blocos_tarefa6.chamar", side_effect=AssertionError("Rede não pode ser chamada!")):
            with self.assertRaises(SystemExit) as ctx:
                prod.main(["--blocos", "B", "--executar", "--teto-caracteres", "5000"])
            self.assertEqual(ctx.exception.code, 2)

    def test_termo_aprovado_aplica_forma_fonetica_sem_mudar_roteiro(self):
        """Quando aprovadas, as formas fonéticas entram na fala enviada, e roteiro/legendas não mudam."""
        dicionario_aprovado = {
            "Frila": {
                "forma": "Fríla",
                "voz": "ambas",
                "status": "aprovada",
                "nota": "aprovada teste"
            },
            "check-in": {
                "forma": "tchéquin",
                "voz": "ambas",
                "status": "aprovada",
                "nota": "aprovada teste"
            }
        }
        
        blocos_planejados, pendencias = prod.planejar_blocos(
            roteiro=self.roteiro_original,
            pronuncia_dict=dicionario_aprovado
        )
        
        # Como todos os termos de risco configurados estão aprovados, não há pendências
        self.assertEqual(len(pendencias), 0)
        
        # O Bloco B deve conter a forma fonética aprovada "Fríla" e "tchéquin"
        bloco_b = blocos_planejados["B"]
        self.assertIn("Fríla", bloco_b["texto_envio"])
        self.assertIn("tchéquin", bloco_b["texto_envio"])
        
        # O roteiro oficial e as legendas de tela NUNCA são alterados
        roteiro_atual = json.loads(ROTEIRO_PATH.read_text(encoding="utf-8"))
        self.assertEqual(roteiro_atual, self.roteiro_original)
        for c in roteiro_atual["cenas"]:
            self.assertNotIn("tchéquin", c["pt"]["legenda"])
            self.assertNotIn("Fríla", c["pt"]["legenda"])

    def test_filtro_blocos_todos_aprovados(self):
        """Todos os blocos (A, B, C, D) estão com status aprovado de acordo com as decisões do Fabrício."""
        dicionario_atual = carregar_pronuncia()
        
        # Testando A, C, D: 0 pendências
        blocos_acd, pendencias_acd = prod.planejar_blocos(
            self.roteiro_original,
            pronuncia_dict=dicionario_atual,
            blocos_filtro=["A", "C", "D"]
        )
        self.assertEqual(len(pendencias_acd), 0)
        self.assertEqual(set(blocos_acd.keys()), {"A", "C", "D"})
        # Fríla aplicada nos blocos D e A onde cabível
        self.assertIn("Fríla", blocos_acd["D"]["texto_envio"])
        self.assertIn("Méta", blocos_acd["C"]["texto_envio"])
        self.assertIn("déis", blocos_acd["C"]["texto_envio"])
        self.assertIn("Federau", blocos_acd["C"]["texto_envio"])

        # Testando Bloco B (Gabriel): 0 pendências e texto idêntico ao original (formas originais aprovadas)
        blocos_b, pendencias_b = prod.planejar_blocos(
            self.roteiro_original,
            pronuncia_dict=dicionario_atual,
            blocos_filtro=["B"]
        )
        self.assertEqual(len(pendencias_b), 0)
        self.assertEqual(blocos_b["B"]["texto_envio"], blocos_b["B"]["fala_oficial"])
        self.assertIn("Frila", blocos_b["B"]["texto_envio"])
        self.assertIn("check-in", blocos_b["B"]["texto_envio"])
        self.assertIn("histórico", blocos_b["B"]["texto_envio"])


if __name__ == "__main__":
    unittest.main()
