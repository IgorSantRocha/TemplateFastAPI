from fastapi import HTTPException, status
import re
import random


def valida_pwd(pwd):
    # Verifica o comprimento da senha
    if len(pwd) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve conter pelo menos 6 caracteres!"
        )

    # Verifica se contém pelo menos uma letra maiúscula
    if not re.search(r'[A-Z]', pwd):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve conter pelo menos uma letra maiúscula!"
        )

    # Verifica se contém pelo menos uma letra minúscula
    if not re.search(r'[a-z]', pwd):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve conter pelo menos uma letra minúscula!"
        )

    # Verifica se contém pelo menos um número
    if not re.search(r'[0-9]', pwd):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve conter pelo menos um número!"
        )

    # Verifica se contém pelo menos um caractere especial
    if not re.search(r'[!@#\$%\^&\*\(\)_\+\-=\[\]\{\};:\'",<>\./?]', pwd):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve conter pelo menos um caractere especial!"
        )

    return True


def valida_username(username: str):
    # Verifica o comprimento do nome de usuário
    if len(username) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome de usuário deve conter pelo menos 6 caracteres!"
        )

    # Verifica se contém apenas letras, números e underscore
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome de usuário deve conter apenas letras, números e underline! (Não use espaços)"
        )
    return True


def generate_token():
    return random.randint(100000, 999999)


def format_whatsapp_number(phone_number):
    # Remove espaços, traços e parênteses
    phone_number = phone_number.replace(" ", "").replace(
        "-", "").replace("(", "").replace(")", "")

    # Remove o símbolo de '+' no começo, se existir
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]

    # Se o número não começar com '55', adiciona o '55'
    if not phone_number.startswith("55"):
        phone_number = "55" + phone_number

    # Adiciona o sufixo '@s.whatsapp.net'
    formatted_number = phone_number + "@s.whatsapp.net"

    return formatted_number


def format_sms_number(phone_number):
    # Remove todos os caracteres não numéricos
    phone_number = re.sub(r'\D', '', phone_number)

    # Se o número começar com '55', remove o '55'
    if phone_number.startswith("55"):
        phone_number = phone_number[2:]

    return phone_number


def valida_cpf(cpf: str) -> bool:
    # Remover caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)

    # Verificar se o CPF tem 11 dígitos
    if len(cpf) != 11:
        return False

    # Verificar se todos os dígitos são iguais
    if cpf == cpf[0] * len(cpf):
        return False

    # Calcular o primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    primeiro_digito = (soma * 10) % 11
    if primeiro_digito == 10:
        primeiro_digito = 0

    # Calcular o segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    segundo_digito = (soma * 10) % 11
    if segundo_digito == 10:
        segundo_digito = 0

    if cpf[-2:] != f"{primeiro_digito}{segundo_digito}":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF inválido"
        )
    # Verificar se os dígitos verificadores estão corretos
    return True


def valida_email(email: str) -> bool:
    padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(padrao, email) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail inválido"
        )

    return True
