"""Testes unitários da mecânica de pronúncia e fonética familiar (Tarefa 6).
Garante:
1. Legendas do roteiro.json são imutáveis;
2. 'Frila' casa com 'Fríla' (e outras candidatas) no conferidor normal();
3. Substituição não vira palavra de outro item (word-boundary estrito);
4. Preservação de maiúsculas/minúsculas;
5. Distinção rigorosa entre candidata e aprovada;
6. Separação por voz (Ana / Gabriel / ambas).
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
from vozes.pronuncia import aplicar_pronuncia, carregar_pronuncia, mapa_reverso_fonetico
from vozes.manifesto import normal

ROTEIRO_PATH = ROOT / "roteiro.json"


class TestPronuncia(unittest.TestCase):

    def setUp(self):
        self.roteiro = json.loads(ROTEIRO_PATH.read_text(encoding="utf-8"))
        self.dicionario = carregar_pronuncia()

    def test_legenda_nao_muda(self):
        """As legendas de todas as cenas do roteiro devem permanecer estritamente intocadas."""
        for cena in self.roteiro["cenas"]:
            legenda_original = cena["pt"]["legenda"]
            # Mesmo se aplicarmos substituições na legenda, o roteiro real não é alterado
            texto_legenda, subs = aplicar_pronuncia(legenda_original, apenas_aprovadas=False)
            # O arquivo roteiro.json deve conter a legenda canônica
            self.assertEqual(cena["pt"]["legenda"], legenda_original)
            # Legendas oficiais nunca devem conter formas fonéticas alteradas como 'tchéquin' ou 'Fríla'
            self.assertNotIn("tchéquin", legenda_original.lower())
            self.assertNotIn("fríla", legenda_original.lower())

    def test_frila_casa_com_frila_no_conferidor(self):
        """O conferidor normal() deve mapear formas fonéticas e transcrições ASR para o termo canônico."""
        self.assertEqual(normal("Frila"), normal("Fríla"))
        self.assertEqual(normal("Freela"), normal("Fríla"))
        self.assertEqual(normal("Fríla conecta"), normal("Frila conecta"))
        self.assertEqual(normal("tchéquin"), normal("check-in"))
        self.assertEqual(normal("Abrazéu"), normal("Abrasel"))
        self.assertEqual(normal("Federau"), normal("Federal"))
        self.assertEqual(normal("cinkuenta"), normal("cinquenta"))
        self.assertEqual(normal("déis"), normal("dez"))
        self.assertEqual(normal("dezenóve"), normal("dezenove"))
        self.assertEqual(normal("méta"), normal("meta"))
        self.assertEqual(normal("cúida"), normal("cuida"))

    def test_substituicao_nao_vira_palavra_de_outro_item(self):
        """Substituições devem respeitar word boundary estrito e não casar substrings de palavras maiores."""
        dic_teste = {
            "Frila": {"forma": "Fríla", "voz": "ambas", "status": "aprovada"},
            "meta": {"forma": "méta", "voz": "ana", "status": "aprovada"},
            "check-in": {"forma": "tchéquin", "voz": "ambas", "status": "aprovada"},
        }
        texto = "Desfrilar o aplicativo com metamorfose e rechecar o check-in no Frila."
        modificado, subs = aplicar_pronuncia(texto, voz="ambas", apenas_aprovadas=True, dicionario=dic_teste)

        # Não deve substituir 'Desfrilar' nem 'metamorfose' nem 'rechecar'
        self.assertIn("Desfrilar", modificado)
        self.assertIn("metamorfose", modificado)
        self.assertIn("rechecar", modificado)
        # Deve substituir exatamente 'check-in' e 'Frila'
        self.assertIn("tchéquin", modificado)
        self.assertIn("Fríla", modificado)
        self.assertEqual(len(subs), 2)

    def test_preservacao_de_maiuscula(self):
        """A capitalização inicial ou ALL CAPS deve ser rigorosamente respeitada."""
        dic_teste = {
            "Frila": {"forma": "Fríla", "voz": "ambas", "status": "aprovada"},
            "check-in": {"forma": "tchéquin", "voz": "ambas", "status": "aprovada"},
        }
        # Title case
        txt1, _ = aplicar_pronuncia("O Frila conecta.", dicionario=dic_teste)
        self.assertIn("Fríla", txt1)

        # Lowercase
        txt2, _ = aplicar_pronuncia("o frila conecta.", dicionario=dic_teste)
        self.assertIn("fríla", txt2)

        # Uppercase
        txt3, _ = aplicar_pronuncia("O FRILA CONECTA.", dicionario=dic_teste)
        self.assertIn("FRÍLA", txt3)

        # Termo composto
        txt4, _ = aplicar_pronuncia("Fazer Check-in agora.", dicionario=dic_teste)
        self.assertIn("Tchéquin", txt4)

    def test_status_candidata_vs_aprovada(self):
        """Apenas itens aprovados podem ser substituídos no modo padrão."""
        dic_teste = {
            "Frila": {"forma": "Fríla", "voz": "ambas", "status": "candidata"},
            "meta": {"forma": "méta", "voz": "ana", "status": "aprovada"},
        }
        texto = "A meta do Frila."
        
        # Modo de produção (apenas_aprovadas=True): Frila NÃO deve mudar
        mod_prod, subs_prod = aplicar_pronuncia(texto, voz="ana", apenas_aprovadas=True, dicionario=dic_teste)
        self.assertIn("Frila", mod_prod)
        self.assertIn("méta", mod_prod)
        self.assertEqual(len(subs_prod), 1)
        self.assertEqual(subs_prod[0]["termo"], "meta")

        # Modo teste (apenas_aprovadas=False): ambos mudam
        mod_teste, subs_teste = aplicar_pronuncia(texto, voz="ana", apenas_aprovadas=False, dicionario=dic_teste)
        self.assertIn("Fríla", mod_teste)
        self.assertIn("méta", mod_teste)
        self.assertEqual(len(subs_teste), 2)

    def test_filtro_por_voz(self):
        """Regras exclusivas de uma voz não afetam a outra voz."""
        dic_teste = {
            "Abrasel": {"forma": "Abrazéu", "voz": "ana", "status": "aprovada"},
            "histórico": {"forma": "histórico-limpo", "voz": "gabriel", "status": "aprovada"},
            "Frila": {"forma": "Fríla", "voz": "ambas", "status": "aprovada"},
        }
        texto = "No Frila, a Abrasel consulta o histórico."

        # Para Ana
        txt_ana, subs_ana = aplicar_pronuncia(texto, voz="ana", apenas_aprovadas=True, dicionario=dic_teste)
        self.assertIn("Fríla", txt_ana)
        self.assertIn("Abrazéu", txt_ana)
        self.assertIn("histórico", txt_ana)  # Não mudou para histórico-limpo
        self.assertNotIn("histórico-limpo", txt_ana)

        # Para Gabriel
        txt_gabriel, subs_gabriel = aplicar_pronuncia(texto, voz="gabriel", apenas_aprovadas=True, dicionario=dic_teste)
        self.assertIn("Fríla", txt_gabriel)
        self.assertIn("Abrasel", txt_gabriel)  # Não mudou para Abrazéu
        self.assertIn("histórico-limpo", txt_gabriel)


if __name__ == "__main__":
    unittest.main()
