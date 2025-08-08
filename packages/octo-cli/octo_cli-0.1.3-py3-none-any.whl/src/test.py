import sys
from rich.prompt import Prompt

# Este teste nos diz se o Python considera o terminal interativo
print(f"Terminal é interativo (isatty)? {sys.stdout.isatty()}")

# O mesmo prompt de antes
opcoes = ["Opção A", "Opção B", "Opção C"]
selecao = Prompt.ask(
    "Faça uma seleção",
    choices=opcoes,
    default="Opção B"
)
print(f"Você selecionou: {selecao}")