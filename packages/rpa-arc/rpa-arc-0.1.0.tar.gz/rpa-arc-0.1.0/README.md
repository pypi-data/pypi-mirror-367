# rpa-arc

🚀 **rpa-arc** cria a estrutura base de um projeto RPA em Python num piscar de olhos.

> Sem firula, na lata: um comando e pronto—you’re ready to automate.

---

## 🔍 Por que usar rpa-arc?

- **Simplicidade visionária:** seu projeto nasce 100% organizadinho.
- **CLI intuitiva:** zig-zag, um `rpa-arc nome-do-projeto` e tudo se alinha.
- **Flexível:** gera na raiz ou em subpasta, você escolhe.

## 🛠️ Requisitos

- Python 3.8+
- requests
- python-dotenv
- selenium
- webdriver-manager

## ⚡ Instalação

```bash
pip install rpa-arc
```

## 🚀 Uso

```bash
# Cria ./meu-projeto/
rpa-arc meu-projeto

# Gera estrutura na raiz atual (se não passar nome)
rpa-arc
```

## 📂 Estrutura Gerada

```
meu-projeto/               # ou cwd/ se não passar nome
├── src/
│   └── rpa_arc/
│       ├── __init__.py
│       ├── cli.py
│       ├── estrutura.py
│       └── conteudos.py
├── tests/
│   └── test_estrutura.py
├── .gitignore
├── LICENSE
├── setup.py
└── README.md
```

## 🤝 Contribuição

Sério, sua ajuda importa. Abra uma issue ou mande um PR—qualquer sugestão é bem-vinda.

## 📜 Licença

MIT License. Veja o [LICENSE](LICENSE) para detalhes.