def cnpj(cnpj) -> bool:
    cnpj = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj) != 14:
        return False
    
    # Verificar se todos os dígitos são iguais (caso inválido)
    if cnpj == cnpj[0] * 14: return False
    
    def calcular_digito(cnpj, pesos):
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    # Pesos para cálculo
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1  # Adiciona o 6 no início

    # Calcular dígitos verificadores
    digito1 = calcular_digito(cnpj[:12], pesos1)
    digito2 = calcular_digito(cnpj[:12] + digito1, pesos2)

    return cnpj[-2:] == digito1 + digito2


def cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11: return False

    # Cálculo do primeiro dígito verificador
    soma1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma1 * 10 % 11) % 10

    # Cálculo do segundo dígito verificador
    soma2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma2 * 10 % 11) % 10

    return cpf[-2:] == f"{digito1}{digito2}"