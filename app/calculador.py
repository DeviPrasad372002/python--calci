# -*- coding: utf-8 -*-

# @author: Matheus Felipe
# @github: github.com/matheusfelipeog

class Calculador(object):
    """Class responsible for performing all calculator computations"""
    
    def calculation(self, calc):
        """Responsible for receiving the calculation to be performed, returning
        the result or an error message in case of failure.

        """
        return self.__calculation_validation(calc=calc)

    def __calculation_validation(self, calc):
        """Responsible for verifying if the informed calculation is possible to be done"""

        try:
            result = eval(calc)

            return self.__format_result(result=result)
        except (NameError, ZeroDivisionError, SyntaxError, ValueError):
            return 'Error' 

    def __format_result(self, result):
        """Formats the result in scientific notation if it's too large
        and returns the formatted value as string type"""

        result = str(result)
        if len(result) > 15:
            result = '{:5.5E}'.format(float(result))
            
        return result