# Zarvyn TrustCheck

[English](README.md) | **Português**

[![Tests](https://github.com/zar4t/zarvyn-trustcheck/actions/workflows/test.yml/badge.svg)](https://github.com/zar4t/zarvyn-trustcheck/actions/workflows/test.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-experimental-orange)

Transforme as fronteiras de confiança pretendidas entre GitHub Actions e AWS em testes de regressão repetíveis.

Uma política de confiança OIDC mal configurada pode deixar qualquer branch, fork ou
pull request assumir um papel de produção. O TrustCheck permite registrar quais
identidades do GitHub **devem** e **não devem** conseguir assumir um papel, e quebra o
build quando a política deixa de corresponder a essa intenção.

- Offline: sem credenciais AWS, chamadas de rede, telemetria ou dependências em tempo de execução
- Determinístico: mesma política e mesmos cenários, mesmo resultado
- Pronto para CI: código de saída 0 (tudo passou), 1 (alguma expectativa falhou), 2 (entrada inválida ou UNKNOWN)

## Começo rápido

Requer Python 3.10 ou superior.

```sh
git clone https://github.com/zar4t/zarvyn-trustcheck.git
cd zarvyn-trustcheck
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install .
```

Rode os dois exemplos incluídos:

```sh
zarvyn-trustcheck --policy examples/restricted-policy.json --scenarios examples/scenarios.json
zarvyn-trustcheck --policy examples/broad-policy.json --scenarios examples/scenarios.json
```

A política restrita passa nos cinco cenários (saída 0). A política ampla falha em duas
expectativas negativas (saída 1): uma branch de feature e um subject de pull request
casam com o curinga dela. São avaliações sintéticas da política, não prova de que um
workflow real consegue emitir ou trocar esses tokens.

Gerar um relatório:

```sh
zarvyn-trustcheck --policy examples/restricted-policy.json --scenarios examples/scenarios.json --format markdown > report.md
```

Formatos: `text`, `json` e `markdown`. UNKNOWN tem prioridade sobre FAIL.

Sem instalar, a partir da raiz do repositório:

```sh
python3 -m trustcheck --policy examples/restricted-policy.json --scenarios examples/scenarios.json
python3 -m unittest discover -s tests -v
```

## Entradas e escopo suportado

As entradas são **JSON**. Copie `examples/scenarios.json` e informe o ARN exato do
provedor e as strings `sub`/`aud` hipotéticas completas. Cada caso tem um nome único e
um resultado esperado `ALLOW` ou `DENY`. Nunca informe tokens ou segredos reais.

Suportado: política versão 2012-10-17; Allow/Deny explícitos; a ação exata
`sts:AssumeRoleWithWebIdentity`; ARNs explícitos do provedor OIDC do GitHub na partição
comercial `aws`; `StringEquals`/`StringLike` apenas em `sub`/`aud` do GitHub. Entradas
e operadores de condição são combinados com E; valores dentro de uma entrada, com OU.
Um Deny explícito correspondente prevalece sobre Allow; sem Allow correspondente, o
resultado é Deny. `StringLike` diferencia maiúsculas e minúsculas e suporta `*` e `?`;
colchetes são literais.

Qualquer declaração não suportada torna o resultado UNKNOWN, inclusive Deny não
suportado. Variáveis, `NotAction`, `NotPrincipal`, outros operadores, provedores e
chaves de condição não são suportados. Chaves JSON duplicadas e suítes vazias são
rejeitadas. Condições ausentes são incondicionais neste modelo, o que não significa que
a AWS aceite essa política. Cada arquivo de entrada é limitado a 1 MiB.

Os exemplos usam o formato legado de subject. Informe subjects com ID imutável ou
personalizados de forma literal quando for o caso; a ferramenta não descobre nem gera
formatos de subject.

## Limites: leia antes de interpretar um PASS

O TrustCheck **não** é um simulador completo de IAM, um verificador de JWT nem uma
certificação de segurança. PASS significa apenas que o cenário informado corresponde à
decisão esperada neste modelo.

- Não valida assinatura, emissor, expiração ou emissão de token
- Não inspeciona workflows, regras de branch, aprovações de ambiente ou configurações do repositório
- Não avalia SCPs, permissões do papel, políticas de recurso, permission boundaries ou o acesso efetivo na AWS
- Ainda não foram feitos testes comparativos com a AWS real

A cobertura de cenários é finita. Valide em um ambiente isolado antes de confiar nos
resultados. O TrustCheck complementa o IAM Access Analyzer da AWS e scanners de
workflow como o zizmor.

## Uso em CI

O workflow incluído (`.github/workflows/test.yml`) roda os testes em Python 3.10 e 3.12
e aplica o contrato dos exemplos, sem segredos da AWS e sem permissão `id-token`. Aponte
a CLI para a sua política e os seus cenários versionados para barrar mudanças em
políticas de confiança. Não esconda códigos de saída diferentes de zero com
`continue-on-error` ou `|| true`.

## Próximos passos

- Comparação com a AWS real em um ambiente isolado
- Leitura de cenários a partir dos arquivos de workflow
- Importação opcional, somente leitura, de políticas de confiança existentes
- Comparação de política antes/depois em pull requests

O retorno de uso real é a contribuição mais valiosa. Abra uma issue com um exemplo
sintético e mínimo.

## Contribuição e segurança

Veja [CONTRIBUTING.md](CONTRIBUTING.md) e [SECURITY.md](SECURITY.md). Reporte
vulnerabilidades de forma privada pelo reporte privado de vulnerabilidades do GitHub.

## Referências

- [GitHub: OpenID Connect na AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [AWS: operadores de condição do IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition_operators.html)
- [AWS: IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)
- [zizmor](https://docs.zizmor.sh/audits/)

## Licença

Apache License 2.0. Veja [LICENSE](LICENSE). As identidades de exemplo são fictícias.

---

Feito por [Luan Thales](https://github.com/zar4t) · [LinkedIn](https://www.linkedin.com/in/luanthales)
