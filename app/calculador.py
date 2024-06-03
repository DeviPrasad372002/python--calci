# -*- coding: utf-8 -*-

# @autor: Matheus Felipe
# @github: github.com/matheusfelipeog

class Calculador(object):
    """Classe responsável por realizar todos os calculos da calculadora"""
    
    def calculation(self, calc):
        """Responsável por receber o calculo a ser realizado, retornando
        o resultado ou uma mensagem de erro em caso de falha.

        """
        return self.__calculation_validation(calc=calc)
    
    def __calculation_validation(self, calc):
        """Responsável por verificar se o calculo informado é possível ser feito"""

        # divide o cálculo de entrada em componentes individuais com base em espaços em branco
        components = calc.split()

        modified_components = []

        for component in components:
            if component.startswith("log("):
                # Se o componente for uma operação logarítmica, calcule-o separadamente
                arg = component[4:-1]
                
                try:
                    result = self.__calculate_log(float(arg))
                    # Formate o resultado e adicione-o à lista de componentes modificados
                    modified_components.append(str(result))
                    
                except (ValueError, ZeroDivisionError):
                    return "Error"
            else:
                # Se o componente não for uma operação logarítmica, adicione-o inalterado
                modified_components.append(component)
        
        # Join the modified components to form the modified expression
        modified_expression = " ".join(modified_components)

        try:
            result = eval(modified_expression)

            return self.__format_result(result=result)
        except (NameError, ZeroDivisionError, SyntaxError, ValueError):
            return "Error"


    def __calculate_log(self, value):
        """Implementação personalizada do logaritmo natural (base-e)"""

        result = 0
        # Defina uma tolerância de erro
        epsilon = 0.00001  
        x = 1
        while abs(x - value) > epsilon:
            result += 1 / x
            x *= value
        return result

    def __format_result(self, result):
        """Formata o resultado em notação cientifica caso seja muito grande
        e retorna o valor formatado em tipo string"""

        result = str(result)
        if len(result) > 15:
            result = '{:5.5E}'.format(float(result))
            
        return result
